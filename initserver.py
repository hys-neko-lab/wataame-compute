import http.server
import socketserver
import shutil
import os

def run():
    tmp='www'
    cwd=os.getcwd()
    os.makedirs(tmp, exist_ok=True)
    os.chdir(tmp)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("",3003), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            os.chdir(cwd)
            shutil.rmtree('www')

if __name__ == '__main__':
    run()