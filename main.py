"""
Pennyworth Slack Bot - Core Functionality
"""
import os
import logging
import random
import re
import datetime
import pytz
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Import components
from src.ai_assistant import AIAssistant
from src.trello_workflows import TrelloWorkflow

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
)

ai_assistant = AIAssistant(
    api_key=os.getenv('GOOGLE_GEMINI_API_KEY')
)

trello_workflow = TrelloWorkflow(
    api_key=os.getenv('TRELLO_API_KEY'),
    api_secret=os.getenv('TRELLO_API_SECRET'),
    token=os.getenv('TRELLO_TOKEN')
)

# Helper function to get time-appropriate greeting
def _get_time_greeting():
    """
    Return a greeting based on the time of day.
    'time_zone' is set via GitHub repo variables ${{ vars.TIMEZONE }}).
    """
    time_zone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))
    current_time = datetime.datetime.now(time_zone)
    hour = current_time.hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good night"

# Pennyworth name addressee helper function
def get_preferred_name(user_info):
    """
    Get the preferred name to address a user according to precedence rules:
    1. Display name if available
    2. First name (ignoring honorifics) if available
    3. Full real name if no spaces
    """
    # Try to get profile info
    profile = user_info.get('profile', {})
    
    # Check for display name (highest precedence)
    display_name = profile.get('display_name')
    if display_name and display_name.strip():
        return display_name.strip()
    
    # Check for real name
    real_name = profile.get('real_name')
    if not real_name or not real_name.strip():
        return None
        
    real_name = real_name.strip()
    
    # If no spaces, use the whole name
    if ' ' not in real_name:
        return real_name
    
    # Split by spaces to get parts
    name_parts = real_name.split()
    
    # Check for honorifics to skip
    honorifics = ['mr', 'ms', 'mrs', 'dr', 'prof', 'sir', 'madam', 'miss', 'lord', 'lady', 'rev']
    if name_parts[0].lower().rstrip('.') in honorifics and len(name_parts) > 1:
        # Skip the honorific and use the next part
        return name_parts[1]
    else:
        # Otherwise use the first part
        return name_parts[0]

def get_user_address(user_id):
    """Get the appropriate way to address a user"""
    try:
        # Get full user info
        user_info = app.client.users_info(user=user_id).get('user', {})
        preferred_name = get_preferred_name(user_info)
        
        if preferred_name:
            return f"Master {preferred_name}"
        else:
            return f"Master <@{user_id}>"
    except Exception as e:
        logger.warning(f"Could not retrieve user info: {e}")
        return f"Master <@{user_id}>"

# Enhanced Alfred-style greeting
@app.message("hello")
def say_hello(message, say):
    greeting = _get_time_greeting()
    user_address = get_user_address(message['user'])
    
    # Common responses for any time of day
    common_responses = [
        f"{greeting}, {user_address}. How might I be of service today?",
        f"{greeting}, {user_address}. I trust you're well. Is there anything you require?",
        f"{greeting}, {user_address}. Always a pleasure to be of assistance.",
        f"{greeting}, {user_address}. I've prepared your digital workspace. What shall we accomplish today?"
    ]
    
    # Start with the common responses
    responses = common_responses.copy()

    # Add time-specific responses
    if greeting in ["Good evening", "Good night"]:
        responses.append(f"{greeting}, {user_address}. Dare we hope that Gotham treats you to an early evening? :bat:")
    
    if greeting == "Good morning":
        responses.append(f"{greeting}, {user_address}. I've prepared your usual breakfast: toast :bread:, coffee :coffee:, bandages :adhesive_bandage:.")

    # Randomize response
    response = responses[random.randint(0, len(responses) - 1)]
    say(response)

# Register event handlers
@app.event("team_join")
def handle_team_join(event, say):
    """Handle when a new user joins the team"""
    user = event["user"]
    
    # Get workspace name
    try:
        workspace_info = app.client.team_info()
        workspace_name = workspace_info["team"]["name"]
    except Exception as e:
        logger.warning(f"Could not retrieve workspace name: {e}")
        workspace_name = "the ship"
    
    user_address = get_user_address(user['id'])
    
    # Direct welcome message to the user
    welcome_message = (
        f"Good day, {user_address}. Welcome aboard {workspace_name}. 🎩\n\n"
        "I'm Pennyworth, your AI butler. Allow me to assist with your orientation:\n"
        "• The study (TBD) contains our documentation and project resources\n"
        "• The #galley channel hosts our common area for all manner of discourse and shenaniganry\n"
        "• Your quarters await your personal profile setup\n\n"
        "Should you require anything, simply summon me with `!ai [your question]` or engage with me via the *Apps* directory below."
    )
    say(welcome_message)
       
    # Notify #galley channel about the new user with Alfred-style formality
    galley_channel = os.getenv('GALLEY_CHANNEL')
    
    # Create a formal butler-style announcement for #galley
    galley_announcement = (
        f"*Announcing a new arrival* 🎩\n\n"
        f"May I present {user_address}, who has just joined our distinguished company.\n\n"
        f"*For those unfamiliar with my services:*\n"
        f"• Summon my assistance with `!ai [your question]` for information, guidance, or witty banter\n"
        f"• Request `!summarize` in any channel for a concise briefing of recent discussions\n"
        f"• React to messages with emoji reactions that I shall dutifully mirror\n"
        f"• Create reminders that I shall manage with utmost attention to detail\n"
        f"• Engage me in direct messages for more private inquiries\n\n"
        f"A full catalogue of my capabilities is available via the <https://triskelionflagship.slack.com/marketplace/A08EFNHTC57-pennyworth-service-bot?tab=settings&next_id=0|App Marketplace>.\n\n"
        f"I shall be attending to {user_address}'s orientation. Do make them feel welcome.\n"
        f"As always, I remain at your service in all channels. Simply call when needed."
    )
    
    # Send the announcement to #galley
    app.client.chat_postMessage(
        channel=galley_channel,
        text=galley_announcement,
        unfurl_links=False
    )
    
    # Now send project-specific welcome messages
    send_project_welcome_messages(user['id'])@app.command("/pennyworth")

def send_project_welcome_messages(user_id):
    """Send welcome messages to project channels for new users"""
    user_address = get_user_address(user_id)
    
    # Project UX-Ops Channel
    uxops_channel = os.getenv('UXOPS_CHANNEL')
    if uxops_channel:
        uxops_welcome = (
            f"*Welcome to #project-ux-ops*, {user_address} 🎩\n\n"
            f"This channel is dedicated to our joint UI/UX + DevOps initiatives. Allow me to acquaint you with the resources at your disposal:\n\n"
            f"• *Channel Overview*: <https://triskelionflagship.slack.com/canvas/C08G80DD9PE|Prj. UX-Ops Project Canvas>\n"
            f"• *Project Management*: <https://trello.com/b/DH3kuqWZ/00-project-overview|Prj. UX-Ops Trello Board>\n\n"
            f"I'm configured to assist with your Trello workflows in this channel:\n"
            f"• `!trello create [card title]` - Create a new task card\n"
            f"• `!trello lists` - View all task categories\n"
            f"• `!trello boards` - View connected project boards\n\n"
            f"Should you require anything else, Master {user_id.split('.')[-1]}, I remain at your service."
        )
        
        try:
            app.client.chat_postMessage(
                channel=uxops_channel,
                text=uxops_welcome,
                unfurl_links=False
            )
            logger.info(f"Sent UX Ops welcome message to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send UX Ops welcome: {e}")
    
    # Afrotaku Channel
    afrotaku_channel = os.getenv('AFROTAKU_CHANNEL')
    if afrotaku_channel:
        afrotaku_welcome = (
            f"*Welcome to #afrotaku*, {user_address} 🎩\n\n"
            f"This channel is dedicated to our Afrotaku creative initiatives. Allow me to present the resources at your disposal:\n\n"
            f"• *Channel Overview*: <https://triskelionflagship.slack.com/canvas/C08GLJD9RH9|Afrotaku Project Canvas>\n"
            f"• *Project Management*: <https://trello.com/b/hCjGH8SJ/00-project-overview|Afrotaku Trello Board>\n\n"
            f"I've been programmed to assist with your Trello workflows in this channel:\n"
            f"• `!trello create [card title]` - Create a new task card\n"
            f"• `!trello lists` - View all task categories\n"
            f"• `!trello boards` - View connected project boards\n\n"
            f"Should you wish to link conversations to tasks, simply use `!trello comment [card ID] [your comment]`\n\n"
            f"As with all project channels, I can provide summaries of discussions with `!summarize`.\n\n"
            f"I shall endeavor to make your creative process as seamless as possible, {user_address}."
        )
        
        try:
            app.client.chat_postMessage(
                channel=afrotaku_channel,
                text=afrotaku_welcome,
                unfurl_links=False
            )
            logger.info(f"Sent Afrotaku welcome message to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send Afrotaku welcome: {e}")

def handle_command(ack, command, say):
    ack()  # Must acknowledge command receipt
    user_address = get_user_address(command['user_id'])
    say(f"At your service, {user_address}. How may I assist?")

@app.message(re.compile(r"thanks|thank you"))
def handle_thanks(message, say):
    user_address = get_user_address(message['user'])
    say(f"You're most welcome, {user_address}.")

@app.message(re.compile(r"^!ai\s+(.+)"))
def handle_ai_request(message, say):
    # Extract the query (everything after !ai)
    match = re.search(r"^!ai\s+(.+)", message['text'])
    query = match.group(1) if match else None
    
    if not query:
        say("Please provide a question after !ai")
        return
    
    # Get user info for context
    user_id = message.get('user')
    user_info = app.client.users_info(user=user_id).get('user', {})
    
    # Generate AI response with enhanced user context
    context = {
        "user": user_id,
        "user_info": user_info,
        "channel": message.get('channel', '')
    }
    
    response = ai_assistant.ask(query, context)
    say(response)

@app.message(re.compile(r"^!summarize"))
def summarize_conversation(message, say):
    try:
        channel_id = message['channel']
        
        # Get channel info
        channel_info = app.client.conversations_info(channel=channel_id)
        channel_name = channel_info['channel']['name'] if 'name' in channel_info['channel'] else "this conversation"
        
        # Fetch conversation history
        history = app.client.conversations_history(channel=channel_id, limit=30)
        
        # Skip the command message itself
        messages = [msg['text'] for msg in history['messages'] if 'text' in msg and '!summarize' not in msg['text']][::-1]
        
        if not messages:
            say("There's no recent conversation to summarize, sir.")
            return
            
        context = {
            "channel_name": channel_name,
            "messages": " ".join(messages),
            "user": message.get('user')  # Pass the user ID for personalization
        }
        
        # Use your existing AI assistant
        summary = ai_assistant.summarize_conversation(context)
        
        say(f"*Summary of recent conversation in #{channel_name}*\n\n{summary}")
    
    except Exception as e:
        logger.error(f"Error summarizing conversation: {e}")
        say("I'm terribly sorry, but I couldn't summarize the conversation at this time.")

@app.message(re.compile(r"^!trello\s+(.+)"))
def handle_trello_command(message, say):
    """Handle Trello commands with Alfred-style responses"""
    text = message['text'].replace('!trello', '', 1).strip()
    parts = text.split(' ', 1)
    command = parts[0].lower() if parts else ""
    user_id = message['user']
    user_address = get_user_address(user_id)
    
    # Get channel info to determine which board to use by default
    channel_id = message.get('channel', '')
    
    try:
        # Handle different trello commands
        if command == "create" and len(parts) > 1:
            # Parse card title and optional list name
            card_info = parts[1].strip()
            list_name = "To Do"  # Default list
            board_name = "Main Board"  # Default board
            
            # Check if card info specifies a list
            if " in " in card_info:
                card_title, list_spec = card_info.split(" in ", 1)
                list_name = list_spec.strip()
            else:
                card_title = card_info
            
            # Determine board based on channel
            if channel_id == os.getenv('UXOPS_CHANNEL'):
                board_name = "Prj. UX-Ops"
            elif channel_id == os.getenv('AFROTAKU_CHANNEL'):
                board_name = "Afrotaku"
            
            # Generate AI description
            description = ai_assistant.create_task_description(card_title)
            
            # Create the card
            result = trello_workflow.create_card(
                board_name=board_name, 
                list_name=list_name, 
                title=card_title, 
                description=description
            )
            
            if result['success']:
                say(f"I've created your card in *{list_name}*, {user_address}.\n*Title:* {result['card_name']}\n*URL:* {result['card_url']}")
            else:
                say(f"I'm terribly sorry, {user_address}. I was unable to create the card: {result.get('error', 'Unknown error')}")
        
        elif command == "boards":
            # List all boards
            all_boards = trello_workflow.client.list_boards()
            if all_boards:
                board_list = "\n".join([f"• *{board.name}*" for board in all_boards])
                say(f"The following Trello boards are at your disposal, {user_address}:\n\n{board_list}")
            else:
                say(f"I'm afraid I couldn't find any Trello boards, {user_address}. Would you like me to create one?")
        
        elif command == "lists" and len(parts) > 1:
            # Get lists for a specific board
            board_name = parts[1].strip()
            board = trello_workflow.get_board(board_name)
            
            if board:
                lists = board.list_lists()
                if lists:
                    list_names = "\n".join([f"• *{trello_list.name}*" for trello_list in lists])
                    say(f"For the *{board_name}* board, the following lists are available, {user_address}:\n\n{list_names}")
                else:
                    say(f"The *{board_name}* board appears to be empty, {user_address}. Would you like me to create some lists?")
            else:
                say(f"I couldn't find a board named *{board_name}*, {user_address}.")
        
        elif command == "comment" and len(parts) > 1:
            # Format: !trello comment [card_id] [comment_text]
            comment_parts = parts[1].strip().split(' ', 1)
            if len(comment_parts) < 2:
                say(f"The proper format is `!trello comment [card_id] [comment_text]`, {user_address}.")
                return
                
            card_id = comment_parts[0]
            comment_text = comment_parts[1]
            
            # Add comment
            result = trello_workflow.add_comment(card_id, comment_text)
            
            if result['success']:
                say(f"I've added your comment to the card, {user_address}.")
            else:
                say(f"I'm terribly sorry, {user_address}. I couldn't add your comment: {result.get('error', 'Unknown error')}")
        
        elif command == "move" and len(parts) > 1:
            # Format: !trello move [card_id] to [list_name]
            move_text = parts[1].strip()
            if " to " not in move_text:
                say(f"The proper format is `!trello move [card_id] to [list_name]`, {user_address}.")
                return
                
            card_id, list_name = move_text.split(" to ", 1)
            card_id = card_id.strip()
            list_name = list_name.strip()
            
            # Move card
            result = trello_workflow.move_card(card_id, list_name)
            
            if result['success']:
                say(f"I've moved the card to *{list_name}*, {user_address}.")
            else:
                say(f"I was unable to move the card, {user_address}: {result.get('error', 'Unknown error')}")
        
        else:
            # Help message for unknown commands
            help_text = (
                f"*Trello Commands*, {user_address}:*\n"
                "• `!trello create [card title] in [list name]` - Create a new task card\n"
                "• `!trello move [card ID] to [list name]` - Move a card to another list\n"
                "• `!trello comment [card ID] [comment text]` - Add a comment to a card\n"
                "• `!trello boards` - List available boards\n"
                "• `!trello lists [board name]` - List the lists in a specific board\n"
            )
            say(help_text)
            
    except Exception as e:
        logger.error(f"Error handling Trello command: {e}")
        say(f"I apologize for the inconvenience, {user_address}, but I encountered an error processing your Trello command. Perhaps we should try again when the Bat-Computer is functioning properly.")

# Add more handlers here...

def start_bot():
    """Start the bot in socket mode"""
    try:
        handler = SocketModeHandler(app, os.getenv('SLACK_APP_TOKEN'))
        logger.info("Starting Pennyworth bot in socket mode")
        handler.start()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

# Only run when executed directly
if __name__ == "__main__":
    start_bot()