"""
Pennyworth Bot - Core Bot Implementation
"""

import os
import logging
import random
import slack_bolt
import google.generativeai as genai
import re
from dotenv import load_dotenv
import trello

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Gemini AI Configuration
genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))

class PennyworthBot:
    def __init__(self):
        # Slack Bot Initialization
        self.slack_app = slack_bolt.App(
            token=os.getenv('SLACK_BOT_TOKEN'),
            signing_secret=os.getenv('SLACK_SIGNING_SECRET')
        )

        # Gemini AI Model - Use environment variable with default fallback
        self.ai_model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'))

        # Trello Client
        self.trello_client = trello.TrelloClient(
            api_key=os.getenv('TRELLO_API_KEY'),
            api_secret=os.getenv('TRELLO_API_SECRET'),
            token=os.getenv('TRELLO_TOKEN')
        )

        # Register Event Handlers
        self._register_handlers()
        logger.info("Pennyworth Bot initialized successfully")

    def _get_alfred_style_response(self, user_id, category="general"):
        """Generate Alfred-style responses based on category"""
        responses = {
            "general": [
                f"How may I be of service, Master <@{user_id}>?",
                f"At your disposal, Master <@{user_id}>.",
                f"As you wish, Master <@{user_id}>."
            ],
            "error": [
                f"My sincerest apologies, Master <@{user_id}>. There seems to be a technical issue.",
                f"I've encountered an error, Master <@{user_id}>. Perhaps the Bat-Computer needs maintenance.",
                f"Regrettably, I've hit a snag, Master <@{user_id}>. Shall I prepare some tea while we troubleshoot?"
            ],
            "success": [
                f"Task completed, Master <@{user_id}>. Will there be anything else?",
                f"It's been taken care of, Master <@{user_id}>.",
                f"Consider it done, Master <@{user_id}>. Your digital affairs are in order."
            ],
            "greeting": [
                f"Good day, Master <@{user_id}>. How might I assist you today?",
                f"Welcome, Master <@{user_id}>. The digital manor is prepared for your arrival.",
                f"Master <@{user_id}>. A pleasure as always. What services do you require today?"
            ]
        }
        
        category_responses = responses.get(category, responses["general"])
        return random.choice(category_responses)

    def _register_handlers(self):
        # New User Join Notification with improved Alfred tone
        @self.slack_app.event("team_join")
        def welcome_new_user(event, say):
            try:
                user = event["user"]
                welcome_message = f"""
*{self._get_alfred_style_response(user['id'], "greeting")}* 🎩

I'm Pennyworth, your faithful digital butler. Permit me to assist with your onboarding:

• *Manor Protocols:* I suggest reviewing our team documentation
• *Common Areas:* Consider joining our primary communication channels
• *Personal Effects:* Please complete your profile at your convenience

Should you require assistance, simply mention me by name, or use `!ai` followed by your inquiry.

The team has been notified of your arrival, sir. Welcome aboard.
                """
                say(welcome_message)
                logger.info(f"Welcomed new user: {user['id']}")
            except Exception as e:
                logger.error(f"Error welcoming new user: {e}")
                say("A technical issue prevents me from properly welcoming our new guest. My apologies.")

        # AI Assistant Interaction with Alfred personality
        @self.slack_app.message("!ai")
        def ai_assistant(message, say):
            user = message.get('user', 'unknown')
            try:
                # Extract user query
                query = message['text'].replace('!ai', '').strip()
                
                if not query:
                    say(f"How may I assist you, Master <@{user}>? Please provide a query after the !ai command.")
                    return
                
                # Create Alfred-style prompt
                alfred_prompt = f"""
You are Alfred Pennyworth from the Batman Arkham video game series.
Use a formal, dignified, and slightly sardonic tone.
Address the user as "Master <@{user}>".
Be helpful, wise, and occasionally witty, but always respectful.
Include subtle references to being a butler when appropriate.

User query: {query}
"""
                
                # Generate AI response
                logger.info(f"Generating AI response for user {user}")
                response = self.ai_model.generate_content(alfred_prompt)
                
                say(response.text)
            except Exception as e:
                logger.error(f"AI assistant error: {str(e)}")
                error_message = self._get_alfred_style_response(user, "error")
                say(f"{error_message} Technical details: {str(e)}")

        # Trello Workflow Handlers with enhanced functionality
        @self.slack_app.message(re.compile(r"^!trello\s+(.+)"))
        def handle_trello_workflow(message, say):
            user = message.get('user', 'unknown')
            try:
                # Extract command parts
                text = message['text'].replace('!trello', '', 1).strip()
                parts = text.split(' ', 1)
                command = parts[0].lower() if parts else ""
                
                # Handle different Trello commands
                if command == "create" and len(parts) > 1:
                    # Format: !trello create Card Title
                    card_title = parts[1]
                    
                    # Get default board and list
                    boards = self.trello_client.list_boards()
                    if not boards:
                        say(f"Master <@{user}>, I'm unable to locate any Trello boards. Perhaps one needs to be created first?")
                        return
                        
                    board = boards[0]  # Using first board as default
                    lists = board.list_lists()
                    if not lists:
                        say(f"Master <@{user}>, the board appears to be empty. Shall I create a list for you?")
                        return
                        
                    todo_list = lists[0]  # First list
                    
                    # Create AI-generated description
                    description_prompt = f"""
Create a concise task description (max 100 words) for: {card_title}
Include:
- What needs to be done
- Potential first steps
- Key considerations

Write in the style of Alfred Pennyworth from the Batman Arkham games:
formal, dignified, and slightly sardonic.
"""
                    description_response = self.ai_model.generate_content(description_prompt)
                    description = description_response.text.strip()
                    
                    # Create card
                    new_card = todo_list.add_card(name=card_title, desc=description)
                    
                    say(f"I've created your Trello card, Master <@{user}>.\n*Title:* {card_title}\n*List:* {todo_list.name}\n*Board:* {board.name}\n*URL:* {new_card.url}")
                    logger.info(f"Created Trello card for user {user}: {card_title}")
                    
                elif command == "boards":
                    # List available boards
                    boards = self.trello_client.list_boards()
                    if boards:
                        board_list = "\n".join([f"• {board.name}" for board in boards])
                        say(f"Your Trello boards, Master <@{user}>:\n{board_list}")
                    else:
                        say(f"You don't appear to have any Trello boards, Master <@{user}>. Shall I assist you in creating one?")
                        
                elif command == "lists" and len(parts) > 1:
                    # Format: !trello lists BoardName
                    board_name = parts[1]
                    boards = self.trello_client.list_boards()
                    matching_boards = [b for b in boards if b.name.lower() == board_name.lower()]
                    
                    if matching_boards:
                        board = matching_boards[0]
                        lists = board.list_lists()
                        if lists:
                            list_names = "\n".join([f"• {lst.name}" for lst in lists])
                            say(f"Lists in *{board.name}*, Master <@{user}>:\n{list_names}")
                        else:
                            say(f"The board *{board.name}* appears to be empty, Master <@{user}>.")
                    else:
                        say(f"I couldn't find a board named *{board_name}*, Master <@{user}>.")
                
                else:
                    # Help message
                    help_text = """
*Trello Commands*:
• `!trello create [card title]` - Create a new card on the default board
• `!trello boards` - List your Trello boards
• `!trello lists [board name]` - List the lists in a specific board
• `!trello help` - Show this help message
"""
                    say(f"Master <@{user}>, allow me to explain the Trello commands:\n{help_text}")
                    
            except Exception as e:
                logger.error(f"Trello workflow error: {str(e)}")
                error_message = self._get_alfred_style_response(user, "error") 
                say(f"{error_message} The Trello system appears to be offline: {str(e)}")

    def start(self):
        # Start the Slack bot
        try:
            logger.info("Starting Pennyworth Bot in Socket Mode")
            handler = slack_bolt.adapter.socket_mode.SocketModeHandler(
                self.slack_app, 
                os.getenv('SLACK_APP_TOKEN')
            )
            handler.start()
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            raise

def main():
    logger.info("Initializing Pennyworth Bot")
    bot = PennyworthBot()
    bot.start()

if __name__ == "__main__":
    main()