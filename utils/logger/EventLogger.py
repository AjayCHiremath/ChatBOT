import os
from utils.logger.SessionId import get_session_id

def log_message(message: str, log_file:str, echo=False):

    session_id = get_session_id()

    log_file += f"{session_id}/{session_id}_logs.txt"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

    if echo:
        print(message)