"""
AI Assistant module for Pennyworth Service Bot
Handles AI functionality using Google's Gemini API
"""

import os
import google.generativeai as genai
from typing import Optional, Dict, Any
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
            
            # Alfred Pennyworth personality instructions
            alfred_instruction = f"""
            Respond as Alfred Pennyworth from the Batman Arkham video game series. 
            Use a formal, dignified, and slightly sardonic tone.
            Address the user as "{user_address}".
            Be helpful, wise, and occasionally witty, but always respectful.
            Include subtle references to being a butler when appropriate.
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