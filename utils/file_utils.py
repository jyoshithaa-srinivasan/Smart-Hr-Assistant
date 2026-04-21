#file type helpers and indexing helper
import os
from langchain.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

ALLOWED_EXTENSIONS = {'txt','pdf','docx','pptx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def load_document(filepath):
    ext = filepath.rsplit('.',1)[1].lower()
    if ext == 'pdf':
        loader = PyPDFLoader(filepath)
        docs = loader.load()
    elif ext == 'docx':
        loader = Docx2txtLoader(filepath)
        docs = loader.load()
    elif ext == 'pptx':
        loader = UnstructuredPowerPointLoader(filepath)
        docs = loader.load()
    else:
        loader = TextLoader(filepath, encoding='utf8')
        docs = loader.load()
    return docs

def save_and_index_file(filepath, persist_dir='chroma_db', embeddings_model_name='sentence-transformers/all-MiniLM-L6-v2'):
    # load
    docs = load_document(filepath)
    # add source metadata
    for d in docs:
        d.metadata = d.metadata or {}
        d.metadata['source'] = os.path.basename(filepath)

    # split
    splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=50)
    split_docs = []
    for d in docs:
        split_docs.extend(splitter.split_documents([d]))

    # embeddings & chroma
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    vectordb = Chroma.from_documents(split_docs, embeddings, persist_directory=persist_dir)
    vectordb.persist()
    return True
