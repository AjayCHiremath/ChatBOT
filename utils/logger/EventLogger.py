import os
from utils.logger.SessionId import get_session_id
from utils.aws_utils import read_auth_file_from_s3, write_auth_file_to_s3

def log_message(message: str, log_file:str, echo=False):
    # Get the session ID and format the log file path
    session_id = get_session_id().split("_")

    log_file += f"{session_id[0]}/{session_id[1]}_logs.txt".replace("//", "/")

    # Read the existing log file from S3
    file = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), object_key=log_file, use_locally=True)
    # If the file is empty, initialize it as a list
    file.append(message + "\n")
    # Write the updated log file back to S3
    write_auth_file_to_s3(authorized_user_data=file, bucket_name=os.getenv("MY_S3_BUCKET"), object_key=log_file, use_locally=True)

    if echo:
        print(message)
