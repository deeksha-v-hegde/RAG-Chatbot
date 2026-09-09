"""
Phase 5: Minimal Web Interface & API Layer
Runner: run_server.py

Starts the FastAPI server with Uvicorn using configurations from .env.
"""

import os
import sys
from pathlib import Path
import uvicorn

# Add paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Load .env if present
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(dotenv_path=env_file)
    else:
        load_dotenv()
except ImportError:
    pass

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))


def main():
    print("=" * 72)
    print("       GROWW MUTUAL FUND FAQ ASSISTANT - API & WEB INTERFACE        ")
    print(f"       Serving on: http://{HOST}:{PORT}                             ")
    print(f"       Health Check: http://{HOST}:{PORT}/health                   ")
    print(f"       Interactive Docs: http://{HOST}:{PORT}/docs                 ")
    print("=" * 72)

    uvicorn.run(
        "phase5.api:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
