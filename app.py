import os                             # <--- ESTA LÍNEA ES VITAL
from dotenv import load_dotenv        
from flask import Flask, render_template, request, jsonify
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from groq import Groq

# Cargar las variables del archivo .env
load_dotenv()

app = Flask(__name__)

# CONFIGURACIÓN
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PDF_NAME = "mundiales.pdf"

# Crear el cliente de Groq una sola vez
client = Groq(api_key=GROQ_API_KEY)

app = Flask(__name__)

# --- CONFIGURACIÓN ---
app = Flask(__name__)

# Ahora traemos la llave de forma segura
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) 
PDF_NAME = "mundiales.pdf"       # <--- YA PUSE EL NOMBRE QUE VI EN TU FOTO
# ---------------------

client = Groq(api_key=GROQ_API_KEY)

try:
    print("--- Cargando PDF y Modelos (Esto puede tardar un poco) ---")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    loader = PyPDFLoader(PDF_NAME)
    pages = loader.load_and_split()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(pages)
    vectorstore = Chroma.from_documents(documents=docs, embedding=embeddings)
    print("--- ¡Todo listo! Servidor iniciado correctamente ---")
except Exception as e:
    print(f"ERROR AL INICIAR: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get("message")
        # Buscar contexto
        docs = vectorstore.similarity_search(user_input, k=3)
        contexto = "\n".join([d.page_content for d in docs])
        
        # Llamada a Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Responde usando solo la información del PDF proporcionado."},
                {"role": "user", "content": f"Contexto: {contexto}\n\nPregunta: {user_input}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return jsonify({"response": chat_completion.choices[0].message.content})
    except Exception as e:
        print(f"ERROR EN EL CHAT: {e}") # <--- ESTO APARECERÁ EN TU TERMINAL
        return jsonify({"response": f"Ocurrió un error interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)