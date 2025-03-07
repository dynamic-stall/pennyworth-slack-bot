"""
Pennyworth Slack Bot - Cloud Run HTTP Server Wrapper
"""
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Import the PennyworthBot class
from src.bot import PennyworthBot

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP Handler for Cloud Run health checks"""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Health check OK')
    
    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format % args))

def run_server():
    """Run the HTTP server for Cloud Run"""
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    
    logger.info(f"Starting HTTP server on port {port}")
    
    try:
        httpd = HTTPServer(server_address, HealthCheckHandler)
        logger.info(f"HTTP server started successfully")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting HTTP server: {e}")
        raise

def start_bot():
    """Start the PennyworthBot instance"""
    try:
        bot = PennyworthBot()
        bot.start()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise

if __name__ == "__main__":
    # Start bot in background thread
    logger.info("Starting Pennyworth bot in background thread")
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run HTTP server in main thread
    logger.info("Starting HTTP server for health checks")
    run_server()