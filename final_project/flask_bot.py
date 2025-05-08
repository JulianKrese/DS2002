from flask import Flask, render_template, request, session
from flask import redirect, url_for
import requests
import re

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Required for session support


# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Debug route
@app.route('/debug')
def debug():
    return "This is the debug route. Everything's (hopefully) fine."


# Chat route
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'history' not in session:
        session['history'] = []

    if request.method == 'POST':
        user_message = request.form['message']

        # Call the bot backend
        bot_reply = ""
        
        try:
            print("calling chat bot")

        except Exception as e: 
            bot_reply = f"Error: {e}"

        # Append to chat history
        session['history'].append({'user': user_message, 'bot': bot_reply})
        session.modified = True
        return redirect(url_for('chat'))

    return render_template('chat.html', history=session.get('history', []))


# Clear chat history
@app.route('/clear')
def clear():
    session.pop('history', None)
    return redirect(url_for('chat'))


# Run app
if __name__ == '__main__':
    app.run(debug=True)