import os


LOGS_PARENT_DIR = os.environ.get("LOGS_PARENT_DIR", "/tmp/")
LOGS_DIR = os.path.join(LOGS_PARENT_DIR, "chocolate_smart_home_logs/")

def create_logging_directory():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

if __name__ == "__main__":
    create_logging_directory()
