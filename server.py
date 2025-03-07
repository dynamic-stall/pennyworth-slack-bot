import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import datetime
import pytz
import random
import re

# Import components from main.py
from main import app, start_bot

# Configure logging and environment
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize app
app = App(
    token=os.getenv('SLACK_BOT_TOKEN'),
    signing_secret=os.getenv('SLACK_SIGNING_SECRET')
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


# Enhanced Alfred-style greeting
@app.message("hello")
def say_hello(message, say):
    greeting = _get_time_greeting()
    user = message['user']
    
    # Common responses for any time of day
    common_responses = [
        f"{greeting}, Master <@{user}>. How might I be of service today?",
        f"{greeting}, Master <@{user}>. I trust you're well. Is there anything you require?",
        f"{greeting}, Master <@{user}>. Always a pleasure to be of assistance.",
        f"{greeting}, Master <@{user}>. I've prepared your digital workspace. What shall we accomplish today?"
    ]
    
    # Start with the common responses
    responses = common_responses.copy()

    # Add time-specific responses
    if greeting in ["Good evening", "Good night"]:
        responses.append(f"{greeting}, Master <@{user}>. Dare we hope that Gotham treats you to an early evening? :bat:")
    
    if greeting == "Good morning":
        responses.append(f"{greeting}, Master <@{user}>. I've prepared your usual breakfast: toast :bread:, coffee :coffee:, bandages :adhesive_bandage:.")

    # Randomize response
    response = responses[random.randint(0, len(responses) - 1)]
    say(response)

# Example of adding an event handler
@app.event("team_join")
def handle_team_join(event, say):
    user = event["user"]["id"]
    welcome = _get_time_greeting()
    say(f"{welcome}, Master <@{user}>. Welcome to Triskelion Flagship's Lower Deck. I'll be assisting you.")

# Example of adding a command handler
@app.command("/pennyworth")
def handle_command(ack, command, say):
    ack()  # Must acknowledge command receipt
    say(f"At your service, Master <@{command['user_id']}>. How may I assist?")

# Example of adding a message handler with regex
@app.message(re.compile(r"thanks|thank you"))
def handle_thanks(message, say):
    say(f"You're most welcome, Master <@{message['user']}>.")

def start_bot():
    """Start the bot in socket mode"""
    try:
        handler = SocketModeHandler(app, os.getenv('SLACK_APP_TOKEN'))
        logger.info("Starting bot in socket mode")
        handler.start()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Health check OK')
    
    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format % args))

def run_server():
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    
    logger.info(f"Starting server on port {port}")
    
    try:
        httpd = HTTPServer(server_address, HealthCheckHandler)
        logger.info(f"Server started successfully")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run HTTP server in main thread
    logger.info("Starting HTTP server with bot in background")
    run_server()