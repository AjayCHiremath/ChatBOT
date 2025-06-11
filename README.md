
# 📚✨ ChatBOT Project ✨📚

Welcome to the **ChatBOT Project** — a modular, real-time AI assistant built with 💡 **LangChain**, 🚀 **Streamlit**, and 🤖 **Together.ai**! This system features token-level streaming, plug-and-play models/chains, and is accessible via a live demo.

⚠️ **Note:** Both the **LinkedIn automation logic** and parts of the **ChatBOT's core logic** are currently under development. Expect exciting updates soon!

---

## 🧱 Project Structure

```markdown
📂 CHATBOT/
├── ChatBotApp.py                        # 🚀 Main app entry point
├── .gitignore                           # 🛑 Specifies files/folders ignored by Git
├── README.md                            # 📖 Project documentation
├── requirements.txt                     # 🛠️ Python dependencies
├── .env                                 # 🔐 Environment variables

├── .streamlit/
│   └── config.toml                      # 🎨 Streamlit theme configuration

├── ai/
│   └── pdf_summarizer/
│       ├── chains/
│       │   └── Chain.py                 # 🔗 Conversation chain manager
│       ├── data_ingestion/
│       │   ├── DataLoaders.py           # 📥 Loads documents
│       │   ├── DocumentSplitters.py     # ✂️ Splits PDFs
│       │   └── VectorEmbeddings.py      # 🧩 Generates embeddings
│       ├── memory/
│       │   └── Memory.py                # 🧠 Stores conversation memory
│       ├── models/
│       │   ├── ModelLoader.py           # 📦 Loads AI models
│       │   └── OutputParsers.py         # 📝 Parses model outputs
│       ├── prompts/
│       │   └── Prompts.py               # ✍️ Prompt templates
│       ├── rag/
│       │   └── Retrivers.py             # 🔍 Retrieves relevant context
│       ├── tools/
│       │   └── ModelConnections.py      # 🔗 Integrates AI modules & S3
│       └── vectorstore/
│           └── VectorStore.py           # 🗂️ Pinecone vectorstore

├── components/
│   ├── main_ui/
│   │   ├── Animation2.json              # 🎞️ UI animations
│   │   ├── background.css               # 🎨 App styling
│   │   └── Sidebar.py                   # 📑 App sidebar
│   ├── pdf_summarizer/
│   │   ├── PDFSummarizer.py             # 📄 Summarizer logic
│   │   └── ui/
│   │       ├── ChatHistory.py           # 💬 Chat display
│   │       ├── ContainerLayout.py       # 📐 Layout management
│   │       ├── Expander.py              # ➕ Collapsible sections
│   │       ├── StatusBar.py             # 📊 Session status
│   │       ├── UserInput.py             # 📝 User queries
│   │       └── avatar/
│   │           ├── ai.png               # 🤖 AI avatar
│   │           └── human.png            # 👤 Human avatar
│   └── linkedin_automation/
│       ├── ChromeJobsApplier.py         # 💼 Automates LinkedIn jobs
│       ├── jobs_applier_selanium/
│       │   ├── data/
│       │   │   └── configurations.py
│       │   ├── helpers/
│       │   │   ├── ApplyForJobs.py
│       │   │   ├── DataPreprocess.py
│       │   │   ├── LoginPage.py
│       │   │   ├── myExperiencePage.py
│       │   │   └── myInformationPage.py
│       │   └── notification/
│       │       └── alert.mp3            # 🔔 Alert sound
│       ├── ui/
│       │   ├── ConfirmRefixValues.py
│       │   ├── ExternalJobDetails.py
│       │   ├── LinkedInJobDetails.py
│       │   ├── LinkedInMain.py
│       │   ├── LoginPage.py
│       │   └── ResumeUploader.py
│       └── web_scrapper_selanium/
│           ├── LinkedInApplier.py
│           └── helpers/
│               ├── AppLogin.py
│               ├── ApplyJobFilters.py
│               ├── FillJobFilters.py
│               ├── JobSearch.py
│               ├── PageChange.py
│               ├── ScrapeData.py
│               ├── ScrapeHelpers.py
│               └── TerminateProcess.py

├── logs/
│   ├── chatbot/                         # 📊 Session logs by user/email/session
│   └── jobs_applied/
│       └── linkedin_jobs.xlsx

├── utils/
│   ├── aws_utils.py                     # ☁️ AWS helpers
│   ├── EnvLoaders.py / EnvReloader.py   # 🔄 .env loaders
│   ├── global_variables.py              # 🌐 Global variables
│   ├── models_used.json                 # 📊 AI models used
│   ├── logger/
│   │   ├── EventLogger.py               # 📝 Event logging
│   │   ├── SessionId.py                 # 🔑 Session management
│   │   └── SessionStatePersistence.py
│   └── login_page/
│       └── streamlit_login_auth_ui/
│           ├── aws_utils.py
│           ├── login.py
│           ├── login_utils.py
│           └── widgets.py
```

---

## 🔥 Key Features (In Depth)

✨ **Modular AI Components**
- Designed to separate logic and AI modules for easy testing, scalability, and maintenance.

📄 **Document Summarizer**
- Ingests and splits PDFs into chunks.
- Embeds text using Together AI’s `m2-bert-80M-8k-retrieval`.
- Stores embeddings in Pinecone.
- Uses prompt engineering, RAG, memory, and chains for interactive Q&A.

🤖 **LinkedIn Job Application Automator (Educational Purposes Only)**
- Selenium automation to scrape and apply to LinkedIn/Workday jobs.
- LLMs (in progress) for dynamic question responses and resume customization.

🔒 **Security & Stability**
- Authentication with login page.
- Input validation, session management, content moderation.
- Rate limiting to avoid overload.

🗂️ **Session & User Logging**
- Logs stored in S3 by session and user.
- Supports easy monitoring and debugging.

---

## ⚙️ Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 2. Configure Environment

Create a `.env` file with your LangChain/LangSmith keys:

```env
LANGCHAIN_API_KEY=your-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=your-project
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

PINECONE_API_KEY=your-key
PINECONE_INDEX=your-index
PINECONE_REGION=your-region

TOGETHER_API_KEY=your-key
TOGETHER_BASE_URL=https://api.together.ai

AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_DEFAULT_REGION=your-region
MY_S3_BUCKET=your-bucket

SMTP_SENDER_EMAIL=your-email
SMTP_APP_PASSWORD=your-app-password
COMPANY_NAME=your-company-name
```

---

### 3. Run the App

```bash
streamlit run ChatBotApp.py
```

---

## 🤝 Contributing

We welcome contributions! Fork this repo and submit a pull request. 📬

---

🌟 Thank you for exploring ChatBOT! 🌟
