"""
Google Authentication Routes
Provides explicit authentication endpoints for Google OAuth flow.
"""

import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mcp_server.utils.auth import get_credentials, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, TOKEN_FILE

logger = logging.getLogger(__name__)

# Create router for Google auth endpoints
router = APIRouter(prefix="/auth/google", tags=["Google Authentication"])


class AuthStatusResponse(BaseModel):
    """Response model for authentication status"""
    authenticated: bool
    client_id_configured: bool
    client_secret_configured: bool
    message: str


class AuthResponse(BaseModel):
    """Response model for authentication actions"""
    success: bool
    message: str
    authenticated: bool


# --- Authentication Endpoints ---

@router.get(
    "/status",
    response_model=AuthStatusResponse,
    summary="Check Google Authentication Status",
    operation_id="google_auth_status"
)
def google_auth_status_endpoint():
    """
    Check if Google (Gmail/Calendar) is authenticated and configured.
    Returns current authentication status without triggering OAuth.
    """
    # Check if credentials are configured
    client_id_configured = bool(GOOGLE_CLIENT_ID)
    client_secret_configured = bool(GOOGLE_CLIENT_SECRET)
    
    # Check if we have a valid token
    has_token_cache = os.path.exists(TOKEN_FILE)
    
    authenticated = False
    message = "Not authenticated"
    
    if not client_id_configured or not client_secret_configured:
        message = "Google credentials not configured in .env file. Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
    elif has_token_cache:
        try:
            creds = get_credentials()
            if creds and creds.valid:
                authenticated = True
                message = "Authenticated successfully"
            else:
                message = "Token expired or invalid. Please re-authenticate using /auth/google/login"
        except Exception as e:
            logger.error(f"Error checking credentials: {e}")
            message = f"Authentication error: {str(e)}"
    else:
        message = "No token cache found. Please authenticate using /auth/google/login"
    
    return AuthStatusResponse(
        authenticated=authenticated,
        client_id_configured=client_id_configured,
        client_secret_configured=client_secret_configured,
        message=message
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate with Google",
    operation_id="google_login"
)
def google_login_endpoint():
    """
    Trigger Google OAuth flow.
    This will open a browser window for you to sign in with your Google account.
    After successful authentication, the token is cached for future use.
    """
    logger.info("Google authentication requested")
    
    # Check if credentials are configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=400,
            detail="Google credentials not configured. Please add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to your .env file."
        )
    
    try:
        # This will trigger the OAuth flow
        creds = get_credentials()
        
        if creds and creds.valid:
            logger.info("Google authentication successful")
            return AuthResponse(
                success=True,
                message="Successfully authenticated with Google. Token cached for future use.",
                authenticated=True
            )
        else:
            logger.error("Google authentication failed - no valid credentials")
            return AuthResponse(
                success=False,
                message="Authentication failed. Check server logs for details.",
                authenticated=False
            )
    
    except Exception as e:
        logger.error(f"Google authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=AuthResponse,
    summary="Clear Google Authentication",
    operation_id="google_logout"
)
def google_logout_endpoint():
    """
    Clear Google authentication token cache.
    You will need to re-authenticate before using Google APIs again.
    """
    logger.info("Google logout requested - clearing token cache")
    
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            logger.info(f"Token file {TOKEN_FILE} removed")
        
        return AuthResponse(
            success=True,
            message="Token cache cleared. You will need to re-authenticate before using Google APIs.",
            authenticated=False
        )
    except Exception as e:
        logger.error(f"Error clearing token cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing token cache: {str(e)}"
        )


@router.get(
    "/config",
    summary="Show Google Configuration",
    operation_id="google_config"
)
def google_config_endpoint():
    """
    Show current Google configuration from environment.
    Useful for debugging setup issues.
    """
    has_token = os.path.exists(TOKEN_FILE)
    
    config = {
        "client_id_configured": bool(GOOGLE_CLIENT_ID),
        "client_secret_configured": bool(GOOGLE_CLIENT_SECRET),
        "token_cache_file": TOKEN_FILE,
        "token_cache_exists": has_token,
        "callback_port": os.getenv('OAUTH_CALLBACK_PORT', '8080'),
    }
    
    # Check if credentials look valid
    if GOOGLE_CLIENT_ID:
        if GOOGLE_CLIENT_ID.startswith('YOUR_'):
            config["client_id_warning"] = "GOOGLE_CLIENT_ID looks like a placeholder."
        elif not GOOGLE_CLIENT_ID.endswith('.apps.googleusercontent.com'):
            config["client_id_warning"] = "GOOGLE_CLIENT_ID format looks unusual (should end with .apps.googleusercontent.com)"
    else:
        config["client_id_warning"] = "GOOGLE_CLIENT_ID not set in environment"
    
    if not GOOGLE_CLIENT_SECRET:
        config["client_secret_warning"] = "GOOGLE_CLIENT_SECRET not set in environment"
    
    return config


@router.get(
    "/help",
    summary="Get Help for Google Setup",
    operation_id="google_help"
)
def google_help_endpoint():
    """
    Get help and instructions for setting up Google authentication.
    """
    return {
        "title": "Google OAuth Setup Guide",
        "quick_start": [
            "1. Go to Google Cloud Console (https://console.cloud.google.com/)",
            "2. Create a new project or select existing",
            "3. Enable Gmail API and Calendar API",
            "4. Go to: APIs & Services → Credentials",
            "5. Create OAuth 2.0 Client ID (Desktop app type)",
            "6. Set redirect URI: http://localhost:8080",
            "7. Download credentials JSON or copy Client ID and Client Secret",
            "8. Add to .env: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET",
            "9. Restart server and call POST /auth/google/login"
        ],
        "env_variables": {
            "required": [
                "GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com",
                "GOOGLE_CLIENT_SECRET=your-client-secret"
            ],
            "optional": [
                "TOKEN_FILE_PATH=.gcp-saved-tokens.json",
                "OAUTH_CALLBACK_PORT=8080",
                "GOOGLE_SCOPES=comma-separated-scopes"
            ]
        },
        "endpoints": {
            "GET /auth/google/status": "Check authentication status",
            "POST /auth/google/login": "Trigger OAuth flow to authenticate",
            "POST /auth/google/logout": "Clear token cache",
            "GET /auth/google/config": "View current configuration",
            "GET /auth/google/help": "This help message"
        },
        "required_apis": [
            "Gmail API",
            "Google Calendar API"
        ],
        "documentation": "See GETTING_STARTED.md for detailed instructions"
    }

