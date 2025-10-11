"""
Main FastAPI application for Google Calendar & Gmail MCP Server.
Refactored for modular architecture.
"""

import logging
import sys
import os
from fastapi import FastAPI, HTTPException, Depends
from typing import Optional
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import from mcp_server package
from mcp_server.utils.auth import get_credentials
from mcp_server import gmail_routes

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Unified MCP Server - Google & Microsoft",
    description="MCP server for interacting with Google (Calendar, Gmail) and Microsoft (Outlook, Teams) APIs.",
    version="0.3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] if you want to allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global State / Initialization ---
global_credentials: Optional[Credentials] = None

@app.on_event("startup")
def startup_event():
    """Attempt to get credentials on server startup."""
    global global_credentials
    logger.info("Server starting up. Attempting to authenticate with Google...")
    try:
        global_credentials = get_credentials()
        if not global_credentials or not global_credentials.valid:
            logger.error("Failed to obtain valid Google credentials on startup. Endpoints requiring auth will be unavailable.")
        else:
            logger.info("Successfully obtained Google credentials.")
    except Exception as e:
        logger.error(f"An error occurred during startup authentication: {e}. Endpoints requiring auth will be unavailable.", exc_info=True)
        global_credentials = None

# --- Dependency for Credentials ---

def get_current_credentials() -> Credentials:
    """Dependency to provide valid credentials to endpoints. Attempts refresh if invalid."""
    global global_credentials

    if not global_credentials:
        logger.warning("Credentials not available (failed during startup?). Attempting to re-fetch.")
        try:
            global_credentials = get_credentials()
            if not global_credentials:
                 raise HTTPException(
                    status_code=503, 
                    detail="Google API credentials are not available. Initial fetch failed."
                )
        except Exception as e:
            logger.error(f"Failed to re-fetch credentials: {e}", exc_info=True)
            raise HTTPException(
                status_code=503, 
                detail=f"Google API credentials unavailable. Failed to re-fetch: {e}"
            )
    
    # Check if valid, try refreshing if expired or invalid
    if not global_credentials.valid:
        logger.warning("Credentials are invalid or expired. Attempting refresh...")
        try:
            global_credentials.refresh(Request())
            if not global_credentials.valid:
                logger.error("Credential refresh succeeded but credentials still invalid.")
                raise HTTPException(
                    status_code=503, 
                    detail="Google API credentials invalid after refresh attempt."
                )
            logger.info("Credentials refreshed successfully within dependency.")
        except Exception as e:
            logger.error(f"Failed to refresh credentials within dependency: {e}", exc_info=True)
            logger.warning("Refresh failed. Attempting a full re-fetch of credentials...")
            try:
                global_credentials = get_credentials()
                if not global_credentials or not global_credentials.valid:
                    raise HTTPException(
                        status_code=503,
                        detail="Google API credentials unavailable after failed refresh and re-fetch."
                    )
                logger.info("Credentials re-fetched successfully after failed refresh.")
            except Exception as inner_e:
                logger.error(f"Failed to re-fetch credentials after failed refresh: {inner_e}", exc_info=True)
                raise HTTPException(
                    status_code=503, 
                    detail=f"Google API credentials unavailable. Refresh and re-fetch failed: {inner_e}"
                )

    return global_credentials

# --- Management Endpoints ---
@app.get("/health", tags=["Management"], operation_id="health_check")
def health_check():
    """Basic health check endpoint."""
    from mcp_server.utils.msgraph_auth import get_msgraph_token
    
    google_auth_status = "authenticated" if global_credentials and global_credentials.valid else "authentication_failed_or_pending"
    
    # Check MS Graph authentication
    msgraph_token = get_msgraph_token()
    msgraph_auth_status = "authenticated" if msgraph_token else "authentication_failed_or_pending"
    
    return {
        "status": "ok",
        "google_authentication": google_auth_status,
        "msgraph_authentication": msgraph_auth_status
    }

# --- Register Gmail Routes ---
gmail_routes.register_endpoints(get_current_credentials)
app.include_router(gmail_routes.router)

# --- Register Calendar Routes ---
from mcp_server import calendar_routes
calendar_routes.register_endpoints(get_current_credentials)
app.include_router(calendar_routes.router)

# --- Register Authentication Routes ---
from mcp_server import google_auth_routes, msgraph_auth_routes
app.include_router(google_auth_routes.router)
app.include_router(msgraph_auth_routes.router)

# --- Register Microsoft Graph Routes (Outlook & Teams) ---
from mcp_server import outlook_routes, teams_routes
app.include_router(outlook_routes.router)
app.include_router(teams_routes.router)

logger.info("FastAPI app initialized successfully with all Google (Gmail, Calendar) and Microsoft (Outlook, Teams) routes.")

