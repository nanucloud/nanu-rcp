import sqlite3
from datetime import datetime
from contextlib import contextmanager

class Database:
    def __init__(self, db_path: str = 'redis_manager.db'):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def init_db(self):
        with self.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS redis_instances (
                    id TEXT PRIMARY KEY,
                    port INTEGER UNIQUE,
                    config_path TEXT,
                    data_dir TEXT,
                    created_at TIMESTAMP,
                    status TEXT,
                    service_status INTEGER DEFAULT 0,
                    password TEXT
                )
            ''')
            conn.commit()