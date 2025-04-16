from functools import lru_cache
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from google.cloud import bigquery

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # BigQuery settings
    google_application_credentials: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    bigquery_project_id: str = os.getenv("BIGQUERY_PROJECT_ID", "")
    bigquery_dataset: str = os.getenv("BIGQUERY_DATASET", "")
    
    # API settings
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_root_path: str = os.getenv("API_ROOT_PATH", "/api")
    debug: bool = os.getenv("DEBUG", "True").lower() in ["true", "1", "t", "yes"]
    
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "default-secret-key-for-development-only")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }


@lru_cache()
def get_settings():
    """
    Get cached settings object to avoid reloading from environment
    """
    return Settings()


def get_bigquery_client():
    """
    Create and return a BigQuery client
    """
    settings = get_settings()
    project_id = settings.bigquery_project_id or "gcpxbixpflegehilfesenioren"
    
    # Look for any JSON file in the current and parent directories that might be credentials
    current_dir = os.getcwd()
    json_files_current = [f for f in os.listdir(current_dir) if f.endswith('.json')]
    json_files_parent = []
    parent_dir = os.path.join(current_dir, "..")
    if os.path.exists(parent_dir):
        json_files_parent = [os.path.join("..", f) for f in os.listdir(parent_dir) if f.endswith('.json')]
    
    # Try multiple potential credential paths
    credential_paths = [
        # Windows project directory path - any JSON file
        *[os.path.join(current_dir, f) for f in json_files_current],
        # Parent directory path - any JSON file
        *[os.path.join(current_dir, f) for f in json_files_parent],
        # Standard name in project directory
        os.path.join(current_dir, "credentials.json"),
        # Linux path from other project
        "/home/PfS/gcpxbixpflegehilfesenioren-a47c654480a8.json",
        # Environment variable path
        settings.google_application_credentials
    ]
    
    # Try each path until one works
    last_error = None
    for path in credential_paths:
        if not path:  # Skip empty paths
            continue
            
        try:
            # Try with explicit path
            client = bigquery.Client.from_service_account_json(
                path, 
                project=project_id
            )
            print(f"Successfully connected to BigQuery using credentials at: {path}")
            return client
        except FileNotFoundError:
            # Try next path
            last_error = f"Credentials file not found at: {path}"
            continue
        except Exception as e:
            # Log the error but try next path
            last_error = f"Error with credentials at {path}: {str(e)}"
            continue
    
    # If we get here, all paths failed
    raise ValueError(f"Failed to create BigQuery client. Last error: {last_error}") 