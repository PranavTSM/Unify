"""
Microsoft Graph Authentication Routes
Provides explicit authentication endpoints for MS Graph OAuth flow.
"""

import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from mcp_server.utils.msgraph_auth import get_msgraph_token, clear_token_cache, MSFT_CLIENT_ID, MSFT_TENANT_ID, REDIRECT_PORT, REDIRECT_URI

logger = logging.getLogger(__name__)

# Create router for MS Graph auth endpoints
router = APIRouter(prefix="/auth/msgraph", tags=["Microsoft Graph Authentication"])


class AuthStatusResponse(BaseModel):
    """Response model for authentication status"""
    authenticated: bool
    client_id_configured: bool
    tenant_id: str
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
    summary="Check MS Graph Authentication Status",
    operation_id="msgraph_auth_status"
)
def msgraph_auth_status_endpoint():
    """
    Check if Microsoft Graph is authenticated and configured.
    Returns current authentication status without triggering OAuth.
    """
    # Check if CLIENT_ID is configured
    client_id_configured = bool(MSFT_CLIENT_ID)
    
    # Check if we have a valid token (without triggering new auth)
    token_file = os.getenv('MSGRAPH_TOKEN_FILE', '.msgraph-tokens.json')
    has_token_cache = os.path.exists(token_file)
    
    # Try to get token (this will use cache if available, but won't trigger OAuth)
    authenticated = False
    message = "Not authenticated"
    
    if not client_id_configured:
        message = "CLIENT_ID not configured in .env file. Please add your Azure app CLIENT_ID."
    elif has_token_cache:
        try:
            token = get_msgraph_token()
            if token:
                authenticated = True
                message = "Authenticated successfully"
            else:
                message = "Token expired or invalid. Please re-authenticate using /auth/msgraph/login"
        except Exception as e:
            logger.error(f"Error checking token: {e}")
            message = f"Authentication error: {str(e)}"
    else:
        message = "No token cache found. Please authenticate using /auth/msgraph/login"
    
    return AuthStatusResponse(
        authenticated=authenticated,
        client_id_configured=client_id_configured,
        tenant_id=MSFT_TENANT_ID or "not configured",
        message=message
    )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate with Microsoft Graph",
    operation_id="msgraph_login"
)
def msgraph_login_endpoint():
    """
    Trigger Microsoft Graph OAuth flow.
    This will open a browser window for you to sign in with your Microsoft account.
    After successful authentication, the token is cached for future use.
    """
    logger.info("MS Graph authentication requested")
    
    # Check if CLIENT_ID is configured
    if not MSFT_CLIENT_ID:
        raise HTTPException(
            status_code=400,
            detail="CLIENT_ID not configured. Please add CLIENT_ID to your .env file with your Azure app client ID."
        )
    
    try:
        # This will trigger the OAuth flow
        token = get_msgraph_token()
        
        if token:
            logger.info("MS Graph authentication successful")
            return AuthResponse(
                success=True,
                message="Successfully authenticated with Microsoft Graph. Token cached for future use.",
                authenticated=True
            )
        else:
            logger.error("MS Graph authentication failed - no token returned")
            return AuthResponse(
                success=False,
                message="Authentication failed. Check server logs for details.",
                authenticated=False
            )
    
    except Exception as e:
        logger.error(f"MS Graph authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Authentication error: {str(e)}"
        )


@router.post(
    "/logout",
    response_model=AuthResponse,
    summary="Clear MS Graph Authentication",
    operation_id="msgraph_logout"
)
def msgraph_logout_endpoint():
    """
    Clear Microsoft Graph authentication token cache.
    You will need to re-authenticate before using MS Graph APIs again.
    """
    logger.info("MS Graph logout requested - clearing token cache")
    
    try:
        clear_token_cache()
        return AuthResponse(
            success=True,
            message="Token cache cleared. You will need to re-authenticate before using MS Graph APIs.",
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
    summary="Show MS Graph Configuration",
    operation_id="msgraph_config"
)
def msgraph_config_endpoint():
    """
    Show current Microsoft Graph configuration from environment.
    Useful for debugging setup issues.
    """
    token_file = os.getenv('MSGRAPH_TOKEN_FILE', '.msgraph-tokens.json')
    has_token = os.path.exists(token_file)
    
    config = {
        "client_id_configured": bool(MSFT_CLIENT_ID),
        "client_id_length": len(MSFT_CLIENT_ID) if MSFT_CLIENT_ID else 0,
        "tenant_id": MSFT_TENANT_ID or "not configured",
        "token_cache_file": token_file,
        "token_cache_exists": has_token,
        "redirect_uri": REDIRECT_URI,
        "callback_port": str(REDIRECT_PORT),
    }
    
    # Check if CLIENT_ID looks valid (should be a GUID)
    if MSFT_CLIENT_ID:
        if MSFT_CLIENT_ID.startswith('YOUR_'):
            config["client_id_warning"] = "CLIENT_ID looks like a placeholder. Please replace with your actual Azure app ID."
        elif len(MSFT_CLIENT_ID) < 30:
            config["client_id_warning"] = "CLIENT_ID seems too short. Should be a GUID (36 characters)."
    else:
        config["client_id_warning"] = "CLIENT_ID not set in environment"
    
    return config


@router.get(
    "/help",
    summary="Get Help for MS Graph Setup",
    operation_id="msgraph_help"
)
def msgraph_help_endpoint():
    """
    Get help and instructions for setting up Microsoft Graph authentication.
    """
    return {
        "title": "Microsoft Graph Setup Guide",
        "quick_start": [
            "1. Register app in Azure Portal (https://portal.azure.com/)",
            "2. Go to: Azure Active Directory → App registrations → New registration",
            "3. Set redirect URI: http://localhost:8081 (Public client/native)",
            "4. Add API permissions: Mail.ReadWrite, Mail.Send, Calendars.ReadWrite, etc.",
            "5. Enable 'Allow public client flows' in Authentication",
            "6. Copy Application (client) ID",
            "7. Add to .env: CLIENT_ID=your-app-id-here",
            "8. Restart server and call POST /auth/msgraph/login"
        ],
        "env_variables": {
            "required": [
                "CLIENT_ID=your-azure-app-client-id"
            ],
            "optional": [
                "TENANT_ID=common (default: common for multi-tenant)",
                "MSGRAPH_TOKEN_FILE=.msgraph-tokens.json",
                "MSGRAPH_CALLBACK_PORT=8081"
            ]
        },
        "endpoints": {
            "GET /auth/msgraph/status": "Check authentication status",
            "POST /auth/msgraph/login": "Trigger OAuth flow to authenticate",
            "POST /auth/msgraph/logout": "Clear token cache",
            "GET /auth/msgraph/config": "View current configuration",
            "GET /auth/msgraph/help": "This help message"
        },
        "azure_app_requirements": {
            "redirect_uri": "http://localhost:8081 (Public client/native)",
            "api_permissions": [
                "Mail.ReadWrite",
                "Mail.Send",
                "Calendars.ReadWrite",
                "ChannelMessage.Read.All",
                "Chat.Read",
                "User.Read"
            ],
            "public_client_flow": "Must be enabled (Authentication → Advanced settings)"
        },
        "documentation": "See MSGRAPH_SETUP.md for detailed instructions"
    }

