import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_PASS = os.environ.get('DB_PASS')
DB_USER = os.environ.get('DB_USER')
DB_NAME = os.environ.get('DB_NAME')

TEST_DB_HOST = os.environ.get('TEST_DB_HOST')
TEST_DB_PORT = os.environ.get('TEST_DB_PORT')
TEST_DB_PASS = os.environ.get('TEST_DB_PASS')
TEST_DB_USER = os.environ.get('TEST_DB_USER')
TEST_DB_NAME = os.environ.get('TEST_DB_NAME')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

TEST_REDIS_HOST = os.environ.get('TEST_REDIS_HOST')
TEST_REDIS_PORT = os.environ.get('TEST_REDIS_PORT')
