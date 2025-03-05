"""
AI Assistant module for Pennyworth Service Bot
Handles AI functionality using Google's Gemini API
"""

import google.generativeai as genai
from typing import Optional, Dict, Any

class AIAssistant:
    def __init__(self, api_key: str):
        """
        Initialize AI Assistant with Google Gemini
        
        Args:
            api_key (str): Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
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
            # Add context to the prompt if provided
            prompt = query
            if context:
                context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
                prompt = f"{context_str}\n\nQuery: {query}"
            
            # Generate response
            response = self.model.generate_content(prompt)
            
            # Extract and return the text
            return response.text
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"
    
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
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "No description available."