from flask import Flask, request, jsonify
from main import run_agent  # Assuming run_agent is the function you want to expose

app = Flask(__name__)

@app.route('/weather', methods=['POST'])
def get_weather():
    data = request.json
    question = data.get('question', '')
    answer = run_agent(question)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)