# Quick start
python -m venv .venv
source .venv/bin/activate   # windows: .venv\Scripts\activate
pip install -r requirements.txt
# (optional) place hr_policies.txt in project root to seed DB
python app.py
# open http://127.0.0.1:5000
# login as hr@company.com / hrpass to upload documents
