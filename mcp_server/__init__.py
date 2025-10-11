"""MCP Server for Google Calendar, Gmail, Outlook, and Teams integration."""

# Export route modules for easy importing
from mcp_server import gmail_routes
from mcp_server import calendar_routes
from mcp_server import outlook_routes
from mcp_server import teams_routes
from mcp_server import google_auth_routes
from mcp_server import msgraph_auth_routes

__all__ = [
    'gmail_routes',
    'calendar_routes',
    'outlook_routes',
    'teams_routes',
    'google_auth_routes',
    'msgraph_auth_routes',
]
