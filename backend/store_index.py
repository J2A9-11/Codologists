from src.function import load_pdf, text_split, download_hugging_face_embeddings
from langchain_pinecone import Pinecone as PC
import pinecone
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

extracted_data = load_pdf(r'E:\Codologists\backend\custom_data')
text_chunks = text_split(extracted_data)
embeddings = download_hugging_face_embeddings()

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY  # Assuming PINECONE_API_KEY is defined

pc = Pinecone(api_key=PINECONE_API_KEY)


index_name = "medical-chatbot"

# Now do stuff
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name='medical-chatbot',
        dimension=384,
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )

#Creating Embeddings for Each of The Text Chunks & storing
docsearch = PC.from_texts( # Use PineconeStore instead of Pinecone
    [t.page_content for t in text_chunks],
    embeddings,
    index_name=index_name,
    # pinecone_index=pc.Index(index_name)
)
