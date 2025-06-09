from utils.logger.SessionId import get_session_id, get_email_id

# Document chunking
DOCUMENTS_CHUNK_SIZE = 1200
DOCUMENTS_CHUNK_OVERLAP = 200

# Embedding chunk size
CHUNK_SIZE_EMBEDDINGS = 100

# CHAT HISTORY STORAGE
MAX_TOKENS_CHAT_HISTORY = 1000

# Logging and storage
LOG_BASE = "logs/chatbot"
FILE_PATH_LOGS = "logs/chat_logs/"
RAW_CHATS = "logs/raw_chats/"
FILE_PATH_MODEL_NAME = r"D:\Course\ChatBOT\utils\models_used.json"
PERSIST_DIRECTORY = "logs/chat_memory/"

# Search parameters
SEARCH_TYPE = "similarity"  # or 'mmr', 'similarity_score_threshold'
SEARCH_KWARGS = {"k": 5}  # e.g., "score_threshold": 0.7, "lambda_mult": 0.5

# Metadata dictionary
METADATA = {"user_id": get_email_id(), "session_id": get_session_id()}

# Model configuration
MODEL_MAX_TOKENS = 3000

# ICONS
AI_ICONS=["https://api.dicebear.com/9.x/glass/svg?seed=https://api.dicebear.com/9.x/glass/svg?seed=Aiden&backgroundType=solid,gradientLinear&randomizeIds=true",
          "https://api.dicebear.com/9.x/glass/svg?seed=https://api.dicebear.com/9.x/glass/svg?seed=Kingston&backgroundType=solid,gradientLinear&randomizeIds=true",
          "https://api.dicebear.com/9.x/glass/svg?seed=https://api.dicebear.com/9.x/glass/svg?seed=Nolan&backgroundType=solid,gradientLinear&randomizeIds=true",
          "https://api.dicebear.com/9.x/glass/svg?seed=https://api.dicebear.com/9.x/glass/svg?seed=Caleb&backgroundType=solid,gradientLinear&randomizeIds=true",
          "https://api.dicebear.com/9.x/glass/svg?seed=https://api.dicebear.com/9.x/glass/svg?seed=Brian&backgroundType=solid,gradientLinear&randomizeIds=true"]
HUMAN_ICONS=["https://api.dicebear.com/9.x/lorelei/svg?seed=Leo",
          "https://api.dicebear.com/9.x/lorelei/svg?seed=Maria",
          "https://api.dicebear.com/9.x/lorelei/svg?seed=Jack",
          "https://api.dicebear.com/9.x/big-smile/svg?seed=Leo",
          "https://api.dicebear.com/9.x/big-smile/svg?seed=Jack",
          "https://api.dicebear.com/9.x/big-smile/svg?seed=Sophia",
          "https://api.dicebear.com/9.x/lorelei/svg?seed=Sophia"]