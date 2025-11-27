# Spektr - AI-Powered Document Extraction

Extract structured data from documents (PDFs and images) using AI.

## Quick Start

### Local Development
```bash
# Install dependencies
python3 -m pip install -r requirements.txt

# Configure API key (choose one):
# Option 1: .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Option 2: Streamlit secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your OPENAI_API_KEY

# Run the app
python3 -m streamlit run app.py
```

### Deploy to Streamlit Community Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Create a new app pointing to your repository
4. In "Advanced settings", add your secret:
   ```toml
   OPENAI_API_KEY = "sk-proj-your-key-here"
   ```
5. Deploy!

## Features

- ✨ AI-powered extraction using GPT-4o
- 📄 Supports PDFs and images (PNG, JPG, JPEG)
- 🎯 Customizable extraction fields
- 🔒 Secure API key management
- ☁️ Ready for Streamlit Community Cloud deployment

## Documentation

See [walkthrough.md](walkthrough.md) for detailed setup instructions.
