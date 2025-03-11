"""
Utility modules for Pennyworth Service Bot
"""

import re
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

def parse_command(text: str) -> Dict[str, Any]:
    """
    Parse a command string into command and arguments
    
    Args:
        text (str): Raw command text from Slack
        
    Returns:
        Dict containing command and arguments
    """
    # Remove extra whitespace and split by spaces
    parts = text.strip().split()
    if not parts:
        return {'command': None, 'args': []}
    
    # Extract command (first word)
    command = parts[0].lower()
    if command.startswith('!'):
        command = command[1:]
    
    # Extract arguments (everything after command)
    args = parts[1:] if len(parts) > 1 else []
    
    return {'command': command, 'args': args}

def format_slack_message(message: str, blocks: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Format a message for Slack with optional blocks
    
    Args:
        message (str): Plain text message
        blocks (list, optional): Slack blocks for rich formatting
        
    Returns:
        Dict formatted for Slack API
    """
    response = {'text': message}
    if blocks:
        response['blocks'] = blocks
    return response

def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now(timezone.utc).isoformat()

def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection
    
    Args:
        text (str): Raw input text
        
    Returns:
        Sanitized text string
    """
    # Remove potential code injection characters
    sanitized = re.sub(r'[`\'";]', '', text)
    return sanitized

def format_error_response(error_message: str) -> Dict[str, Any]:
    """Format a standardized error response for users"""
    return format_slack_message(f"Error: {error_message}")

def create_section_block(text: str) -> Dict[str, Any]:
    """Create a simple section block with text"""
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }

def create_thread_reply(message: str, thread_ts: str) -> Dict[str, Any]:
    """Create a message that replies in a thread"""
    response = format_slack_message(message)
    response['thread_ts'] = thread_ts
    return response