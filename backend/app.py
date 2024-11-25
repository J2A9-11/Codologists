from flask import Flask, render_template, jsonify, request
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

app = Flask(__name__)

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

embeddings = download_hugging_face_embeddings()

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY  # Assuming PINECONE_API_KEY is defined
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medical-chatbot"

docsearch=PC.from_existing_index(index_name, embeddings)

PROMPT=PromptTemplate(template=prompt_template, input_variables=["context", "question"])
chain_type_kwargs={"prompt": PROMPT}

<<<<<<< Updated upstream
=======
llm = CTransformers(
    model=r"model\llama-2-7b-chat.ggmlv3.q4_0.bin",
    model_type="llama",
    config={'max_new_tokens': 2000, 'temperature': 0.4, 'context_length':800}
)
>>>>>>> Stashed changes

llm=CTransformers(model=r"E:\Codologists\backend\model\llama-2-7b-chat.ggmlv3.q4_0.bin",
                  model_type="llama",
                  config={'max_new_tokens':512,
                          'temperature':0.8})

qa=RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type="stuff", 
    retriever=docsearch.as_retriever(search_kwargs={'k': 2}),
    return_source_documents=True, 
    chain_type_kwargs=chain_type_kwargs)


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    result=qa({"query": input})
    print("Response : ", result["result"])
    return str(result["result"])


if __name__ == '__main__':
    app.run(debug= True)

