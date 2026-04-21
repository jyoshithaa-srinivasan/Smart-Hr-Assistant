import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.utils import secure_filename
from utils.file_utils import allowed_file, save_and_index_file
from prepare_data import build_vectorstore_if_missing
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from llama_cpp import Llama


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'super-secret-key')

# --- Auth setup (very simple in-memory example) ---
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# simple in-memory user store (replace with DB in production)
USERS = {
    'hr@company.com': {'password': 'hrpass', 'role': 'hr', 'name': 'HR Admin'},
    'alice@company.com': {'password': 'alice123', 'role': 'employee', 'name': 'Alice'}
}

class User(UserMixin):
    def __init__(self, id_, name, role):
        self.id = id_
        self.name = name
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    user = USERS.get(user_id)
    if not user:
        return None
    return User(user_id, user.get('name'), user.get('role'))

# --- Initialize vectorstore if not present ---
PERSIST_DIR = 'chroma_db'
EMBED_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

# --- Load Local LLaMA Model ---

HF_REPO_ID = "TheBloke/Llama-2-7B-Chat-GGUF"
GGUF_FILENAME = "llama-2-7b-chat.Q4_K_M.gguf"

print(f"Loading LLaMA model {GGUF_FILENAME}...")
llm = Llama.from_pretrained(
    repo_id=HF_REPO_ID,
    filename=GGUF_FILENAME,
    n_ctx=512,
    n_threads=8,
    n_gpu_layers=0
)

# build vectorstore from seed file if missing (safe no-op if exists)
build_vectorstore_if_missing(persist_dir=PERSIST_DIR)

vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
retriever = vectordb.as_retriever(search_kwargs={'k': 4})

# --- Routes ---
@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'hr':
            return redirect(url_for('hr_dashboard'))
        else:
            return render_template('index.html', user=current_user)
    # return render_template('index.html', user=None)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = USERS.get(email)
        if user and user['password'] == password:
            u = User(email, user.get('name'), user.get('role'))
            login_user(u)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Minimal example — replace with DB-backed registration
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        password = request.form['password']
        if email in USERS:
            flash('User exists', 'warning')
        else:
            USERS[email] = {'password': password, 'role': 'employee', 'name': name}
            flash('Registered — please login', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# HR Dashboard (upload documents)
@app.route('/hr', methods=['GET'])
@login_required
def hr_dashboard():
    if current_user.role != 'hr':
        flash('Access denied', 'danger')
        return redirect(url_for('home'))
    return render_template('hr_dashboard.html')

# upload endpoint for HR
UPLOAD_FOLDER = os.path.join('uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/upload', methods=['GET','POST'])
@login_required
def upload():
    if current_user.role != 'hr':
        return redirect(url_for('home'))
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'warning')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # index file into vectorstore (extract + embed + persist)
            save_and_index_file(filepath, persist_dir=PERSIST_DIR, embeddings_model_name=EMBED_MODEL)
            flash('File uploaded and indexed successfully', 'success')
            return redirect(url_for('hr_dashboard'))
    return render_template('upload.html')

# Query endpoint used by both HR and employees
@app.route("/ask", methods=["POST"])
@login_required
def ask():
    try:
       # Detect content type first
        if request.content_type.startswith('application/json'):
            data = request.get_json()
            query = (data.get('query') or '').strip()
            file = None
        elif request.content_type.startswith('multipart/form-data'):
            data = request.form
            query = (data.get('query') or '').strip()
            file = request.files.get('file')
        else:
            return jsonify({'error': 'Unsupported Content-Type'}), 415

        
        # 1️⃣ If HR uploads a file through chat
        if current_user.role == 'hr' and 'file' in request.files:
            f = request.files['file']
            if f.filename and allowed_file(f.filename):
                fname = secure_filename(f.filename)
                fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                f.save(fpath)
                save_and_index_file(fpath, PERSIST_DIR, EMBED_MODEL)
                msg = f"File '{fname}' uploaded and indexed successfully."
                return jsonify({'answer': msg, 'sources': []})

                 # 2️⃣ Otherwise normal query flow
   
        docs = retriever.get_relevant_documents(query)
        context = "\n\n---\n\n".join([d.page_content for d in docs])

        prompt = f"""
        You are an HR assistant. Use the HR policy context to answer the user's question concisely and accurately.

        CONTEXT:
        {context}

        QUESTION:
        {query}

        Answer in a helpful, short paragraph. If not in context, say you don't have that info and suggest contacting HR.
        """

        result = llm(prompt, max_tokens=256, temperature=0.0)

        if "choices" in result:
            answer = result["choices"][0]["text"].strip()
        elif "text" in result:
            answer = result["text"].strip()
        else:
            answer = "Sorry, I could not generate an answer."

        return jsonify({
            "answer": answer,
            "sources": [d.page_content[:300] for d in docs]
        })
    except Exception as e:
        print("Error in /ask:", e)
        return jsonify({"error": str(e)}), 500

# static favicon route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
