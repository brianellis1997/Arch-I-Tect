# 🧠 Arch-I-Tect: Cloud Diagram to Infrastructure-as-Code Generator

> Turn cloud architecture diagrams into Terraform or CloudFormation code using multi-modal AI.

Arch-I-Tect is an AI-powered developer tool that lets you upload cloud architecture diagrams and receive fully generated Infrastructure-as-Code (IaC). It combines vision models, large language models, and an elegant frontend to help engineers go from whiteboard to deployment in seconds.

---

## 🚀 Features

- 🖼️ **Image Upload** – Upload architecture diagrams (screenshots, draw.io, whiteboard photos)
- 🤖 **Multi-Modal AI Integration** – Analyze images and generate infrastructure definitions using LLMs (Ollama, GPT-4o, Claude)
- 💻 **Code Output Viewer** – Syntax-highlighted IaC output with download/export support
- 🔄 **Modular Backend** – Clean separation of LLMs, prompt management, and image preprocessing
- ⚡ **Local + API Modes** – Use local Ollama models or cloud APIs interchangeably
- 🌐 **Modern Frontend** – Built with React and Vite for fast, responsive UX

---

## 📁 Project Structure

```

arch-i-tect/
├── backend/
│   ├── src/
│   │   ├── api/                 # FastAPI routes & middleware
│   │   ├── models/              # Abstract LLM & client interfaces
│   │   ├── services/            # Core image + IaC generation logic
│   │   ├── utils/               # Formatters and validation
│   │   └── main.py              # Entry point
│   ├── tests/                   # Unit tests (TBD)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/          # UI components
│   │   ├── services/            # Backend API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md

````

---

## 🧑‍💻 Setup Instructions

### 🐍 Backend (FastAPI)

```bash
cd arch-i-tect/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Update model settings and keys
uvicorn src.main:app --reload
````

> ⚙️ Supports both local (`llava`, `bakllava`) and cloud-based (GPT-4o, Claude) models. Configure via `.env`.

### 🌐 Frontend (React + Vite)

```bash
cd arch-i-tect/frontend
npm install
npm run dev
```

> App runs on `http://localhost:5173` and connects to backend on port `8000`.

---

## 🧠 LLMs & Prompts

* Multi-modal models are accessed via:

  * `Ollama` (local): e.g. `llava`, `llava-phi`, `bakllava`
  * `OpenAI` (API): GPT-4o with vision support
  * `Anthropic` (API): Claude 3.5 Sonnet

### Example Prompt Template

```text
You are a senior cloud architect. Analyze the given architecture diagram and generate Terraform (HCL) code to deploy the depicted AWS resources. Focus on EC2, S3, Lambda, VPCs, and Load Balancers.
```

---

## 🛠 Roadmap

* [x] MVP upload + image-to-code flow
* [ ] Image preprocessing (OCR, edge-enhance)
* [ ] Real-time code generation with streaming feedback
* [ ] Editable IaC output
* [ ] Explainability mode ("Explain this architecture")
* [ ] Support for Azure & GCP resource mappings

---

## 🧪 Testing

```bash
cd backend
pytest tests/
```

> Add tests for prompt logic, model outputs, and image preprocessing.

---

## 🧠 Why This Project

This tool demonstrates how agentic systems and multi-modal LLMs can streamline infrastructure workflows. It’s a portfolio-ready, technically diverse application built for speed and clarity.

---

## 📜 License

MIT License

---