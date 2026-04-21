import os
from utils.file_utils import load_document, save_and_index_file

POLICIES_FILE = 'hr_policies.txt'
PERSIST_DIR = 'chroma_db'

# Called at startup to create a DB if missing

def build_vectorstore_if_missing(policies_path=POLICIES_FILE, persist_dir=PERSIST_DIR):
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print('Chroma DB present — skipping rebuild')
        return

    if os.path.exists(policies_path):
        print('Building vectorstore from seed file...')
        save_and_index_file(policies_path, persist_dir=persist_dir)
        print('Done')
    else:
        print('No seed HR policies file found. Upload documents from HR dashboard to populate the DB.')

if __name__ == '__main__':
    build_vectorstore_if_missing()
