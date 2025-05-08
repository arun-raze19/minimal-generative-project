from flask import Flask, render_template, request, jsonify, session
from model import SimpleLLM
import os

app = Flask(__name__)
app.secret_key = 'minimal_llm_secret_key'  # For session management

# Initialize the LLM with the sample corpus
llm = SimpleLLM(os.path.join('data', 'sample_text.txt'))

@app.route('/')
def index():
    """Render the main page"""
    # Initialize chat history if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []

    return render_template('index.html', chat_history=session['chat_history'])

@app.route('/ask', methods=['POST'])
def ask():
    """Process a user question and generate a response"""
    try:
        # Get the question from the request
        question = request.form.get('question', '')

        if not question.strip():
            return jsonify({
                'status': 'error',
                'message': 'Please enter a question'
            }), 400

        # Generate a response
        response = llm.generate_response(question)

        # Update chat history
        if 'chat_history' not in session:
            session['chat_history'] = []

        session['chat_history'].append({
            'question': question,
            'response': response
        })

        # Limit chat history to last 10 exchanges
        if len(session['chat_history']) > 10:
            session['chat_history'] = session['chat_history'][-10:]

        session.modified = True

        return jsonify({
            'status': 'success',
            'response': response,
            'chat_history': session['chat_history']
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

@app.route('/clear_history', methods=['POST'])
def clear_history():
    """Clear the chat history"""
    session['chat_history'] = []
    session.modified = True

    return jsonify({
        'status': 'success',
        'message': 'Chat history cleared'
    })

@app.route('/upload', methods=['POST'])
def upload_corpus():
    """Upload a new corpus file"""
    if 'corpus' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'No file part'
        }), 400

    file = request.files['corpus']

    if file.filename == '':
        return jsonify({
            'status': 'error',
            'message': 'No selected file'
        }), 400

    if file:
        # Save the file
        file_path = os.path.join('data', 'user_corpus.txt')
        file.save(file_path)

        # Load the new corpus
        success = llm.load_corpus(file_path)

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Corpus uploaded and loaded successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to load the corpus'
            }), 500

if __name__ == '__main__':
    app.run(debug=True)
