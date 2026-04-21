📌 Overview

Smart HR Assistant System is an AI-powered application designed to handle employee queries related to HR policies, leave management, and FAQs. The system processes unstructured HR documents such as PDFs and Word files, extracts relevant information, and generates accurate, context-aware responses using a custom Retrieval-Augmented Generation (RAG) pipeline.

Unlike framework-dependent implementations, this system uses a custom-built pipeline integrating document parsing, OCR, embeddings, and vector-based retrieval, providing better control over data flow and system behavior.

🎯 Objectives

Automate HR query resolution using AI-driven techniques
Extract and process information from unstructured documents (PDF, Word)
Enable context-aware response generation using a custom RAG pipeline
Reduce dependency on manual HR support
Build a scalable and efficient document-driven knowledge system


🧠 System Architecture

The system follows a custom modular pipeline:

🔹 Document Processing
Parses PDF and Word documents to extract textual content
Uses Tesseract OCR for scanned or image-based documents
🔹 Text Preprocessing
Cleans and normalizes extracted text
Splits documents into smaller chunks for efficient processing
🔹 Embedding Generation
Converts text chunks into vector representations using Sentence Transformers
🔹 Vector Storage & Retrieval (ChromaDB)
Stores embeddings in ChromaDB
Retrieves relevant document chunks using similarity search
🔹 Response Generation (RAG)
Combines retrieved context with LLM-based reasoning
Generates accurate, context-aware responses


🛠️ Tech Stack


Programming Language: Python
Backend: Flask
OCR: Tesseract OCR
Document Parsing: PDF & Word processing libraries
Embeddings: Sentence Transformers
Vector Database: ChromaDB
Libraries: NumPy, Pandas


⚙️ Workflow

HR documents (PDF/Word) are uploaded
Text is extracted using parsers and OCR (if required)
Content is cleaned and split into chunks
Sentence Transformers generate embeddings
Embeddings are stored in ChromaDB
User submits a query
Relevant document chunks are retrieved
Retrieved context is used to generate a response
System returns a structured answer to the user


📊 Results & Impact

Enabled efficient processing of unstructured HR documents
Improved response accuracy through context-aware retrieval
Reduced manual effort in searching HR policies
Designed a scalable and modular AI system

🚀 Use Cases

HR policy queries
Leave and employee-related FAQs
Document-based knowledge retrieval
Enterprise HR support automation

🔐 Security Features

Role-based access control
Controlled access to HR documents
Secure handling of sensitive organizational data


🔮 Future Enhancements


Web-based UI for improved usability
Integration with enterprise HR systems
Multi-language query support
Advanced analytics for HR queries
