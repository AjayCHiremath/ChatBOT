from utils.logger.SessionId import get_session_id

# APP LINK
APP_LINK="https://chatbot-and-linkedin-jobs-apply.up.railway.app/"

# Document chunking
DOCUMENTS_CHUNK_SIZE = 2500
DOCUMENTS_CHUNK_OVERLAP = 250

# Embedding chunk size
CHUNK_SIZE_EMBEDDINGS = 100

# CHAT HISTORY STORAGE
MAX_TOKENS_CHAT_HISTORY = 1700

# Logging and storage
LOG_BASE = "logs/chatbot"
FILE_PATH_LOGS = "logs/chat_logs/"
RAW_CHATS = "logs/raw_chats/"
FILE_PATH_MODEL_NAME = "utils/models_used.json"
PERSIST_DIRECTORY = "logs/chat_memory/"
LOTTIE_FILE_PATH = "components/main_ui/Animation2.json"

# Search parameters
SEARCH_TYPE = "similarity"  # or 'mmr', 'similarity_score_threshold'
SEARCH_KWARGS = {"k": 15}  # e.g., "score_threshold": 0.7, "lambda_mult": 0.5

# Metadata dictionary
METADATA = {"session_id": get_session_id()}

# File names
OBJECT_KEYS_AUTHETICATION = "_secret_auth_.json"
OBJECT_KEYS_CHAT_HISTORY = f"{get_session_id()}.json"

# Model configuration
MODEL_MAX_TOKENS = 3000

# ICONS
AI_ICON = ("components/pdf_summarizer/ui/avatar/ai.png")
HUMAN_ICON = ("components/pdf_summarizer/ui/avatar/human.png")
