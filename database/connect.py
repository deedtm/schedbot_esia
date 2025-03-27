import sqlite3
from config.database import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
