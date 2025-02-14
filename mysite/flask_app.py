from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    os.chdir('/home/p23')
    os.system('git fetch origin && git reset --hard origin/main')
    os.system('touch /var/www/p23_pythonanywhere_com_wsgi.py')
    return 'Updated PythonAnywhere successfully'

if __name__ == '__main__':
    app.run()

