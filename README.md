diff --git a/README.md b/README.md
index d60c28bc94e38f5949751597dfaf6404ab6cd195..da5cf06202e37f78a979cd3b83cf746ef274ff79 100644
--- a/README.md
+++ b/README.md
@@ -1,111 +1,109 @@
 # LangChain Streamlit ChatBot
 
-A scalable, modular, and real-time chatbot platform powered by **LangChain**, **Streamlit**, and **Ollama**. Built with extensibility in mind, this project serves as a foundation for advanced AI interactions — including agents, tool integrations, multimodal inputs, and dynamic model selection.
+A lightweight Streamlit application that showcases how to combine LangChain with Llama 3 for document summarization and simple automation tasks. The codebase is intentionally small and modular so new tools and chains can be plugged in easily.
 
 ---
 
 ## 🔥 Key Features
 
-- **LLama 3** integration via **Ollama** for fast local inference  
-- **Token-level streaming** to simulate real-time assistant typing  
-- **Clean, modular architecture** supporting pluggable models, chains, and prompts  
-- Future-ready structure for:
-  - LangChain Agents (e.g., LangGraph-based planning)
-  - Document loaders, vector search, and RAG
-  - Multimodal interactions (image, PDF, voice)
-  - File tools and dynamic tool use  
+- **LLama 3 via Ollama** for local, fast inference
+- **Token streaming** to mimic an assistant typing responses
+- **Modular components** so new models and chains can be added quickly
+- Includes a **PDF Summarizer** and a **LinkedIn Jobs Apply** demo
 
 ---
 
 ## 🧱 Project Structure
 
 ```bash
-LLMCHATBOT/
-├── ChatBot.py                      # 🚀 Main Streamlit app entry point
-├── .env                            # 🔐 Environment variables
-│
-├── components/                     # 🎨 UI: input form, display, layout
-│   ├── input_form.py
-│   ├── chat_display.py
-│   └── layout.py
-│
-├── prompts/                        # 💬 Prompt templates
-│   ├── default_prompt.py
-│   └── agent_prompt.py
-│
-├── models/                         # 🧠 Model wrappers (Ollama, OpenAI, etc.)
-│   ├── ollama_model.py
-│   └── parser.py
-│
-├── chains/                         # 🔗 LangChain pipelines
-│   └── chat_chain.py
-│
-├── agents/                         # 🕹️ Future enchancement Multi-agent logic (LangGraph, planners)
-│   └── xyz.py
-│
-├── tools/                          # 🧰 Future enchancement  Agent tools (file parsers, search, APIs)
-│   └── xyz.py
-│
-├── config/                         # ⚙️ Future enchancement App/config settings
-│   └── xyz.yaml
-│
-├── utils/                          # 🧼 Reusable utilities
-│   ├── env_loader.py
-│   └── streaming_callback.py
-│
+ChatBOT/
+├── ChatBotApp.py                  # Main Streamlit app
+├── ai/
+│   └── pdf_summarizer/
+│       ├── chains/
+│       ├── models/
+│       ├── prompts/
+│       └── tools/
+├── components/
+│   ├── pdf_summarizer/
+│   ├── linkedin_automation/
+│   │   ├── jobs_applier_selanium/
+│   │   ├── web_scrapper_selanium/
+│   │   └── ui/
+│   └── ui/                        # Sidebar and common widgets
+├── utils/
+│   ├── EnvironmentLoaders.py
+│   ├── StreamingCallbacks.py
+│   └── logger/
+│       ├── EventLogger.py
+│       └── SessionId.py
 └── README.md
 ```
 
 ---
 
+## 🔗 Pipeline Overview
+
+```
+ChatBotApp.py → Sidebar.select_application
+    ├─ "PDF Summarizer" → run_pdf_summarizer()
+    │       ├─ build_layout → containers for chat and input
+    │       ├─ UserInput.get_file / get_user_input
+    │       ├─ PromptEngineering.get_prompt_template
+    │       ├─ ModelLoader.load_llama_model
+    │       ├─ OutputParsers.get_output_parser
+    │       └─ SimpleLLMChain (prompt → model → parser) → StreamToStreamlit
+    └─ "LinkedIn Jobs Apply" → run_linkedin_jobs_apply()
+```
+
+---
+
 ## ⚙️ Getting Started
 
 ### 1. Install Dependencies
 
+Install the required Python packages:
+
 ```bash
-pip install -r requirements.txt
+pip install streamlit langchain langchain-together pandas spacy selenium
 ```
 
 > Ensure Ollama is installed and running locally.
 
----
-
 ### 2. Configure Environment
 
 Create a `.env` file with your LangChain/LangSmith keys:
 
 ```env
 LANGCHAIN_API_KEY=your-key
 LANGCHAIN_TRACING_V2=true
 LANGCHAIN_PROJECT=your-project
 LANGSMITH_ENDPOINT=https://api.smith.langchain.com
 ```
 
----
-
-### 3. Pull Model with Ollama
+### 3. Pull the Model
 
 ```bash
 ollama pull llama3
 ```
 
----
-
 ### 4. Run the App
 
 ```bash
-streamlit run ChatBot.py
+streamlit run ChatBotApp.py
 ```
 
 ---
 
 ## 🧭 Roadmap
 
-| Module                 | Description |
-|------------------------|-------------|
-| Model Selector         | UI component to switch between models or tools |
-| PDF/Image Summarizer   | Upload and summarize PDFs and images via agents |
-| Retail Insight Agent   | NL query to SQL → data → charts + LLM summary |
-| LangGraph Agents       | Multi-agent orchestration with memory/tool use |
-| Toolkits               | Integrate tools like file parser, web search |
-| Multimodal UI          | Accept image, PDF, text inputs interchangeably |
+| Module               | Description                                                   |
+|----------------------|---------------------------------------------------------------|
+| Model Selector       | UI component to switch between models or tools               |
+| PDF/Image Summarizer | Upload and summarize PDFs and images via agents              |
+| Retail Insight Agent | NL query to SQL → data → charts + LLM summary                |
+| LangGraph Agents     | Multi-agent orchestration with memory/tool use               |
+| Toolkits             | Integrate tools like file parser, web search                 |
+| Multimodal UI        | Accept image, PDF, text inputs interchangeably               |
+| More integrations    | Additional agents and models                                 |
+
