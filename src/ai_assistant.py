"""
AI Assistant module for Pennyworth Service Bot
Handles AI functionality using Google's Gemini API
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any, Callable, List
import logging

class AIAssistant:
    def __init__(self, api_key: str):
        """
        Initialize AI Assistant with Google Gemini
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
        self.model = genai.GenerativeModel(model_name)
        
    def ask(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate AI response for a given query
        
        Args:
            query (str): User's question or command
            context (dict, optional): Additional context for the query
        
        Returns:
            str: AI-generated response
        """
        try:
            # Extract user ID from context if available
            user_address = f"Master <@{context.get('user')}>" if context and 'user' in context else "sir"
            
            # Personality instructions for Alfred Pennyworth
            alfred_instruction = f"""
            Respond as Alfred Pennyworth from the Batman Arkham video game series. 
            Use a formal, dignified, and slightly sardonic tone.
            Address the user as "{user_address}".
            Be helpful, wise, and occasionally witty, but always respectful.
            Include subtle references to being a butler, as well as Batman comic book references, when appropriate.
            IMPORTANT: Keep responses CONCISE and to the point (100 words maximum).
            Focus on answering the question directly first, then add brief characterization.
            """            
            # Add context to the prompt if provided
            if context:
                channel = context.get("channel", "general channel")
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items() if k not in ["user", "channel"]])
                prompt = f"{alfred_instruction}\n\nContext: You are in the #{channel} channel.\n{context_str}\n\nQuery: {query}"
            else:
                prompt = f"{alfred_instruction}\n\nQuery: {query}"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract and return the text
            return response.text
            
        except Exception as e:
            logging.error(f"AI generation error: {e}")
            user_address = f"Master <@{context.get('user')}>" if context and 'user' in context else "sir"
            return f"I'm terribly sorry, {user_address}. I encountered an error while processing your request. Perhaps we should try again when the Bat-Computer is functioning properly."
    
    def create_task_description(self, task_name: str) -> str:
        """
        Generate a detailed task description
        
        Args:
            task_name (str): Short task name or title
        
        Returns:
            str: Generated task description
        """
        prompt = f"""
        Create a comprehensive task description for the following task: "{task_name}"
        Include:
        - What needs to be done
        - Potential first steps
        - Key considerations
        Keep it concise but informative, under 100 words.
        
        Write this description in the style of Alfred Pennyworth from the Batman Arkham video game series:
        formal, dignified, and slightly sardonic. Address the reader as "sir".
        Include subtle butler references if appropriate.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error creating task description: {e}")
            return "No description available, sir. My apologies for the inconvenience. Perhaps this task is best discussed over tea."

    def summarize_conversation(self, context):
        """
        Generate a summary of a conversation.
        
        Args:
            context (dict): Contains channel_name and messages
        
        Returns:
            str: Summary of the conversation
        """
        # Determine if we have a specific user to address
        user_address = "sir"  # Default address
        if 'user' in context:
            user_address = f"Master <@{context['user']}>"
        
        prompt = f"""
        Please summarize this conversation from the Slack channel #{context['channel_name']}:
        
        {context['messages']}
        
        Respond as Alfred Pennyworth from the Batman Arkham video game series.
        Use a formal, dignified, and slightly sardonic tone.
        Address the user as "{user_address}".
        Be helpful, wise, and occasionally witty, but always respectful.
        Provide a concise but comprehensive summary in this butler-like tone.
        Include subtle references to being a butler when appropriate.
        """
        
        # Generate response from Gemini
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logging.error(f"Error generating summary: {e}")
            return f"I'm terribly sorry, {user_address}. I couldn't summarize the conversation at this time. Perhaps the topic was too complex for my humble understanding. Shall I prepare some tea while you review it yourself?"

    def get_contextual_response(self, query: str, user_address: str, 
                            thread_context: Optional[List[str]] = None, 
                            workflow_stats: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response with additional context awareness
        
        Args:
            query (str): User's question or command
            user_address (str): How to address the user
            thread_context (List[str], optional): Messages from a thread
            workflow_stats (Dict, optional): Statistics about workflows/deployments
            
        Returns:
            str: AI-generated response
        """
        try:
            # Base Alfred prompt with brevity instruction
            alfred_prompt = f"""
    You are Alfred Pennyworth from the Batman Arkham video game series.
    Use a formal, dignified, and slightly sardonic tone.
    Address the user as "{user_address}".
    Be helpful, wise, and occasionally witty, but always respectful.
    Include subtle references to being a butler when appropriate.

    IMPORTANT: Keep responses CONCISE (50-100 words maximum).
    Focus on answering the question directly first, then add brief characterization.
    """

            # Add thread context if provided
            if thread_context and len(thread_context) > 0:
                alfred_prompt += f"""
    You're replying in a thread conversation. Here's the recent conversation:
    {chr(10).join(thread_context[-8:])}

    The user specifically asked: "{query}"

    If you're being asked about information in the thread, reference it directly.
    Always respond politely, as if joining an ongoing conversation.
    """
            # Add workflow statistics if provided
            elif workflow_stats:
                alfred_prompt += f"""
    The user asked about workflows or deployments. Here are the actual statistics:
    {workflow_stats['ratio_info']}

    User query: {query}

    Respond with the accurate statistics, formatted neatly. Don't make up numbers.
    """
            else:
                alfred_prompt += f"""
    User query: {query}
    """
            
            # Generate response
            response = self.model.generate_content(alfred_prompt)
            return response.text
            
        except Exception as e:
            logging.error(f"AI generation error: {e}")
            return f"I'm terribly sorry, {user_address}. I encountered an error while processing your request. Perhaps we should try again when the Bat-Computer is functioning properly."

    def get_time_response(self, location: str, time_str: str, user_address: str) -> str:
        """
        Generate a response about the time in a location
        
        Args:
            location (str): The location name
            time_str (str): The formatted time string
            user_address (str): How to address the user
        
        Returns:
            str: AI-generated response about the time
        """
        prompt = f"""
    You are Alfred Pennyworth from Batman.
    The time in {location} is currently {time_str}.
    Create a very brief, butler-like response telling {user_address} the time.
    Keep it under 25 words, formal but slightly witty.
    """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Error generating time response: {e}")
            return f"The time in {location} is currently {time_str}, {user_address}."