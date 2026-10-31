import logging 
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LOG_DIR  = PROJECT_ROOT / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"

def setup_logger():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(
                LOG_FILE,
                encoding="utf-8"
            ),
            logging.StreamHandler()
        ],
        force=True
    )

    return logging.getLogger("jima_retail")