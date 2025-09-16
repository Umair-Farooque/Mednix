# MedNix - AI-Powered Drug Information Retrieval

[![Project Status](https://img.shields.io/badge/status-live-success)](https://mednix.onrender.com/)  
[Live Demo](https://mednix.onrender.com/)

---

## Table of Contents

- [Overview](#overview)  
- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Installation](#installation)  
- [Usage](#usage)  
- [Project Structure](#project-structure)  
- [API Keys & Environment Variables](#api-keys--environment-variables)  
- [Contributing](#contributing)  
- [License](#license)  

---

## Overview

MedNix is a **Retrieval-Augmented Generation (RAG) pipeline** that provides accurate, concise, and contextually relevant drug information. It leverages a combination of **OpenAI’s language models**, **FAISS embeddings**, and **Hugging Face datasets** to efficiently retrieve and answer medical queries.

The project is deployed live at [mednix.onrender.com](https://mednix.onrender.com/).

---

## Features

- **Query decomposition**: Breaks complex drug-related queries into manageable sub-questions.  
- **Vector search with FAISS**: Retrieves relevant text chunks from a precomputed embedding index.  
- **RAG pipeline**: Combines retrieval and LLMs for precise and concise answers.  
- **Final answer aggregation**: Merges sub-question answers into a coherent response.  
- **Live deployment**: Accessible via a web interface.  

---

## Tech Stack

- **Backend**: Python, FastAPI  
- **Embedding & LLM**: OpenAI API (`text-embedding-3-large`, `gpt-4o-mini`)  
- **Vector Database**: FAISS  
- **Data Storage**: Hugging Face Datasets  
- **Deployment**: Render  

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/<your-username>/mednix.git
cd mednix
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

1. Create a `.env` file in the root directory with the following:

```bash
OPENAI_API_KEY=sk-<your-openai-key>
EMBEDDING_MODEL=text-embedding-3-large
DECOMPOSE_MODEL=gpt-4o-mini
ANSWER_MODEL=gpt-4o-mini
```

2. Run the FastAPI server:

```bash
uvicorn main:app --reload
```

3. Access the web interface at `http://127.0.0.1:8000` or use the live link: [mednix.onrender.com](https://mednix.onrender.com/)

---

## Project Structure

```
mednix/
├─ rag_pipeline.py      # Core RAG pipeline (embedding, retrieval, LLM)
├─ main.py              # FastAPI app
├─ requirements.txt     # Dependencies
├─ .env.example         # Sample environment variables
├─ README.md
```

---

## API Keys & Environment Variables

- Use your **OpenAI project API key** (`sk-proj-...`) in the `.env` file.  
- Ensure the key has **embedding** and **chat completion** permissions.  
- Keep `.env` private; do **not commit it** to GitHub.  

---

## Contributing

1. Fork the repository  
2. Create a new branch (`git checkout -b feature/my-feature`)  
3. Commit your changes (`git commit -m "Add new feature"`)  
4. Push to the branch (`git push origin feature/my-feature`)  
5. Create a pull request  

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

