"""
Pennyworth Slack Bot - Entry Point
"""
import os
import logging
from dotenv import load_dotenv

from src.bot import PennyworthBot

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    """Main function to start the bot"""
    logger.info("Starting Pennyworth Bot from main.py")
    bot = PennyworthBot()
    bot.start()

if __name__ == "__main__":
    main()