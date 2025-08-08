import subprocess
import logging
import json
import re
import os
from typing import Dict, Any, Optional

logger = logging.getLogger("ga4-mcp-chat")

# Maximum timeout for MCP queries in seconds
MCP_TIMEOUT = int(os.environ.get("MCP_TIMEOUT", "30"))

def format_response(text: str) -> str:
    """Format the MCP response for better readability"""
    # Try to detect if the response is JSON and format it nicely
    try:
        data = json.loads(text)
        return json.dumps(data, indent=2)
    except json.JSONDecodeError:
        # Not JSON, return as is
        return text

def extract_error_message(stderr: str) -> str:
    """Extract a user-friendly error message from MCP stderr output"""
    # Look for common error patterns
    auth_error = re.search(r"(Authentication|Authorization).*error", stderr, re.IGNORECASE)
    if auth_error:
        return "Google Analytics authentication error. Please check your credentials and permissions."
    
    property_error = re.search(r"property.*not found", stderr, re.IGNORECASE)
    if property_error:
        return "The requested Google Analytics property was not found or you don't have access to it."
    
    # Default error message
    return "An error occurred while processing your query. Please try again or rephrase your question."

def query_ga(prompt: str) -> str:
    """Query the Google Analytics MCP server with natural language"""
    if not prompt.strip():
        return "Please provide a query about your Google Analytics data."
    
    logger.info(f"Sending query to MCP: {prompt[:50]}...")
    
    try:
        # Run the MCP command with timeout
        result = subprocess.run(
            ["google-analytics-mcp", "--query", prompt],
            capture_output=True,
            text=True,
            timeout=MCP_TIMEOUT
        )
        
        # Check for errors
        if result.returncode != 0:
            logger.error(f"MCP command failed with code {result.returncode}: {result.stderr}")
            return extract_error_message(result.stderr)
        
        # Process successful output
        output = result.stdout.strip()
        if not output:
            return "No data found for your query. Please try a different question or time period."
        
        # Format the response
        formatted_output = format_response(output)
        logger.info(f"Successfully processed query, response length: {len(formatted_output)}")
        return formatted_output
        
    except subprocess.TimeoutExpired:
        logger.error(f"MCP query timed out after {MCP_TIMEOUT} seconds")
        return f"The query took too long to process. Please try a simpler query or a shorter time range."
        
    except FileNotFoundError:
        logger.error("google-analytics-mcp command not found")
        return "The Google Analytics MCP tool is not installed or not in the PATH. Please contact the administrator."
        
    except Exception as e:
        logger.exception("Unexpected error in MCP query")
        return f"An unexpected error occurred: {str(e)}"
