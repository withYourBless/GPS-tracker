import logging
import os
import pytest
from fastapi.testclient import TestClient
from src.endpoints.main import app
from src.repository.db_connect import get_cursor

logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
os.makedirs(logs_dir, exist_ok=True)

log_file_path = os.path.join(logs_dir, "test.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, mode='a', encoding='utf-8'),  # mode='a' = append
        logging.StreamHandler()
    ]
)

test_logger = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def test_db_cursor():
    with get_cursor() as cursor:
        yield cursor


@pytest.fixture(scope="function")
def client(test_db_cursor):
    yield TestClient(app)

# @pytest.fixture(autouse=True)
# def clear_test_db():
#     with get_cursor() as cursor:
#         cursor.execute("DELETE FROM cron_log;")
#         cursor.execute("DELETE FROM gps_track;")
#         cursor.execute('DELETE FROM "user";')
