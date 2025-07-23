# Arch-I-Tect: Cloud Diagram-to-Code Generator 🖼️➡️💻

Convert cloud architecture diagrams into Infrastructure as Code (Terraform/CloudFormation) using multi-modal AI.

## 🌟 Features

- **Multi-Modal AI Analysis**: Upload architecture diagrams (screenshots, draw.io exports, whiteboard photos)
- **IaC Generation**: Automatically generate Terraform HCL or AWS CloudFormation YAML
- **Multiple LLM Support**: Use Ollama (local), OpenAI GPT-4 Vision, or Anthropic Claude 3
- **Smart Resource Detection**: Identifies AWS/Azure/GCP resources from visual elements
- **Code Validation**: Ensures generated code follows best practices
- **Interactive UI**: Preview images, syntax-highlighted code output, and explanations

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **Pillow & OpenCV** - Image processing
- **httpx** - Async HTTP client
- **Loguru** - Structured logging

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Monaco Editor** - Code display
- **Zustand** - State management
- **React Dropzone** - File uploads
- **Axios** - API client

### AI/ML
- **Ollama** - Local LLM support
- **OpenAI API** - GPT-4 Vision
- **Anthropic API** - Claude 3

## 🏗️ Architecture

```
arch-i-tect/
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── api/         # HTTP endpoints
│   │   ├── models/      # LLM client implementations
│   │   ├── services/    # Business logic
│   │   └── utils/       # Helpers and validators
│   └── tests/
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   │   ├── UploadZone.jsx
│   │   │   ├── ImagePreview.jsx
│   │   │   ├── CodeViewer.jsx
│   │   │   ├── FeedbackPanel.jsx
│   │   │   └── GenerateControls.jsx
│   │   ├── services/    # API client
│   │   ├── store/       # Zustand state management
│   │   └── App.jsx      # Main application
│   └── public/
└── docs/               # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama (optional, for local models)

### Quick Setup Script

```bash
# Clone repository
git clone https://github.com/yourusername/arch-i-tect.git
cd arch-i-tect

# Make setup script executable
chmod +x setup.sh

# Run setup script
./setup.sh
```

### Manual Setup

#### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/arch-i-tect.git
cd arch-i-tect

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run backend
python src/main.py
```

### Frontend Setup

```bash
# From project root
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Using Ollama (Local Models)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a vision model
ollama pull llava

# Start Ollama server (if not already running)
ollama serve
```

## 📡 API Endpoints

- `POST /api/v1/upload` - Upload architecture diagram
- `POST /api/v1/generate` - Generate IaC from uploaded diagram
- `GET /api/v1/preview/{image_id}` - Get image preview
- `GET /api/v1/status/{image_id}` - Check processing status
- `GET /health` - Health check

## 🔧 Configuration

### LLM Providers

#### Ollama (Local)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llava
```

#### OpenAI
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4-vision-preview
```

#### Anthropic
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229
```

## 🎯 Usage Example

1. **Upload Diagram**: Drag and drop your architecture diagram
2. **Select Format**: Choose Terraform or CloudFormation
3. **Generate Code**: Click generate and wait for AI analysis
4. **Review & Download**: Review the generated IaC and download

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test

# Run frontend in development mode
npm run dev

# Build frontend for production
npm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Ollama for local LLM support
- OpenAI for GPT-4 Vision
- Anthropic for Claude 3
- FastAPI and React communities

## 🚧 Roadmap

- [ ] Support for more cloud providers (Azure, GCP)
- [ ] Real-time collaboration features
- [ ] Version control for generated IaC
- [ ] Template library for common architectures
- [ ] Export to multiple IaC formats simultaneously
- [ ] Advanced validation and security scanning

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile for backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/src ./src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Deployment Options

- **Backend**: Deploy to AWS Lambda, Google Cloud Run, or Azure Functions
- **Frontend**: Deploy to Vercel, Netlify, or AWS S3 + CloudFront
- **Full Stack**: Deploy to Heroku, Railway, or Fly.io

### Environment Variables for Production

```env
# Production settings
API_HOST=0.0.0.0
API_PORT=$PORT
LLM_PROVIDER=openai  # or anthropic for production
ALLOWED_ORIGINS=https://your-domain.com
```