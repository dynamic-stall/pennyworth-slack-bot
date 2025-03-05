import os
from typing import Optional, Dict, Any
import bitwarden_sdk

class BitwardenSecretManager:
    def __init__(
        self, 
        organization_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """
        Initialize Bitwarden Secret Manager with flexible authentication
        
        Args:
            organization_id (str, optional): Bitwarden organization ID
            client_id (str, optional): Client credentials ID
            client_secret (str, optional): Client credentials secret
            access_token (str, optional): BWS access token
            project_id (str, optional): Specific project ID for secrets
        """
        self.organization_id = organization_id or os.getenv('BITWARDEN_ORGANIZATION_ID')
        self.project_id = project_id or os.getenv('BITWARDEN_PROJECT_ID')
        self.client = bitwarden_sdk.Client()
        
        # Authentication priority
        self._authenticate(
            client_id or os.getenv('BITWARDEN_CLIENT_ID'),
            client_secret or os.getenv('BITWARDEN_CLIENT_SECRET'),
            access_token or os.getenv('BITWARDEN_ACCESS_TOKEN')
        )

    def _authenticate(
        self, 
        client_id: Optional[str] = None, 
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None
    ):
        """
        Authenticate with Bitwarden using multiple methods
        
        Tries methods in order:
        1. Access Token
        2. Client Credentials
        3. Interactive Login
        """
        try:
            # Attempt authentication with access token
            if access_token:
                try:
                    self.client.login_with_access_token(access_token)
                    print("Authenticated using access token")
                    return
                except Exception as token_error:
                    print(f"Access token authentication failed: {token_error}")
            
            # Try client credentials
            if client_id and client_secret:
                try:
                    self.client.login_with_client_credentials(
                        client_id=client_id, 
                        client_secret=client_secret
                    )
                    print("Authenticated using client credentials")
                    return
                except Exception as cred_error:
                    print(f"Client credentials authentication failed: {cred_error}")
            
            # Fallback to interactive login
            print("Falling back to interactive login")
            self.client.login_interactive()
        
        except Exception as e:
            print(f"Bitwarden authentication failed completely: {e}")
            raise RuntimeError("Unable to authenticate with Bitwarden")

    def get_secrets(self, secret_names: list) -> Dict[str, Any]:
        """
        Retrieve multiple secrets by name
        
        Args:
            secret_names (list): List of secret names to retrieve
        
        Returns:
            Dict with secret names and their values
        """
        secrets_dict = {}
        
        try:
            # List available secrets
            all_secrets = self.client.list_secrets(
                organization_id=self.organization_id,
                project_id=self.project_id
            )
            
            # Match and collect requested secrets
            for secret in all_secrets:
                if secret.name in secret_names:
                    secrets_dict[secret.name] = secret.value
            
            # Check if all requested secrets were found
            missing_secrets = set(secret_names) - set(secrets_dict.keys())
            if missing_secrets:
                print(f"Warning: Missing secrets: {missing_secrets}")
        
        except Exception as e:
            print(f"Error retrieving secrets: {e}")
        
        return secrets_dict

    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve a single secret by name
        
        Args:
            secret_name (str): Name of the secret to retrieve
        
        Returns:
            str or None: Secret value or None if not found
        """
        secrets = self.get_secrets([secret_name])
        return secrets.get(secret_name)

# Example Usage in Main Application
def initialize_pennyworth_bot():
    try:
        # Initialize Secret Manager
        secret_manager = BitwardenSecretManager()
        
        # Retrieve multiple secrets at once
        required_secrets = [
            'SLACK_BOT_TOKEN', 
            'SLACK_APP_TOKEN', 
            'GOOGLE_GEMINI_API_KEY',
            'TRELLO_API_KEY'
        ]
        
        secrets = secret_manager.get_secrets(required_secrets)
        
        # Use secrets in bot initialization
        slack_bot = SlackBot(
            bot_token=secrets.get('SLACK_BOT_TOKEN'),
            app_token=secrets.get('SLACK_APP_TOKEN')
        )
        
        # Optional: Individual secret retrieval
        gemini_key = secret_manager.get_secret('GOOGLE_GEMINI_API_KEY')
        
        return slack_bot, secrets
    
    except Exception as e:
        print(f"Bot initialization failed: {e}")
        return None, None

# Logging and Error Handling Decorator
def bitwarden_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except bitwarden_sdk.Error as bw_error:
            print(f"Bitwarden SDK Error: {bw_error}")
            # Optionally log to file or send alert
        except Exception as e:
            print(f"Unexpected error: {e}")
    return wrapper