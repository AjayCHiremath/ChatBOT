# LangChain Streamlit ChatBot

A lightweight Streamlit application that showcases how to combine LangChain with Llama 3 for document summarization and simple automation tasks. The codebase is intentionally small and modular so new tools and chains can be plugged in easily.

---

## 🔥 Key Features

- **LLama 3 via Ollama** for local, fast inference
- **Token streaming** to mimic an assistant typing responses
- **Modular components** so new models and chains can be added quickly
- Includes a **PDF Summarizer** and a **LinkedIn Jobs Apply** demo

---

## 🧱 Project Structure

```bash
ChatBOT/
├── ChatBotApp.py                  # Main Streamlit app
├── ai/
│   └── pdf_summarizer/
│       ├── chains/
│       ├── models/
│       ├── prompts/
│       └── tools/
├── components/
│   ├── pdf_summarizer/
│   ├── linkedin_automation/
│   │   ├── jobs_applier_selanium/
│   │   ├── web_scrapper_selanium/
│   │   └── ui/
│   └── ui/                        # Sidebar and common widgets
├── utils/
│   ├── EnvironmentLoaders.py
│   ├── StreamingCallbacks.py
│   └── logger/
│       ├── EventLogger.py
│       └── SessionId.py
└── README.md
```

---

## 🔗 Pipeline Overview

```
ChatBotApp.py → Sidebar.select_application
    ├─ "PDF Summarizer" → run_pdf_summarizer()
    │       ├─ build_layout → containers for chat and input
    │       ├─ UserInput.get_file / get_user_input
    │       ├─ PromptEngineering.get_prompt_template
    │       ├─ ModelLoader.load_llama_model
    │       ├─ OutputParsers.get_output_parser
    │       └─ SimpleLLMChain (prompt → model → parser) → StreamToStreamlit
    └─ "LinkedIn Jobs Apply" → run_linkedin_jobs_apply()
```

---

## ⚙️ Getting Started

### 1. Install Dependencies

Install the required Python packages:

```bash
pip install streamlit langchain langchain-together pandas spacy selenium
```

> Ensure Ollama is installed and running locally.

### 2. Configure Environment

Create a `.env` file with your LangChain/LangSmith keys:

```env
LANGCHAIN_API_KEY=your-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your-project
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

### 3. Pull the Model

```bash
ollama pull llama3
```

### 4. Run the App

```bash
streamlit run ChatBotApp.py
```

---

## 🧭 Roadmap

| Module               | Description                                                   |
|----------------------|---------------------------------------------------------------|
| Model Selector       | UI component to switch between models or tools               |
| PDF/Image Summarizer | Upload and summarize PDFs and images via agents              |
| Retail Insight Agent | NL query to SQL → data → charts + LLM summary                |
| LangGraph Agents     | Multi-agent orchestration with memory/tool use               |
| Toolkits             | Integrate tools like file parser, web search                 |
| Multimodal UI        | Accept image, PDF, text inputs interchangeably               |
| More integrations    | Additional agents and models                                 |

