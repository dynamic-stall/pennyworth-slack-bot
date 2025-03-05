"""
Trello integration module for Pennyworth Service Bot
Handles Trello board, list, and card operations
"""

import trello
from typing import Optional, List, Dict, Any

class TrelloWorkflow:
    def __init__(self, api_key: str, api_secret: str, token: Optional[str] = None):
        """
        Initialize Trello workflow manager
        
        Args:
            api_key (str): Trello API key
            api_secret (str): Trello API secret
            token (str, optional): Trello token for authenticated operations
        """
        self.client = trello.TrelloClient(
            api_key=api_key,
            api_secret=api_secret,
            token=token
        )
        self._cache = {
            'boards': {},
            'lists': {},
        }
    
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
                
        return None
    
    def create_card(self, board_name: str, list_name: str, 
                    title: str, description: Optional[str] = None, 
                    labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new card in the specified list
        
        Args:
            board_name (str): Name of the board
            list_name (str): Name of the list to add the card to
            title (str): Card title
            description (str, optional): Card description
            labels (list, optional): List of label names to apply
            
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
            
            return {
                'success': True, 
                'card_id': card.id, 
                'card_url': card.url,
                'card_name': card.name
            }
            
        except Exception as e:
            print(f"Error creating Trello card: {e}")
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
            
            return {'success': True, 'message': f"Card moved to {target_list_name}"}
            
        except Exception as e:
            print(f"Error moving Trello card: {e}")
            return {'success': False, 'error': str(e)}