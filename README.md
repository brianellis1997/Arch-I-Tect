# 🧠 Arch-I-Tect: Cloud Diagram to Infrastructure-as-Code Generator

> Turn cloud architecture diagrams into Terraform or CloudFormation code using multi-modal AI.

Arch-I-Tect is an AI-powered developer tool that lets you upload cloud architecture diagrams and receive fully generated Infrastructure-as-Code (IaC). It combines vision models, large language models, and an elegant frontend to help engineers go from whiteboard to deployment in seconds.

## 🌟 Features

- **Multi-Modal AI Analysis**: Upload architecture diagrams (screenshots, draw.io exports, whiteboard photos)
- **IaC Generation**: Automatically generate Terraform HCL or AWS CloudFormation YAML
- **Multiple LLM Support**: Use Ollama (local), OpenAI GPT-4 Vision, or Anthropic Claude 3
- **Smart Resource Detection**: Identifies AWS/Azure/GCP resources from visual elements
- **Code Validation**: Ensures generated code follows best practices
- **Interactive UI**: Preview images, syntax-highlighted code output, and explanations

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
│   └── src/
│       ├── components/  # UI components
│       └── services/    # API client
└── docs/               # Documentation
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama (optional, for local models)

### Backend Setup

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