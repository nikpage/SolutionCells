from flask import Flask, request, abort
import os
import hmac
import hashlib

app = Flask(__name__)

# Get webhook secret from environment variable
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', '')

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    # Verify webhook signature for POST requests
    if request.method == 'POST':
        signature = request.headers.get('X-Hub-Signature-256')
        if not signature:
            abort(400, 'No signature header')
            
        # Calculate expected signature
        body = request.get_data()
        expected = 'sha256=' + hmac.new(
            WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected):
            abort(401, 'Invalid signature')

    # If verification passes or it's a GET request, proceed with git update
    os.chdir('/home/p23')
    os.system('git fetch origin && git reset --hard origin/master')
    os.system('touch /var/www/p23_pythonanywhere_com_wsgi.py')
    return 'Updated PythonAnywhere successfully'

if __name__ == '__main__':
    app.run()

