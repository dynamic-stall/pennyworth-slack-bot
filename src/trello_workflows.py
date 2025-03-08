"""
Trello integration module for Pennyworth Service Bot
Handles Trello board, list, and card operations
"""

import logging
import trello
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class TrelloWorkflow:
    def __init__(self, api_key: str = None, api_secret: str = None, token: Optional[str] = None, 
                trello_client: Any = None, ai_generator: Any = None):
        """
        Initialize Trello workflow manager
        
        Args:
            api_key (str): Trello API key
            api_secret (str): Trello API secret
            token (str, optional): Trello token for authenticated operations
            trello_client (Any, optional): Existing Trello client
            ai_generator (Any, optional): Function for generating task descriptions
        """
        if trello_client:
            self.client = trello_client
        else:
            self.client = trello.TrelloClient(
                api_key=api_key,
                api_secret=api_secret,
                token=token
            )
        self.ai_generator = ai_generator
        self._cache = {
            'boards': {},
            'lists': {},
        }
        # Channel mapping (board_id -> slack_channel_id)
        self.channel_mapping = {}
        
        logger.info("Trello workflow manager initialized")

    def get_board(self, board_name: str) -> Optional[trello.Board]:
        """
        Get a board by name
        
        Args:
            board_name (str): Name of the board to find
        
        Returns:
            Board object or None if not found
        """
        # Return from cache if available
        if board_name in self._cache['boards']:
            return self._cache['boards'][board_name]
            
        # Otherwise, fetch from API
        all_boards = self.client.list_boards()
        for board in all_boards:
            if board.name.lower() == board_name.lower():
                self._cache['boards'][board_name] = board
                return board
        
        logger.warning(f"Board not found: {board_name}")
        return None
    
    def get_list(self, board_name: str, list_name: str) -> Optional[trello.List]:
        """
        Get a list from a specific board
        
        Args:
            board_name (str): Name of the parent board
            list_name (str): Name of the list to find
        
        Returns:
            List object or None if not found
        """
        cache_key = f"{board_name}:{list_name}"
        if cache_key in self._cache['lists']:
            return self._cache['lists'][cache_key]
            
        board = self.get_board(board_name)
        if not board:
            return None
            
        for lst in board.list_lists():
            if lst.name.lower() == list_name.lower():
                self._cache['lists'][cache_key] = lst
                return lst
        
        logger.warning(f"List not found: {list_name} on board {board_name}")        
        return None
    
    def create_card(self, board_name: str, list_name: str, 
                    title: str, description: Optional[str] = None, 
                    labels: Optional[List[str]] = None, 
                    due_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new card in the specified list
        
        Args:
            board_name (str): Name of the board
            list_name (str): Name of the list to add the card to
            title (str): Card title
            description (str, optional): Card description
            labels (list, optional): List of label names to apply
            due_date (str, optional): Due date in format YYYY-MM-DD
            
        Returns:
            Dict with card details or error info
        """
        try:
            trello_list = self.get_list(board_name, list_name)
            if not trello_list:
                return {'success': False, 'error': f"List '{list_name}' not found on board '{board_name}'"}
            
            # Create the card
            card = trello_list.add_card(name=title, desc=description or "")
            
            # Add labels if provided
            if labels and card:
                board = self.get_board(board_name)
                available_labels = board.get_labels()
                
                for label_name in labels:
                    for label in available_labels:
                        if label.name.lower() == label_name.lower():
                            card.add_label(label)
            
            # Set due date if provided
            if due_date and card:
                try:
                    # Convert string to datetime
                    due_datetime = datetime.strptime(due_date, "%Y-%m-%d")
                    card.set_due(due_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z"))
                except ValueError:
                    logger.warning(f"Invalid due date format: {due_date}, expected YYYY-MM-DD")
            
            logger.info(f"Created card: '{title}' on board '{board_name}' in list '{list_name}'")
            return {
                'success': True, 
                'card_id': card.id, 
                'card_url': card.url,
                'card_name': card.name
            }
            
        except Exception as e:
            logger.error(f"Error creating Trello card: {e}")
            return {'success': False, 'error': str(e)}
    
    def move_card(self, card_id: str, target_list_name: str) -> Dict[str, Any]:
        """
        Move a card to a different list
        
        Args:
            card_id (str): ID of the card to move
            target_list_name (str): Name of the destination list
            
        Returns:
            Dict with operation status
        """
        try:
            card = self.client.get_card(card_id)
            if not card:
                return {'success': False, 'error': f"Card with ID '{card_id}' not found"}
            
            # Get the board
            board = self.client.get_board(card.board_id)
            
            # Find the target list
            target_list = None
            for lst in board.list_lists():
                if lst.name.lower() == target_list_name.lower():
                    target_list = lst
                    break
            
            if not target_list:
                return {'success': False, 'error': f"List '{target_list_name}' not found"}
            
            # Move the card
            card.change_list(target_list.id)
            
            logger.info(f"Moved card {card.name} to list {target_list_name}")
            return {'success': True, 'message': f"Card moved to {target_list_name}"}
            
        except Exception as e:
            logger.error(f"Error moving Trello card: {e}")
            return {'success': False, 'error': str(e)}

    def create_board(self, board_name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Trello board
        
        Args:
            board_name (str): Name for the new board
            description (str, optional): Board description
            
        Returns:
            Dict with operation status and board details
        """
        try:
            # Create new board
            new_board = self.client.add_board(board_name, desc=description or "")
            
            # Cache the new board
            self._cache['boards'][board_name] = new_board
            
            logger.info(f"Created new board: {board_name}")
            return {
                'success': True,
                'board_id': new_board.id,
                'board_name': new_board.name,
                'board_url': f"https://trello.com/b/{new_board.id}"  # Construct URL
            }
            
        except Exception as e:
            logger.error(f"Error creating Trello board: {e}")
            return {'success': False, 'error': str(e)}

    def create_list(self, board_name: str, list_name: str) -> Dict[str, Any]:
        """
        Create a new list on a board
        
        Args:
            board_name (str): Name of the board
            list_name (str): Name for the new list
            
        Returns:
            Dict with operation status
        """
        try:
            board = self.get_board(board_name)
            if not board:
                return {'success': False, 'error': f"Board '{board_name}' not found"}
            
            # Create the list
            new_list = board.add_list(list_name)
            
            # Update cache
            cache_key = f"{board_name}:{list_name}"
            self._cache['lists'][cache_key] = new_list
            
            logger.info(f"Created new list '{list_name}' on board '{board_name}'")
            return {'success': True, 'list_name': list_name}
            
        except Exception as e:
            logger.error(f"Error creating Trello list: {e}")
            return {'success': False, 'error': str(e)}

    def add_comment(self, card_id: str, comment: str) -> Dict[str, Any]:
        """
        Add a comment to a card
        
        Args:
            card_id (str): ID of the card
            comment (str): Comment text
            
        Returns:
            Dict with operation status
        """
        try:
            card = self.client.get_card(card_id)
            if not card:
                return {'success': False, 'error': f"Card with ID '{card_id}' not found"}
            
            card.comment(comment)
            
            logger.info(f"Added comment to card {card.name}")
            return {'success': True, 'message': "Comment added"}
            
        except Exception as e:
            logger.error(f"Error adding comment to Trello card: {e}")
            return {'success': False, 'error': str(e)}

    def archive_card(self, card_id: str) -> Dict[str, Any]:
        """
        Archive a card
        
        Args:
            card_id (str): ID of the card to archive
            
        Returns:
            Dict with operation status
        """
        try:
            card = self.client.get_card(card_id)
            if not card:
                return {'success': False, 'error': f"Card with ID '{card_id}' not found"}
            
            card.set_closed(True)
            
            logger.info(f"Archived card {card.name}")
            return {'success': True, 'message': "Card archived"}
            
        except Exception as e:
            logger.error(f"Error archiving Trello card: {e}")
            return {'success': False, 'error': str(e)}

    def map_board_to_channel(self, board_name: str, channel_id: str) -> Dict[str, Any]:
        """
        Link a Trello board to a Slack channel for notifications
        
        Args:
            board_name (str): Name of the Trello board
            channel_id (str): ID of the Slack channel
            
        Returns:
            Dict with operation status
        """
        try:
            board = self.get_board(board_name)
            if not board:
                return {'success': False, 'error': f"Board '{board_name}' not found"}
            
            self.channel_mapping[board.id] = channel_id
            
            logger.info(f"Mapped board '{board_name}' to Slack channel {channel_id}")
            return {'success': True, 'message': f"Board '{board_name}' now linked to channel"}
            
        except Exception as e:
            logger.error(f"Error mapping board to channel: {e}")
            return {'success': False, 'error': str(e)}

    def get_upcoming_due_cards(self, days_ahead: int = 2) -> List[Dict[str, Any]]:
        """
        Get cards with due dates within the specified number of days
        
        Args:
            days_ahead (int): Number of days ahead to check
            
        Returns:
            List of dictionaries with card details
        """
        upcoming_cards = []
        today = datetime.now()
        threshold = today + timedelta(days=days_ahead)
        
        try:
            # Get all boards
            boards = self.client.list_boards()
            
            for board in boards:
                board_name = board.name
                
                # Check if this board is mapped to a channel
                channel_id = self.channel_mapping.get(board.id)
                
                # Get all cards on the board
                for lst in board.list_lists():
                    for card in lst.list_cards():
                        # Check if card has a due date
                        if card.due_date:
                            # Convert due date string to datetime
                            try:
                                due_date = datetime.strptime(card.due_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                                
                                # Check if due date is within the threshold
                                if today <= due_date <= threshold:
                                    upcoming_cards.append({
                                        'card_id': card.id,
                                        'card_name': card.name,
                                        'card_url': card.url,
                                        'due_date': card.due_date,
                                        'board_name': board_name,
                                        'list_name': lst.name,
                                        'channel_id': channel_id
                                    })
                            except ValueError:
                                logger.warning(f"Invalid due date format for card {card.name}: {card.due_date}")
            
            logger.info(f"Found {len(upcoming_cards)} cards due in the next {days_ahead} days")
            return upcoming_cards
            
        except Exception as e:
            logger.error(f"Error checking for upcoming due cards: {e}")
            return []

    def get_boards(self) -> Dict[str, Any]:
        """
        Get all available Trello boards
        
        Returns:
            Dict with boards list and status
        """
        try:
            boards = self.client.list_boards()
            return {
                "success": True,
                "boards": [{"name": b.name, "id": b.id} for b in boards]
            }
        except Exception as e:
            logger.error(f"Error retrieving Trello boards: {str(e)}")
            return {"success": False, "error": str(e)}
            
    def get_lists(self, board_name: str) -> Dict[str, Any]:
        """
        Get all lists for a given board
        
        Args:
            board_name: Name of the board
            
        Returns:
            Dict with lists and status
        """
        try:
            board = self.get_board(board_name)
            if not board:
                return {
                    "success": False,
                    "error": f"Board '{board_name}' not found"
                }
                
            lists = board.list_lists()
            
            return {
                "success": True,
                "board_name": board.name,
                "lists": [{"name": lst.name, "id": lst.id} for lst in lists]
            }
        except Exception as e:
            logger.error(f"Error retrieving lists for board '{board_name}': {str(e)}")
            return {"success": False, "error": str(e)}

    def parse_command(self, command_text: str) -> tuple:
        """
        Parse a Trello command string
        
        Args:
            command_text: Full command text (without !trello prefix)
            
        Returns:
            Tuple of command name and parsed arguments
        """
        parts = command_text.strip().split(' ', 1)
        command = parts[0].lower() if parts else ""
        args = {}
        
        if len(parts) > 1:
            remainder = parts[1].strip()
            
            if command == "create":
                # Format: create Card Title in List Name
                if " in " in remainder:
                    card_title, list_name = remainder.split(" in ", 1)
                    args["card_title"] = card_title.strip()
                    args["list_name"] = list_name.strip()
                else:
                    args["card_title"] = remainder
                    args["list_name"] = "To Do"  # Default
            
            elif command == "lists":
                # Format: lists Board Name
                args["board_name"] = remainder
            
            elif command == "comment":
                # Format: comment card_id Comment text
                comment_parts = remainder.split(' ', 1)
                if len(comment_parts) >= 2:
                    args["card_id"] = comment_parts[0].strip()
                    args["comment_text"] = comment_parts[1].strip()
                    
            elif command == "move":
                # Format: move card_id to List Name
                if " to " in remainder:
                    card_id, list_name = remainder.split(" to ", 1)
                    args["card_id"] = card_id.strip()
                    args["list_name"] = list_name.strip()
        
        return command, args