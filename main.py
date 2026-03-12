from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
app = Flask(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не найден в .env файле")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
    return render_template('DUMANGAY.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    try:
        response = model.generate_content(user_message)
        bot_response = response.text
    except Exception as e:
        bot_response = f"Ошибка: {str(e)}"
    
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
