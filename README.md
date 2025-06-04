# LangChain Streamlit ChatBot

A scalable, modular, and real-time chatbot platform powered by **LangChain**, **Streamlit**, and **Ollama**. Built with extensibility in mind, this project serves as a foundation for advanced AI interactions — including agents, tool integrations, multimodal inputs, and dynamic model selection.

---

## 🔥 Key Features

- **LLama 3** integration via **Ollama** for fast local inference  
- **Token-level streaming** to simulate real-time assistant typing  
- **Clean, modular architecture** supporting pluggable models, chains, and prompts  
- Future-ready structure for:
  - LangChain Agents (e.g., LangGraph-based planning)
  - Document loaders, vector search, and RAG
  - Multimodal interactions (image, PDF, voice)
  - File tools and dynamic tool use  

---

## 🧱 Project Structure

```bash
LLMCHATBOT/
├── ChatBot.py                      # 🚀 Main Streamlit app entry point
├── .env                            # 🔐 Environment variables
│
├── components/                     # 🎨 UI: input form, display, layout
│   ├── input_form.py
│   ├── chat_display.py
│   └── layout.py
│
├── prompts/                        # 💬 Prompt templates
│   ├── default_prompt.py
│   └── agent_prompt.py
│
├── models/                         # 🧠 Model wrappers (Ollama, OpenAI, etc.)
│   ├── ollama_model.py
│   └── parser.py
│
├── chains/                         # 🔗 LangChain pipelines
│   └── chat_chain.py
│
├── agents/                         # 🕹️ Future enchancement Multi-agent logic (LangGraph, planners)
│   └── xyz.py
│
├── tools/                          # 🧰 Future enchancement  Agent tools (file parsers, search, APIs)
│   └── xyz.py
│
├── config/                         # ⚙️ Future enchancement App/config settings
│   └── xyz.yaml
│
├── utils/                          # 🧼 Reusable utilities
│   ├── env_loader.py
│   └── streaming_callback.py
│
└── README.md
```

---

## ⚙️ Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> Ensure Ollama is installed and running locally.

---

### 2. Configure Environment

Create a `.env` file with your LangChain/LangSmith keys:

```env
LANGCHAIN_API_KEY=your-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your-project
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

---

### 3. Pull Model with Ollama

```bash
ollama pull llama3
```

---

### 4. Run the App

```bash
streamlit run ChatBot.py
```

---

## 🧭 Roadmap

| Module                 | Description |
|------------------------|-------------|
| Model Selector         | UI component to switch between models or tools |
| PDF/Image Summarizer   | Upload and summarize PDFs and images via agents |
| Retail Insight Agent   | NL query to SQL → data → charts + LLM summary |
| LangGraph Agents       | Multi-agent orchestration with memory/tool use |
| Toolkits               | Integrate tools like file parser, web search |
| Multimodal UI          | Accept image, PDF, text inputs interchangeably |
