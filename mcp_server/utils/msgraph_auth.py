"""
Microsoft Graph Authentication for MCP Server
Handles OAuth flow for Microsoft 365 services (Outlook, Teams, Calendar).
"""

import os
import json
import logging
import webbrowser
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from msal import PublicClientApplication, ConfidentialClientApplication, SerializableTokenCache
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# --- Configuration ---
# Support multiple environment variable naming schemes
# Priority: MSFT_* > OUT_* > TM_* > generic
MSFT_CLIENT_ID = (
    os.getenv('MSFT_CLIENT_ID') or 
    os.getenv('OUT_CLIENT_ID') or 
    os.getenv('TM_CLIENT_ID') or 
    os.getenv('CLIENT_ID')
)
MSFT_CLIENT_SECRET = (
    os.getenv('MSFT_CLIENT_SECRET') or 
    os.getenv('OUT_CLIENT_SECRET') or 
    os.getenv('TM_CLIENT_SECRET') or 
    os.getenv('CLIENT_SECRET')
)
MSFT_TENANT_ID = (
    os.getenv('MSFT_TENANT_ID') or 
    os.getenv('OUT_TENANT_ID') or 
    os.getenv('TM_TENANT_ID') or 
    os.getenv('TENANT_ID') or 
    'common'
)
TOKEN_CACHE_FILE = os.getenv('MSGRAPH_TOKEN_FILE', '.msgraph-tokens.json')
# Read PORT from env (for compatibility with existing Flask setup)
# Priority: REDIRECT_URI (extract port) > PORT > MSGRAPH_CALLBACK_PORT > 8081
REDIRECT_URI_ENV = os.getenv('REDIRECT_URI')
if REDIRECT_URI_ENV:
    # If REDIRECT_URI is set, use it and extract the port from it
    REDIRECT_URI = REDIRECT_URI_ENV
    # Extract port from URI like http://localhost:5000/path
    import re
    port_match = re.search(r':(\d+)/', REDIRECT_URI)
    REDIRECT_PORT = int(port_match.group(1)) if port_match else int(os.getenv('PORT', 8081))
else:
    # No REDIRECT_URI set, build it from PORT
    REDIRECT_PORT = int(os.getenv('PORT', os.getenv('MSGRAPH_CALLBACK_PORT', 8081)))
    REDIRECT_URI = f'http://localhost:{REDIRECT_PORT}'

# Microsoft Graph scopes
# Note: Some permissions require admin consent in organizational accounts
# If you get "Need admin approval" error, comment out the permissions below marked with "Requires Admin"

MSGRAPH_SCOPES = [
    "https://graph.microsoft.com/Mail.ReadWrite",           # Outlook email access
    "https://graph.microsoft.com/Mail.Send",                # Send emails
    "https://graph.microsoft.com/Calendars.ReadWrite",      # Calendar access
    # "https://graph.microsoft.com/ChannelMessage.Read.All",  # Teams channels - Requires Admin
    # "https://graph.microsoft.com/Chat.Read",                 # Teams chats - Requires Admin
    "https://graph.microsoft.com/User.Read",                # Basic user info
]

# With the above configuration:
# ✅ Outlook email will work
# ✅ Calendar will work  
# ❌ Teams will require admin consent (commented out)
#
# To enable Teams: Ask your IT admin to grant consent, or use a personal Microsoft account

# --- Token Cache Management ---

class TokenCache:
    """Manages token cache persistence"""
    
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.cache = SerializableTokenCache()
        
        # Load existing cache if available
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.cache.deserialize(f.read())
                logger.info(f"Loaded token cache from {cache_file}")
            except Exception as e:
                logger.warning(f"Failed to load token cache: {e}")
    
    def save(self):
        """Save cache to file"""
        if self.cache.has_state_changed:
            try:
                with open(self.cache_file, 'w') as f:
                    f.write(self.cache.serialize())
                logger.info(f"Token cache saved to {self.cache_file}")
            except Exception as e:
                logger.error(f"Failed to save token cache: {e}")
    
    def get_cache(self) -> SerializableTokenCache:
        """Get the MSAL cache object"""
        return self.cache


# Global token cache
_token_cache = TokenCache(TOKEN_CACHE_FILE)

# --- OAuth Callback Handler ---

class MSALCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handles the OAuth callback request to capture the authorization code."""
    
    auth_response = None
    error = None
    shutdown_event = None
    
    def do_GET(self):
        """Handle GET requests (the OAuth callback)."""
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get('code')
        error = query_components.get('error')
        state = query_components.get('state')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if code:
            # Capture full auth response including state
            MSALCallbackHandler.auth_response = {
                'code': code[0],
                'state': state[0] if state else None
            }
            logger.info("Authorization code received from Microsoft")
            self.wfile.write(b'<html><body><h1>Authentication Successful!</h1>')
            self.wfile.write(b'<p>You can close this window and return to the application.</p></body></html>')
        elif error:
            MSALCallbackHandler.error = error[0]
            error_desc = query_components.get('error_description', ['Unknown error'])[0]
            logger.error(f"OAuth Error: {MSALCallbackHandler.error} - {error_desc}")
            self.wfile.write(b'<html><body><h1>Authentication Failed</h1>')
            self.wfile.write(f'<p>Error: {error_desc}</p></body></html>'.encode())
        else:
            logger.warning("Received callback without code or error")
            self.wfile.write(b'<html><body><h1>Invalid Callback</h1>')
            self.wfile.write(b'<p>Received an unexpected request.</p></body></html>')
        
        # Signal shutdown
        if MSALCallbackHandler.shutdown_event:
            MSALCallbackHandler.shutdown_event.set()
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass


def _start_local_server(port: int, shutdown_event: threading.Event):
    """Start a local HTTP server to handle OAuth callback"""
    try:
        with socketserver.TCPServer(("", port), MSALCallbackHandler) as httpd:
            logger.info(f"Starting OAuth callback server on port {port}")
            while not shutdown_event.is_set():
                httpd.handle_request()
            logger.info("OAuth callback server stopped")
    except OSError as e:
        logger.error(f"Failed to start callback server on port {port}: {e}")
        shutdown_event.set()


# --- Main Authentication Functions ---

def get_msgraph_token() -> Optional[str]:
    """
    Get a valid access token for Microsoft Graph API.
    Handles silent authentication, token refresh, and interactive flow.
    
    Returns:
        Access token string or None if authentication fails
    """
    logger.info("[MSGRAPH_AUTH] Attempting to get MS Graph access token")
    
    if not MSFT_CLIENT_ID:
        logger.error("[MSGRAPH_AUTH] MSFT_CLIENT_ID not configured in environment variables")
        logger.error("[MSGRAPH_AUTH] Please set CLIENT_ID in your .env file")
        logger.error(f"[MSGRAPH_AUTH] Current CLIENT_ID value: {repr(MSFT_CLIENT_ID)}")
        return None
    
    logger.info(f"[MSGRAPH_AUTH] CLIENT_ID configured: {MSFT_CLIENT_ID[:8]}...{MSFT_CLIENT_ID[-4:]}")
    logger.info(f"[MSGRAPH_AUTH] TENANT_ID: {MSFT_TENANT_ID}")
    logger.info(f"[MSGRAPH_AUTH] Token cache file: {TOKEN_CACHE_FILE}")
    
    # Create MSAL application (confidential or public based on whether secret is provided)
    if MSFT_CLIENT_SECRET:
        logger.info("[MSGRAPH_AUTH] Using Confidential Client flow (with CLIENT_SECRET)")
        app = ConfidentialClientApplication(
            client_id=MSFT_CLIENT_ID,
            client_credential=MSFT_CLIENT_SECRET,
            authority=f"https://login.microsoftonline.com/{MSFT_TENANT_ID}",
            token_cache=_token_cache.get_cache()
        )
    else:
        logger.info("[MSGRAPH_AUTH] Using Public Client flow (no CLIENT_SECRET)")
        app = PublicClientApplication(
            client_id=MSFT_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{MSFT_TENANT_ID}",
            token_cache=_token_cache.get_cache()
        )
    
    # Try to get token silently from cache
    logger.info("[MSGRAPH_AUTH] Checking for cached accounts")
    accounts = app.get_accounts()
    
    if accounts:
        logger.info(f"[MSGRAPH_AUTH] Found {len(accounts)} cached account(s)")
        logger.debug(f"[MSGRAPH_AUTH] Account details: {accounts[0].get('username', 'unknown')}")
        
        logger.info("[MSGRAPH_AUTH] Attempting silent token acquisition from cache")
        result = app.acquire_token_silent(MSGRAPH_SCOPES, account=accounts[0])
        
        if result and 'access_token' in result:
            logger.info("[MSGRAPH_AUTH] ✓ Token acquired silently from cache")
            logger.info(f"[MSGRAPH_AUTH] Token length: {len(result['access_token'])} characters")
            _token_cache.save()
            return result['access_token']
        else:
            logger.warning("[MSGRAPH_AUTH] Silent token acquisition failed")
            if result:
                logger.warning(f"[MSGRAPH_AUTH] Error: {result.get('error', 'unknown')}")
                logger.warning(f"[MSGRAPH_AUTH] Error description: {result.get('error_description', 'unknown')}")
            logger.info("[MSGRAPH_AUTH] Will try interactive OAuth flow")
    else:
        logger.info("[MSGRAPH_AUTH] No cached accounts found")
    
    # Need interactive authentication
    logger.info("[MSGRAPH_AUTH] Starting interactive OAuth flow for Microsoft Graph")
    logger.info(f"[MSGRAPH_AUTH] Redirect URI: {REDIRECT_URI}")
    logger.info(f"[MSGRAPH_AUTH] Redirect port: {REDIRECT_PORT}")
    logger.info(f"[MSGRAPH_AUTH] Requested scopes: {', '.join(MSGRAPH_SCOPES)}")
    
    # Reset callback handler state
    MSALCallbackHandler.auth_response = None
    MSALCallbackHandler.error = None
    shutdown_event = threading.Event()
    MSALCallbackHandler.shutdown_event = shutdown_event
    
    # Start local server in background thread
    logger.info(f"[MSGRAPH_AUTH] Starting local callback server on port {REDIRECT_PORT}")
    server_thread = threading.Thread(
        target=_start_local_server,
        args=(REDIRECT_PORT, shutdown_event),
        daemon=True
    )
    server_thread.start()
    
    # Initiate device flow with local redirect
    logger.info("[MSGRAPH_AUTH] Initiating auth code flow")
    flow = app.initiate_auth_code_flow(
        scopes=MSGRAPH_SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    if "error" in flow:
        logger.error(f"[MSGRAPH_AUTH] Failed to initiate auth flow: {flow.get('error_description')}")
        shutdown_event.set()
        return None
    
    # Open browser for user to authenticate
    auth_url = flow["auth_uri"]
    logger.info(f"Opening browser for authentication: {auth_url}")
    webbrowser.open(auth_url)
    
    # Wait for callback (with timeout)
    logger.info("Waiting for OAuth callback...")
    shutdown_event.wait(timeout=300)  # 5 minute timeout
    
    if MSALCallbackHandler.error:
        logger.error(f"Authentication error: {MSALCallbackHandler.error}")
        return None
    
    if not MSALCallbackHandler.auth_response:
        logger.error("No authorization response received")
        return None
    
    # Exchange code for token
    try:
        logger.info(f"[MSGRAPH_AUTH] Exchanging auth code for token (state: {MSALCallbackHandler.auth_response.get('state')})")
        result = app.acquire_token_by_auth_code_flow(
            auth_code_flow=flow,
            auth_response=MSALCallbackHandler.auth_response
        )
        
        if "access_token" in result:
            logger.info("Successfully obtained access token")
            _token_cache.save()
            return result['access_token']
        else:
            error = result.get('error', 'Unknown error')
            error_desc = result.get('error_description', '')
            logger.error(f"Failed to acquire token: {error} - {error_desc}")
            return None
            
    except Exception as e:
        logger.error(f"Exception during token acquisition: {e}", exc_info=True)
        return None


def get_msgraph_headers() -> Dict[str, str]:
    """
    Get HTTP headers with authentication for Microsoft Graph requests.
    
    Returns:
        Dictionary with Authorization header
    """
    logger.info("[MSGRAPH_AUTH] get_msgraph_headers() called")
    
    token = get_msgraph_token()
    
    if not token:
        logger.error("[MSGRAPH_AUTH] Failed to get Microsoft Graph access token")
        logger.error("[MSGRAPH_AUTH] Returning empty headers - API calls will fail")
        return {}
    
    logger.info("[MSGRAPH_AUTH] ✓ Successfully got access token")
    logger.debug(f"[MSGRAPH_AUTH] Token starts with: {token[:20]}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    logger.info("[MSGRAPH_AUTH] ✓ Headers created successfully")
    return headers


def clear_token_cache():
    """Clear the token cache (for logout/re-authentication)"""
    try:
        if os.path.exists(TOKEN_CACHE_FILE):
            os.remove(TOKEN_CACHE_FILE)
            logger.info("Token cache cleared")
    except Exception as e:
        logger.error(f"Failed to clear token cache: {e}")


# Example usage
if __name__ == '__main__':
    print("Testing Microsoft Graph authentication...")
    token = get_msgraph_token()
    if token:
        print("✓ Successfully obtained access token")
        print(f"Token length: {len(token)} characters")
    else:
        print("✗ Failed to obtain access token")

