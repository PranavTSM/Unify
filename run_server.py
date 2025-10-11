"""
Main entry point for the Unified Inbox MCP Server.
Starts the MCP server with FastAPI backend.
"""

import uvicorn
import os
import sys
import logging
import logging.config
import threading
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware

# --- Centralized Logging Configuration ---
project_dir_for_log = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(project_dir_for_log, 'mcp_server.log')


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
        'file': {
            'formatter': 'default',
            'class': 'logging.FileHandler',
            'filename': log_file_path,
            'mode': 'a',
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
        },
        'uvicorn.error': {
            'level': 'INFO',
            'handlers': ['default', 'file'],
            'propagate': False,
        },
        'uvicorn.access': {
            'level': 'WARNING',
            'handlers': ['default', 'file'],
            'propagate': False,
        },
    }
}

# Force reset existing handlers
root_logger_for_reset = logging.getLogger()
if root_logger_for_reset.hasHandlers():
    for handler in root_logger_for_reset.handlers[:]:
        root_logger_for_reset.removeHandler(handler)
        handler.close()
    print("Log Reset: Removed existing handlers.")

# Apply the configuration
logging.config.dictConfig(LOGGING_CONFIG)

# Get the root logger AFTER configuration
logger = logging.getLogger(__name__)
logger.info(f"Logging configured. Log file path: {log_file_path}")

# Function to run the MCP server in a separate thread
def run_mcp_server():
    """Run MCP server in a separate thread for stdio communication."""
    # Remove console handler for MCP thread to keep stdio clean
    root_logger = logging.getLogger()
    handler_to_remove = None
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler_to_remove = handler
            break

    if handler_to_remove:
        logger.info(f"MCP Mode: Removing console handler {handler_to_remove}")
        root_logger.removeHandler(handler_to_remove)
    else:
        logger.warning("MCP Mode: Console handler (StreamHandler) not found to remove.")
    
    # Import and run MCP server
    try:
        from mcp_server.utils.mcp_bridge import create_mcp_server
        mcp = create_mcp_server()
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"MCP server thread failed: {e}", exc_info=True)

if __name__ == "__main__":
    # Add the project directory to the Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)
    
    # Force PYTHONPATH for reloader
    os.environ["PYTHONPATH"] = f"{project_dir}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
    logger.info(f"Set PYTHONPATH to include {project_dir}")
    
    # Load environment variables
    load_dotenv()

    # Start MCP server thread if stdin is not a TTY (i.e., piped input from MCP client)
    if not os.isatty(0):
        logger.info("MCP client detected via stdin: Starting MCP server thread")
        mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
        mcp_thread.start()
        logger.info("MCP server thread launched")
    else:
        logger.info("Running in HTTP-only mode (stdin is a TTY)")
        # Ensure console handler is present if we started in HTTP mode
        root_logger = logging.getLogger()
        has_console = any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers)
        if not has_console:
            logger.warning("Console handler missing in HTTP mode, adding default.")
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(logging.Formatter(LOGGING_CONFIG['formatters']['default']['format']))
            root_logger.addHandler(console_handler)

    # FastAPI/Uvicorn settings
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    logger.info(f"Starting MCP FastAPI server on {host}:{port}...")
    logger.info(f"Reload mode: {'Enabled' if reload else 'Disabled'}")

    # Run Uvicorn with logging config
    try:
        uvicorn.run(
            "mcp_server.app:app",
            host=host,
            port=port,
            reload=reload,
            log_config=LOGGING_CONFIG
        )
    except Exception as e:
        logger.error(f"Error starting FastAPI server: {e}", exc_info=True)
        sys.exit(1)
