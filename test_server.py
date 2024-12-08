from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class TestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/claim-form':
            self.path = '/test_files/claim_form.html'
        return SimpleHTTPRequestHandler.do_GET(self)

def run_server(port=8000):
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, TestHandler)
    print(f"Starting test server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
