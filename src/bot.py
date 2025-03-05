import os
import slack_bolt
import google.generativeai as genai
from dotenv import load_dotenv
import trello

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

        # Gemini AI Model
        self.ai_model = genai.GenerativeModel('gemini-2.0-flash')

        # Trello Client
        self.trello_client = trello.TrelloClient(
            api_key=os.getenv('TRELLO_API_KEY'),
            api_secret=os.getenv('TRELLO_API_SECRET')
        )

        # Register Event Handlers
        self._register_handlers()

    def _register_handlers(self):
        # New User Join Notification
        @self.slack_app.event("team_join")
        def welcome_new_user(event, say):
            user = event["user"]
            welcome_message = f"""
            Greetings, Master <@{user['id']}>! 🎉
            
            I'm Pennyworth, T. Flagship's service bot. Here's what you need to know:
            • Check out our onboarding resources
            • Join relevant Slack channels
            • Set up your workspace profile
            """
            say(welcome_message)

        # AI Assistant Interaction
        @self.slack_app.message("!ai")
        def ai_assistant(message, event, say):
            user = event["user"]
            try:
                # Extract user query
                query = message['text'].replace('!ai', '').strip()
                
                # Generate AI response
                response = self.ai_model.generate_content(query)
                
                say(response.text)
            except Exception as e:
                say(f"Apologies Master <@{user['id']}>, I've encountered an error: {str(e)}")

        # Trello Workflow Handlers
        @self.slack_app.message("!trello")
        def handle_trello_workflow(message, say):
            # Example: Create a new Trello card from Slack
            try:
                board = self.trello_client.list_boards()[0]  # First board
                todo_list = board.list_lists()[0]  # First list
                
                card_title = message['text'].replace('!trello', '').strip()
                todo_list.add_card(name=card_title)
                
                say(f"Created Trello card: {card_title}")
            except Exception as e:
                say(f"Trello workflow error: {str(e)}")

    def start(self):
        # Start the Slack bot
        handler = slack_bolt.adapter.socket_mode.SocketModeHandler(
            self.slack_app, 
            os.getenv('SLACK_APP_TOKEN')
        )
        handler.start()

def main():
    bot = PennyworthBot()
    bot.start()

if __name__ == "__main__":
    main()