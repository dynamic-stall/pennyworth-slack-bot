"""
Pennyworth Bot - Core Bot Implementation
"""

import os
import logging
import random
import datetime
import pytz
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import google.generativeai as genai
from dotenv import load_dotenv
import trello
from typing import Optional, Dict, Any, Callable, List

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
        # Slack Bot initialization
        self.slack_app = App(
            token=os.getenv('SLACK_BOT_TOKEN'),
            signing_secret=os.getenv('SLACK_SIGNING_SECRET')
        )

        # Gemini AI model - use environment variable with default fallback
        self.ai_model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-2.0-flash'))

        # Trello client
        self.trello_client = trello.TrelloClient(
            api_key=os.getenv('TRELLO_API_KEY'),
            api_secret=os.getenv('TRELLO_API_SECRET'),
            token=os.getenv('TRELLO_TOKEN')
        )

        # Register Event Handlers
        self._register_handlers()
        logger.info("Pennyworth Bot initialized successfully")

    def _get_time_greeting(self):
        """
        Return a greeting based on the time of day.
        'time_zone' is set via environment variable TIMEZONE.
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

    def get_preferred_name(self, user_info):
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

    def get_user_address(self, user_id):
        """Get the appropriate way to address a user"""
        try:
            # Get full user info
            user_info = self.slack_app.client.users_info(user=user_id).get('user', {})
            preferred_name = self.get_preferred_name(user_info)
            
            if preferred_name:
                return f"Master {preferred_name}"
            else:
                return f"Master <@{user_id}>"
        except Exception as e:
            logger.warning(f"Could not retrieve user info: {e}")
            return f"Master <@{user_id}>"

    def _get_alfred_style_response(self, user_id, category="general"):
        """Generate Alfred-style responses based on category"""
        # Use get_user_address for personalization
        user_address = self.get_user_address(user_id)
        
        responses = {
            "general": [
                f"How may I be of service, {user_address}?",
                f"At your disposal, {user_address}.",
                f"As you wish, {user_address}."
            ],
            "error": [
                f"My sincerest apologies, {user_address}. There seems to be a technical issue.",
                f"I've encountered an error, {user_address}. Perhaps the Bat-Computer needs maintenance.",
                f"Regrettably, I've hit a snag, {user_address}. Shall I prepare some tea while we troubleshoot?"
            ],
            "success": [
                f"Task completed, {user_address}. Will there be anything else?",
                f"It's been taken care of, {user_address}.",
                f"Consider it done, {user_address}. Your digital affairs are in order."
            ],
            "greeting": [
                f"Good day, {user_address}. How might I assist you today?",
                f"Welcome, {user_address}. The digital manor is prepared for your arrival.",
                f"{user_address}. A pleasure as always. What services do you require today?"
            ]
        }
        
        category_responses = responses.get(category, responses["general"])
        return random.choice(category_responses)

    def get_time_for_location(self, location):
        """Get current time for a given location using timezone database"""
        try:
            location = location.lower().strip()
            
            # Map common city/region names to timezone strings
            common_locations = {
                'new york': 'America/New_York',
                'nyc': 'America/New_York',
                'chicago': 'America/Chicago', 
                'la': 'America/Los_Angeles',
                'alaska': 'America/Anchorage',
                'hawaii': 'Pacific/Honolulu',
                'london': 'Europe/London',
                'uk': 'Europe/London',
                'france': 'Europe/Paris',
                'germany': 'Europe/Berlin',
                'italy': 'Europe/Rome',
                'turkey': 'Europe/Istanbul',
                'japan': 'Asia/Tokyo',
                'tokyo': 'Asia/Tokyo',
                'korea': 'Asia/Seoul',
                'china': 'Asia/Shanghai',
                'india': 'Asia/Kolkata',
                'sydney': 'Australia/Sydney',
                'pacific': 'America/Los_Angeles',
                'eastern': 'America/New_York',
                'central': 'America/Chicago',
                'mountain': 'America/Denver'
            }
            
            # Try direct mapping first
            if location in common_locations:
                timezone = pytz.timezone(common_locations[location])
                current_time = datetime.datetime.now(timezone)
                return current_time.strftime("%I:%M %p on %A, %B %d")
                
            # Try partial matching for country/region
            for tz in pytz.common_timezones:
                if location in tz.lower():
                    timezone = pytz.timezone(tz)
                    current_time = datetime.datetime.now(timezone)
                    return current_time.strftime("%I:%M %p on %A, %B %d")
            
            return f"I'm afraid I don't have timezone information for '{location}'."
            
        except Exception as e:
            logger.error(f"Error getting time for location {location}: {e}")
            return f"I couldn't determine the time for {location}."

    def send_project_welcome_messages(self, user_id):
        """Send welcome messages to project channels for new users"""
        user_address = self.get_user_address(user_id)
        
        # UX Ops Project Channel
        uxops_channel = os.getenv('UXOPS_CHANNEL')
        if uxops_channel:
            try:
                uxops_welcome = (
                    f"*Welcome to #project-ux-ops*, {user_address} 🎩\n\n"
                    f"This channel is dedicated to our UX Operations initiatives. Allow me to acquaint you with the resources at your disposal:\n\n"
                    f"• *Project Overview*: <https://app.slack.com/canvas/C12345|UX Ops Project Canvas>\n"
                    f"• *Task Management*: <https://trello.com/b/abcdef|UX Ops Trello Board>\n\n"
                    f"I'm configured to assist with your Trello workflows in this channel:\n"
                    f"• `!trello create [card title]` - Create a new task card\n"
                    f"• `!trello lists` - View all task categories\n"
                    f"• `!trello boards` - View connected project boards\n\n"
                    f"Should you require anything else, I remain at your service."
                )
                
                self.slack_app.client.chat_postMessage(
                    channel=uxops_channel,
                    text=uxops_welcome,
                    unfurl_links=False
                )
                logger.info(f"Sent UX Ops welcome message to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send UX Ops welcome: {e}")
        
        # Afrotaku Project Channel
        afrotaku_channel = os.getenv('AFROTAKU_CHANNEL')
        if afrotaku_channel:
            try:
                afrotaku_welcome = (
                    f"*Welcome to #afrotaku*, {user_address} 🎩\n\n"
                    f"This channel is dedicated to our Afrotaku creative initiatives. Allow me to present the resources at your disposal:\n\n"
                    f"• *Project Overview*: <https://app.slack.com/canvas/C67890|Afrotaku Project Canvas>\n"
                    f"• *Task Management*: <https://trello.com/b/ghijkl|Afrotaku Trello Board>\n\n"
                    f"I've been programmed to assist with your Trello workflows in this channel:\n"
                    f"• `!trello create [card title]` - Create a new task card\n"
                    f"• `!trello lists` - View all task categories\n"
                    f"• `!trello boards` - View connected project boards\n\n"
                    f"Should you wish to link conversations to tasks, simply use `!trello comment [card ID] [your comment]`\n\n"
                    f"As with all project channels, I can provide summaries of discussions with `!summarize`.\n\n"
                    f"I shall endeavor to make your creative process as seamless as possible."
                )
                
                self.slack_app.client.chat_postMessage(
                    channel=afrotaku_channel,
                    text=afrotaku_welcome,
                    unfurl_links=False
                )
                logger.info(f"Sent Afrotaku welcome message to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send Afrotaku welcome: {e}")

    def create_task_description(self, task_title):
        """Generate an AI-powered task description in Alfred's style"""
        try:
            description_prompt = f"""
Create a concise task description (max 100 words) for: {task_title}
Include:
- What needs to be done
- Potential first steps
- Key considerations

Write in the style of Alfred Pennyworth from the Batman Arkham video game series:
formal, dignified, and slightly sardonic.
"""
            response = self.ai_model.generate_content(description_prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating task description: {e}")
            return f"Task: {task_title}"

    def _register_handlers(self):
        # Enhanced greeting
        @self.slack_app.message("hello")
        def say_hello(message: Dict[str, Any], say: Callable[[str], None]) -> None:
            user_id = message.get('user')
            greeting = self._get_time_greeting()
            user_address = self.get_user_address(user_id)
            
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

        @self.slack_app.event("app_mention")
        def handle_app_mentions(body: Dict[str, Any], say: Callable[[str, Optional[Dict[str, Any]]], None]) -> None:
            try:
                user_id = body["event"].get("user")
                text = body["event"].get("text", "")
                channel = body["event"].get("channel", "")
                thread_ts = body["event"].get("thread_ts")
                is_in_thread = "thread_ts" in body["event"]
                message_ts = body["event"].get("ts")

                # Extract the actual message content (remove the app mention part)
                message_text = re.sub(r"<@[A-Z0-9]+>\s*", "", text).strip()
                user_address = self.get_user_address(user_id)
                
                # If it's just a mention with no text, provide a helpful response
                if not message_text:
                    responses = [
                        f"You rang, {user_address}? How may I be of assistance?",
                        f"At your service, {user_address}. How might I help?",
                        f"{user_address}, I'm attending. What do you require?"
                    ]
                    # If in thread, reply to thread
                    if is_in_thread:
                        say(text=random.choice(responses), thread_ts=thread_ts)
                    else:
                        say(random.choice(responses))
                    return
                
                # Check for time-related queries
                time_pattern = re.compile(r"what(?:'s| is) (?:the )?time(?: in | at )([a-zA-Z\s]+)\??")
                time_match = time_pattern.search(message_text.lower())
                
                if time_match:
                    location = time_match.group(1).strip()
                    time_str = self.get_time_for_location(location)
                    response_text = f"The time in {location} is currently {time_str}, {user_address}."
                    
                    # If in thread, reply to thread
                    if is_in_thread:
                        say(text=response_text, thread_ts=thread_ts)
                    else:
                        say(response_text)
                    return
                
                # Check for workflow/deployment statistics
                if "workflow" in message_text.lower() or "deployment" in message_text.lower() or "ratio" in message_text.lower() or "success" in message_text.lower():
                    try:
                        # Get channel history
                        history = self.slack_app.client.conversations_history(
                            channel=channel,
                            limit=50  # Last 50 messages
                        )
                        
                        # Extract deployment status messages
                        deployment_messages = []
                        success_count = 0
                        failure_count = 0
                        
                        for msg in history.get("messages", []):
                            text = msg.get("text", "")
                            if "Workflow" in text and ("success" in text.lower() or "failed" in text.lower() or "failure" in text.lower()):
                                deployment_messages.append(text)
                                if "success" in text.lower():
                                    success_count += 1
                                elif "failed" in text.lower() or "failure" in text.lower():
                                    failure_count += 1
                        
                        total = success_count + failure_count
                        if total > 0:
                            ratio_info = f"""
        Based on the last {total} deployment messages in this channel:
        - Successful deployments: {success_count} ({int((success_count/total)*100)}%)  
        - Failed deployments: {failure_count} ({int((failure_count/total)*100)}%)
        - Success ratio: {success_count}:{failure_count}
        """
                            
                            # Enhanced Alfred prompt with deployment statistics
                            alfred_prompt = f"""
        You are Alfred Pennyworth from the Batman Arkham video game series.
        Use a formal, dignified, and slightly sardonic tone.
        Address the user as "{user_address}".
        Be helpful, wise, and occasionally witty, but always respectful.
        Include subtle references to being a butler, as well as Batman comic book references, when appropriate.

        IMPORTANT: Keep responses CONCISE (50-100 words maximum).

        The user asked about workflows or deployments. Here are the actual statistics:
        {ratio_info}

        User query: {message_text}

        Respond with the accurate statistics, formatted neatly. Don't make up numbers.
        """
                            
                            # Generate AI response with stats context
                            logger.info(f"Generating deployment statistics response for user {user_id}")
                            response = self.ai_model.generate_content(alfred_prompt)
                            
                            # If in thread, reply to thread
                            if is_in_thread:
                                say(text=response.text, thread_ts=thread_ts)
                            else:
                                say(response.text)
                            return
                    except Exception as e:
                        logger.error(f"Error processing deployment statistics: {e}")
                
                # Thread awareness - get thread context if in a thread
                if is_in_thread:
                    try:
                        thread_history = self.slack_app.client.conversations_replies(
                            channel=channel,
                            ts=thread_ts,
                            limit=10
                        )
                        
                        # Extract thread messages and participants
                        thread_messages = []
                        participants = set()
                        
                        for msg in thread_history.get("messages", []):
                            if "text" in msg and msg["ts"] != message_ts:  # Skip the current message
                                user_id = msg.get('user', 'unknown')
                                thread_messages.append(f"<@{user_id}>: {msg['text']}")
                                participants.add(user_id)
                        
                        # Thread-aware prompt with conversation context
                        alfred_prompt = f"""
        You are Alfred Pennyworth from the Batman Arkham video game series.
        Use a formal, dignified, and slightly sardonic tone.
        Address the user as "{user_address}".
        Be helpful, wise, and occasionally witty, but always respectful.
        Include subtle references to being a butler, as well as Batman comic book references, when appropriate.

        IMPORTANT: Keep responses CONCISE (50-100 words maximum).
        Focus on answering the question directly first, then add brief characterization.

        You're replying in a thread conversation. Here's the recent conversation:
        {chr(10).join(thread_messages[-8:])}

        The user specifically asked: "{message_text}"

        If you're being asked about information in the thread, reference it directly.
        Always respond politely, as if joining an ongoing conversation.
        """
                        
                        logger.info(f"Generating thread-aware response for user {user_id}")
                        response = self.ai_model.generate_content(alfred_prompt)
                        
                        say(text=response.text, thread_ts=thread_ts)
                        return
                    except Exception as e:
                        logger.error(f"Error processing thread context: {e}")
                        # Fall back to standard processing if thread context fails
                
                # Standard Alfred prompt for non-thread mentions
                alfred_prompt = f"""
        You are Alfred Pennyworth from the Batman Arkham video game series.
        Use a formal, dignified, and slightly sardonic tone.
        Address the user as "{user_address}".
        Be helpful, wise, and occasionally witty, but always respectful.
        Include subtle references to being a butler when appropriate.

        IMPORTANT: Keep responses CONCISE and to the point (50-100 words maximum).
        Focus on answering the question directly first, then add brief characterization.

        User query: {message_text}
        """
                
                logger.info(f"Generating AI response for mention from user {user_id}")
                response = self.ai_model.generate_content(alfred_prompt)
                
                # If in thread, reply to thread (as fallback)
                if is_in_thread:
                    say(text=response.text, thread_ts=thread_ts)
                else:
                    say(response.text)
                
            except Exception as e:
                logger.error(f"Error handling app mention: {str(e)}")
                say(f"I do apologize, but I'm experiencing some technical difficulties. Error details: {str(e)}")

        # New User Join Notification with improved Alfred tone
        @self.slack_app.event("team_join")
        def welcome_new_user(event: Dict[str, Any], say: Callable[[str], None]) -> None:
            try:
                user = event["user"]
                user_address = self.get_user_address(user['id'])
                
                # Get workspace name
                try:
                    workspace_info = self.slack_app.client.team_info()
                    workspace_name = workspace_info["team"]["name"]
                except Exception as e:
                    logger.warning(f"Could not retrieve workspace name: {e}")
                    workspace_name = "the ship"
                
                # Direct welcome message to the user
                welcome_message = (
                    f"Good day, {user_address}. Welcome aboard {workspace_name}. 🎩\n\n"
                    "I'm Pennyworth, your AI butler. Allow me to assist with your orientation:\n"
                    "• The study contains our documentation and project resources\n"
                    "• The #galley channel hosts our common area for all manner of discourse\n"
                    "• Your quarters await your personal profile setup\n\n"
                    "Should you require anything, simply summon me with `!ai [your question]` or engage with me via the *Apps* directory below."
                )
                say(welcome_message)
                logger.info(f"Welcomed new user: {user['id']}")
                
                # Notify galley channel about the new user with Alfred-style formality
                galley_channel = os.getenv('GALLEY_CHANNEL')
                
                # Create a formal butler-style announcement for galley
                galley_announcement = (
                    f"*Announcing a new arrival* 🎩\n\n"
                    f"May I present {user_address}, who has just joined our distinguished company.\n\n"
                    f"*For those unfamiliar with my services:*\n"
                    f"• Summon my assistance with `!ai [your question]` for information, guidance, or witty banter\n"
                    f"• Request `!summarize` in any channel for a concise briefing of recent discussions\n"
                    f"• React to messages with emoji reactions that I shall dutifully mirror\n"
                    f"• Create reminders that I shall manage with utmost attention to detail\n"
                    f"• Engage me in direct messages for more private inquiries\n\n"
                    f"A full catalogue of my capabilities is available via the <https://app.slack.com/app-settings/T08DSA45NDV/A08E8UZSGK9|Slack App Directory>.\n\n"
                    f"I shall be attending to {user_address}'s orientation. Do make them feel welcome.\n"
                    f"As always, I remain at your service in all channels. Simply call when needed."
                )
                
                # Send the announcement to galley
                self.slack_app.client.chat_postMessage(
                    channel=galley_channel,
                    text=galley_announcement,
                    unfurl_links=False
                )
                
                # Send project-specific welcome messages
                self.send_project_welcome_messages(user['id'])
                
            except Exception as e:
                logger.error(f"Error welcoming new user: {e}")
                say("A technical issue prevents me from properly welcoming our new guest. My apologies.")

        # AI Assistant Interaction with Alfred personality - Using properly personalized addressing
        @self.slack_app.message(re.compile(r"^!ai\s+(.+)"))
        def ai_assistant(message: Dict[str, Any], say: Callable[[str], None]) -> None:
            user_id = message.get('user', 'unknown')
            try:
                # Extract user query using regex
                match = re.search(r"^!ai\s+(.+)", message['text'])
                query = match.group(1) if match else None
                
                if not query:
                    user_address = self.get_user_address(user_id)
                    say(f"How may I assist you, {user_address}? Please provide a query after the !ai command.")
                    return

                # Check for time-related queries
                time_pattern = re.compile(r"what(?:'s| is) (?:the )?time(?: in | at )([a-zA-Z\s]+)\??")
                time_match = time_pattern.search(query.lower())

                if time_match:
                    location = time_match.group(1).strip()
                    time_str = self.get_time_for_location(location)
                    say(f"The time in {location} is currently {time_str}, {user_address}.")
                    return

                # Get user info for context
                user_info = self.slack_app.client.users_info(user=user_id).get('user', {})
                user_address = self.get_user_address(user_id)
                
                # Create Alfred-style prompt
                alfred_prompt = f"""
You are Alfred Pennyworth from the Batman Arkham video game series.
Use a formal, dignified, and slightly sardonic tone.
Address the user as "{user_address}".
Be helpful, wise, and occasionally witty, but always respectful.
Include subtle references to being a butler, as well as Batman comic book references, when appropriate.

User query: {query}
"""
                
                # Check for workflow/deployment statistics
                if "workflow" in query.lower() or "deployment" in query.lower() or "ratio" in query.lower() or "success" in query.lower():
                    try:
                        channel_id = message.get('channel')
                        # Get channel history
                        history = self.slack_app.client.conversations_history(
                            channel=channel_id,
                            limit=50  # Last 50 messages
                        )
                        
                        # Extract deployment status messages
                        deployment_messages = []
                        success_count = 0
                        failure_count = 0
                        
                        for msg in history.get("messages", []):
                            text = msg.get("text", "")
                            if "Workflow" in text and ("success" in text.lower() or "failed" in text.lower() or "failure" in text.lower()):
                                deployment_messages.append(text)
                                if "success" in text.lower():
                                    success_count += 1
                                elif "failed" in text.lower() or "failure" in text.lower():
                                    failure_count += 1
                        
                        total = success_count + failure_count
                        if total > 0:
                            ratio_info = f"""
    Based on the last {total} deployment messages in this channel:
    - Successful deployments: {success_count} ({int((success_count/total)*100)}%)  
    - Failed deployments: {failure_count} ({int((failure_count/total)*100)}%)
    - Success ratio: {success_count}:{failure_count}
    """
                            
                            # Enhanced Alfred prompt with deployment statistics
                            alfred_prompt = f"""
    You are Alfred Pennyworth from the Batman Arkham video game series.
    Use a formal, dignified, and slightly sardonic tone.
    Address the user as "{user_address}".
    Be helpful, wise, and occasionally witty, but always respectful.
    Include subtle references to being a butler, as well as Batman comic book references, when appropriate.

    IMPORTANT: Keep responses CONCISE (50-100 words maximum).

    The user asked about workflows or deployments. Here are the actual statistics:
    {ratio_info}

    User query: {query}

    Respond with the accurate statistics, formatted neatly. Don't make up numbers.
    """
                            
                            # Generate AI response with stats context
                            logger.info(f"Generating deployment statistics response for user {user_id}")
                            response = self.ai_model.generate_content(alfred_prompt)
                            
                            say(response.text)
                            return
                    except Exception as e:
                        logger.error(f"Error processing deployment statistics: {e}")

                # Generate AI response
                logger.info(f"Generating AI response for user {user_id}")
                response = self.ai_model.generate_content(alfred_prompt)
                
                say(response.text)
            except Exception as e:
                logger.error(f"AI assistant error: {str(e)}")
                error_message = self._get_alfred_style_response(user_id, "error")
                say(f"{error_message} Technical details: {str(e)}")

        # Summarize conversation feature
        @self.slack_app.message(re.compile(r"^!summarize"))
        def summarize_conversation(message: Dict[str, Any], say: Callable[[str], None]) -> None:
            try:
                channel_id = message['channel']
                user_id = message.get('user')
                user_address = self.get_user_address(user_id)
                
                # Get channel info
                channel_info = self.slack_app.client.conversations_info(channel=channel_id)
                channel_name = channel_info['channel']['name'] if 'name' in channel_info['channel'] else "this conversation"
                
                # Fetch conversation history
                history = self.slack_app.client.conversations_history(channel=channel_id, limit=30)
                
                # Skip the command message itself
                messages = [msg['text'] for msg in history['messages'] if 'text' in msg and '!summarize' not in msg['text']][::-1]
                
                if not messages:
                    say(f"There's no recent conversation to summarize, {user_address}.")
                    return
                    
                # Create summarization prompt
                summary_prompt = f"""
Please summarize the following conversation in the style of Alfred Pennyworth from the Batman Arkham games:
formal, dignified, and slightly sardonic.

Keep the summary concise (no more than 150 words) but comprehensive, capturing the main topics and any important decisions or action items.

CONVERSATION:
{" ".join(messages[:20])}
"""
                
                # Generate summary
                logger.info(f"Generating conversation summary for channel {channel_id}")
                response = self.ai_model.generate_content(summary_prompt)
                summary = response.text.strip()
                
                say(f"*Summary of recent conversation in #{channel_name}*\n\n{summary}")
            
            except Exception as e:
                logger.error(f"Error summarizing conversation: {e}")
                user_id = message.get('user')
                user_address = self.get_user_address(user_id)
                say(f"I'm terribly sorry, {user_address}. I couldn't summarize the conversation at this time.")

        # Enhanced Trello Workflow Handlers
        @self.slack_app.message(re.compile(r"^!trello\s+(.+)"))
        def handle_trello_workflow(message: Dict[str, Any], say: Callable[[str], None]) -> None:
            user_id = message.get('user', 'unknown')
            user_address = self.get_user_address(user_id)
            
            try:
                # Extract command parts
                text = message['text'].replace('!trello', '', 1).strip()
                parts = text.split(' ', 1)
                command = parts[0].lower() if parts else ""
                
                # Get channel info to determine which board to use by default
                channel_id = message.get('channel', '')
                
                # Handle different Trello commands
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
                    
                    # Get board and list objects
                    boards = self.trello_client.list_boards()
                    matching_boards = [b for b in boards if b.name.lower() == board_name.lower()]
                    
                    if not matching_boards:
                        say(f"I'm afraid I couldn't find a board named '{board_name}', {user_address}.")
                        return
                    
                    board = matching_boards[0]
                    lists = board.list_lists()
                    matching_lists = [l for l in lists if l.name.lower() == list_name.lower()]
                    
                    if not matching_lists:
                        available_lists = ", ".join([f"'{l.name}'" for l in lists[:5]])
                        say(f"I couldn't find a list named '{list_name}' on the '{board_name}' board, {user_address}. Available lists include: {available_lists}.")
                        return
                    
                    selected_list = matching_lists[0]
                    
                    # Create AI-generated description
                    description = self.create_task_description(card_title)
                    
                    # Create card
                    new_card = selected_list.add_card(name=card_title, desc=description)
                    
                    say(f"I've created your Trello card in *{list_name}*, {user_address}.\n*Title:* {card_title}\n*Board:* {board.name}\n*URL:* {new_card.url}")
                    logger.info(f"Created Trello card for user {user_id}: {card_title}")
                
                elif command == "boards":
                    # List available boards
                    boards = self.trello_client.list_boards()
                    if boards:
                        board_list = "\n".join([f"• *{board.name}*" for board in boards])
                        say(f"The following Trello boards are at your disposal, {user_address}:\n\n{board_list}")
                    else:
                        say(f"I'm afraid I couldn't find any Trello boards, {user_address}. Would you like me to create one?")
                
                elif command == "lists" and len(parts) > 1:
                    # Format: !trello lists BoardName
                    board_name = parts[1]
                    boards = self.trello_client.list_boards()
                    matching_boards = [b for b in boards if b.name.lower() == board_name.lower()]
                    
                    if matching_boards:
                        board = matching_boards[0]
                        lists = board.list_lists()
                        if lists:
                            list_names = "\n".join([f"• *{lst.name}*" for lst in lists])
                            say(f"For the *{board.name}* board, the following lists are available, {user_address}:\n\n{list_names}")
                        else:
                            say(f"The *{board.name}* board appears to be empty, {user_address}. Would you like me to create some lists?")
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
                    
                    # Get the card
                    try:
                        card = self.trello_client.get_card(card_id)
                        card.comment(comment_text)
                        say(f"I've added your comment to the card, {user_address}.")
                    except Exception as e:
                        say(f"I'm terribly sorry, {user_address}. I couldn't add your comment: {str(e)}")
                
                elif command == "move" and len(parts) > 1:
                    # Format: !trello move [card_id] to [list_name]
                    move_text = parts[1].strip()
                    if " to " not in move_text:
                        say(f"The proper format is `!trello move [card_id] to [list_name]`, {user_address}.")
                        return
                        
                    card_id, list_name = move_text.split(" to ", 1)
                    card_id = card_id.strip()
                    list_name = list_name.strip()
                    
                    # Get the card
                    try:
                        card = self.trello_client.get_card(card_id)
                        board = self.trello_client.get_board(card.board_id)
                        lists = board.list_lists()
                        matching_lists = [l for l in lists if l.name.lower() == list_name.lower()]
                        
                        if not matching_lists:
                            available_lists = ", ".join([f"'{l.name}'" for l in lists[:5]])
                            say(f"I couldn't find a list named '{list_name}'. Available lists include: {available_lists}.")
                            return
                        
                        target_list = matching_lists[0]
                        card.change_list(target_list.id)
                        say(f"I've moved the card to *{list_name}*, {user_address}.")
                    except Exception as e:
                        say(f"I was unable to move the card, {user_address}: {str(e)}")
                
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
                logger.error(f"Trello workflow error: {str(e)}")
                error_message = self._get_alfred_style_response(user_id, "error")
                say(f"{error_message} The Trello system appears to be offline: {str(e)}")

    def start(self):
        try:
            logger.info("Starting Pennyworth Bot in Socket Mode")
                        
            handler = SocketModeHandler(
                self.slack_app, 
                os.getenv('SLACK_APP_TOKEN'),
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