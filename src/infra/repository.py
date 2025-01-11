
from typing import List, Optional
from  domain.redis.domain import RedisInstance, RedisStatus
from infra.database import Database

class RedisRepository:
    def __init__(self, database: Database):
        self.database = database
    
    def save(self, instance: RedisInstance):
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO redis_instances 
                (id, port, config_path, data_dir, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                instance.id,
                instance.port,
                instance.config_path,
                instance.data_dir,
                instance.created_at,
                instance.status.value
            ))
            conn.commit()
    
    def find_by_id(self, redis_id: str) -> Optional[RedisInstance]:
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM redis_instances WHERE id = ?', (redis_id,))
            row = c.fetchone()
            
            if row:
                return RedisInstance(
                    id=row[0],
                    port=row[1],
                    config_path=row[2],
                    data_dir=row[3],
                    created_at=datetime.fromisoformat(row[4]),
                    status=RedisStatus(row[5])
                )
            return None
    
    def find_all(self) -> List[RedisInstance]:
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM redis_instances')
            rows = c.fetchall()
            
            return [
                RedisInstance(
                    id=row[0],
                    port=row[1],
                    config_path=row[2],
                    data_dir=row[3],
                    created_at=datetime.fromisoformat(row[4]),
                    status=RedisStatus(row[5])
                )
                for row in rows
            ]
    
    def delete(self, redis_id: str):
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM redis_instances WHERE id = ?', (redis_id,))
            conn.commit()