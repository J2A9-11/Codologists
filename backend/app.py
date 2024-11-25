<<<<<<< Updated upstream
from flask import Flask, render_template, session, redirect, url_for
from flask_session import Session
from flask_socketio import SocketIO
from auth import auth_bp  # Import the Blueprint for auth
from chat import chat_bp, socketio  # Import the Blueprint for chat and SocketIO
import os

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
=======
import warnings
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.function import download_hugging_face_embeddings
from langchain_pinecone import Pinecone as PC
import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from src.prompt import *
import os

# Import the auth blueprint
from auth import auth_bp

warnings.filterwarnings("ignore")

app = Flask(
    __name__,
    template_folder="../frontend/templates",  # Path to templates
    static_folder="../frontend/static"        # Path to static files
)

# Set secret key for session management (make sure it's unique and secret)
app.secret_key = os.urandom(24)

CORS(app)  # Enable CORS for all routes

# Register the auth blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')
>>>>>>> Stashed changes

# Set secret key for session management
app.secret_key = os.urandom(24)

# Register the auth Blueprint for login, signup, etc.
app.register_blueprint(auth_bp)

# Register the chat Blueprint for the chat functionality
app.register_blueprint(chat_bp)

# Flask session configuration
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

<<<<<<< Updated upstream
# Initialize SocketIO with the app
socketio.init_app(app)

# Route for home page (the one that was already defined)
@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('auth.login'))

# Default route for the root URL
@app.route('/')
def index():
    # Redirect to /home by default when visiting the root URL
    return redirect(url_for('home'))

# Start the Flask app and run SocketIO with it
if __name__ == "__main__":
    socketio.run(app, debug=True)
=======
docsearch = PC.from_existing_index(index_name, embeddings)

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
chain_type_kwargs = {"prompt": PROMPT}

llm = CTransformers(
    model=r"model\llama-2-7b-chat.ggmlv3.q4_0.bin",
    model_type="llama",
    config={'max_new_tokens': 512, 'temperature': 0.8}
)

qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=docsearch.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True, 
    chain_type_kwargs=chain_type_kwargs
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chatroom')
def chatroom():
    return render_template('chatroom.html')


@app.route("/get", methods=["POST"])
def chat():
    # Get the JSON data from the request
    data = request.get_json()
    msg = data.get("msg", "")
    
    if not msg:
        return jsonify({"error": "No message provided"}), 400

    input = msg
    print(f"User input: {input}")

    # Perform the query using the RetrievalQA chain
    result = qa({"query": input})

    # Print the result for debugging
    print(f"Response: {result['result']}")

    return jsonify({"response": result["result"]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Ensure Flask runs on port 5000
>>>>>>> Stashed changes
