from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import google.genai as genai

load_dotenv()
app = Flask(__name__)

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY не найден в .env файле")

client = genai.Client(api_key=GEMINI_API_KEY)

@app.route('/')
def index():
    return render_template('DUMANGAY.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json or {}
    user_message = data.get('message', '')

    def _parse_quota_error(err: genai.errors.ClientError) -> str:
        # Try to extract the retry delay and a user-friendly message from the API error.
        try:
            payload = getattr(err, 'response_json', {}) or {}
            details = payload.get('error', {}).get('details', []) or []
            retry_info = next(
                (d.get('retryDelay') for d in details if d.get('@type', '').endswith('RetryInfo')),
                None,
            )
            if retry_info:
                return f"Квота исчерпана. Повторите через {retry_info}."
        except Exception:
            pass
        return "Ошибка квоты (RESOURCE_EXHAUSTED). Проверьте план/биллинг или используйте другой ключ/проект."

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=user_message,
        )
    except genai.errors.ClientError as e:
        if getattr(e, 'status_code', None) == 429:
            # Если квота кончилась — пробуем менее “тяжёлую” модель.
            try:
                response = client.models.generate_content(
                    model="models/gemini-flash-latest",
                    contents=user_message,
                )
            except genai.errors.ClientError as e2:
                bot_response = _parse_quota_error(e2)
                return jsonify({'response': bot_response})
        else:
            bot_response = f"Ошибка: {str(e)}"
            return jsonify({'response': bot_response})

    try:
        candidate = (response.candidates or [None])[0]
        bot_response = ''
        if candidate and candidate.content and candidate.content.parts:
            bot_response = candidate.content.parts[0].text or ''
    except Exception as e:
        bot_response = f"Ошибка: {str(e)}"

    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
