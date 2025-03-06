import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Health check OK')
    
    def log_message(self, format, *args):
        logger.info("%s - %s" % (self.address_string(), format % args))

def run_server():
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8080))
    server_address = ('', port)
    
    logger.info(f"Starting server on port {port}")
    
    try:
        httpd = HTTPServer(server_address, HealthCheckHandler)
        logger.info(f"Server started successfully")
        httpd.serve_forever()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    # Start with very basic functionality - just the HTTP server
    print(f"DEBUGGING: Starting simple HTTP server")
    run_server()