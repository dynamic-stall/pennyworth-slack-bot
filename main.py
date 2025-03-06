"""
Pennyworth Service Bot - Main Application Entry Point
"""

import os
import re
import logging
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from src.ai_assistant import AIAssistant
from src.trello_workflows import TrelloWorkflow
from src.utils import parse_command, format_slack_message

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize Slack app at module level
app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)

# Initialize components
ai_assistant = AIAssistant(
    api_key=os.getenv('GOOGLE_GEMINI_API_KEY')
)

trello_workflow = TrelloWorkflow(
    api_key=os.getenv('TRELLO_API_KEY'),
    api_secret=os.getenv('TRELLO_API_SECRET'),
    token=os.getenv('TRELLO_TOKEN')
)

# Register event handlers
@app.event("team_join")
def handle_team_join(event, say):
    """Handle when a new user joins the team"""
    user = event["user"]
    welcome_message = (
        f"Welcome to the team, <@{user['id']}>! 🎉\n\n"
        "I'm Pennyworth, your service bot. Here's what you need to know:\n"
        "• Check out our onboarding resources\n"
        "• Join relevant Slack channels\n"
        "• Set up your workspace profile"
    )
    say(welcome_message)
    
    # Notify a specific channel about the new user
    admin_channel = os.getenv('ADMIN_CHANNEL', 'C0123456789')
    app.client.chat_postMessage(
        channel=admin_channel,
        text=f"New team member alert! <@{user['id']}> has joined the workspace."
    )

@app.message(re.compile(r"^!ai"))
def handle_ai_request(message, say):
    """Handle AI assistant requests"""
    # Extract query (remove !ai prefix)
    text = message['text']
    query = text.replace('!ai', '', 1).strip()
    
    if not query:
        say("Please provide a question or prompt after !ai")
        return
        
    # Get user info for context
    user_id = message.get('user')
    user_info = app.client.users_info(user=user_id).get('user', {})
    
    # Generate AI response with user context
    context = {
        "user_name": user_info.get('real_name', ''),
        "channel": message.get('channel', '')
    }
    
    response = ai_assistant.ask(query, context)
    say(response)

@app.message(re.compile(r"^!trello"))
def handle_trello_command(message, say):
    """Handle Trello workflow commands"""
    text = message['text'].replace('!trello', '', 1).strip()
    parts = text.split(' ', 2)  # Split into command and content
    
    if not parts or parts[0] == "":
        # Show help
        help_text = (
            "*Trello Commands*\n"
            "• `!trello add [board] [list] [card title]` - Add a new card\n"
            "• `!trello move [card_id] [list]` - Move a card to a different list\n"
            "• `!trello boards` - List available boards\n"
            "• `!trello lists [board]` - List available lists in a board\n"
            "• `!trello help` - Show this help message"
        )
        say(help_text)
        return
    
    command = parts[0].lower()
    
    if command == "add" and len(parts) >= 3:
        # Format: !trello add [board] [list] [card title]
        board_name, list_name, *title_parts = parts[1].split(' ', 2)
        title = ' '.join(title_parts) if title_parts else "New Card"
        
        # Use AI to generate a description
        description = ai_assistant.create_task_description(title)
        
        # Create the card
        result = trello_workflow.create_card(board_name, list_name, title, description)
        
        if result.get('success'):
            say(f"Card created: {result['card_name']}\nURL: {result['card_url']}")
        else:
            say(f"Failed to create card: {result.get('error', 'Unknown error')}")
    
    elif command == "move" and len(parts) >= 2:
        # Format: !trello move [card_id] [list]
        card_id, target_list = parts[1].split(' ', 1)
        
        result = trello_workflow.move_card(card_id, target_list)
        
        if result.get('success'):
            say(f"Card moved: {result['message']}")
        else:
            say(f"Failed to move card: {result.get('error', 'Unknown error')}")
    
    elif command == "boards":
        # List available boards
        boards = trello_workflow.client.list_boards()
        board_names = [board.name for board in boards]
        
        if board_names:
            say("*Available Boards*\n• " + "\n• ".join(board_names))
        else:
            say("No boards available.")
    
    elif command == "lists" and len(parts) >= 2:
        # Format: !trello lists [board]
        board_name = parts[1]
        board = trello_workflow.get_board(board_name)
        
        if board:
            lists = board.list_lists()
            list_names = [lst.name for lst in lists]
            say(f"*Lists in {board_name}*\n• " + "\n• ".join(list_names))
        else:
            say(f"Board '{board_name}' not found.")
    
    else:
        say("Unknown command. Try `!trello help` for available commands.")

def start_bot():
    """Start the Slack bot - can be called from another module"""
    try:
        logger.info("Starting Pennyworth Service Bot")
        app_token = os.getenv('SLACK_APP_TOKEN')
        handler = SocketModeHandler(app, app_token)
        handler.start()
    except Exception as e:
        logger.error(f"Failed to start Pennyworth Service Bot: {e}")
        raise

def main():
    """Main application entry point"""
    try:
        logger.info("Initializing Pennyworth Service Bot")
        start_bot()
    except Exception as e:
        logger.error(f"Failed to start Pennyworth Service Bot: {e}")
        raise

if __name__ == "__main__":
    main()