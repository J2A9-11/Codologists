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

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

embeddings = download_hugging_face_embeddings()

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY  # Assuming PINECONE_API_KEY is defined
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medical-chatbot"

docsearch = PC.from_existing_index(index_name, embeddings)

llm = CTransformers(
    model=r"model\llama-2-7b-chat.ggmlv3.q4_0.bin",
    model_type="llama",
    config={'max_new_tokens': 2000, 'temperature': 0.4, 'context_length':800}
)

PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
chain_type_kwargs = {"prompt": PROMPT}

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
