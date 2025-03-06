import os
import threading
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from main import start_bot

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        
    def log_message(self, format, *args):
        # Override to use our logger
        logger.info("%s - %s" % (self.address_string(), format % args))

def run_server():
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logger.info(f"Starting health check server on port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Start the bot in a separate thread
    logger.info("Starting bot thread")
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run the HTTP server in the main thread
    logger.info("Starting HTTP server")
    run_server()