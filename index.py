import os
from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_split_splitters import RecursiveCharacterTextSplitter
from groq import Groq

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# No necesitas load_dotenv() en Vercel si configuras las variables en su panel
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PDF_NAME = "mundiales.pdf"

# Crear el cliente de Groq una sola vez
client = Groq(api_key=GROQ_API_KEY)

# --- LÓGICA DE DOCUMENTOS (RAG) ---
# Nota: En Vercel, el PDF debe estar en la raíz o junto a este archivo
try:
    loader = PyPDFLoader(PDF_NAME)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(pages)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()
except Exception as e:
    print(f"Error cargando el PDF: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")
        
        # 1. Buscar contexto en el PDF
        context_docs = retriever.get_relevant_documents(user_message)
        context_text = "\n".join([doc.page_content for doc in context_docs])
        
        # 2. Consultar a Groq
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"Eres un experto en mundiales. Usa este contexto: {context_text}"},
                {"role": "user", "content": user_message},
            ],
            model="llama3-8b-8192",
        )
        
        return jsonify({"response": response.choices[0].message.content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# IMPORTANTE: No pongas app.run() aquí para Vercel