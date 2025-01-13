# infra/repository.py
from typing import List, Optional
from datetime import datetime
from domain.redis.domain import RedisInstance, RedisStatus
from infra.database import Database

class RedisRepository:
    def __init__(self, database: Database):
        self.database = database
    
    def save(self, instance: RedisInstance):
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO redis_instances 
                (id, port, config_path, data_dir, created_at, status, service_status, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                instance.id,
                instance.port,
                instance.config_path,
                instance.data_dir,
                instance.created_at.isoformat(),
                instance.status.value,
                instance.service_status,
                instance.password
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
                    status=RedisStatus(row[5]),
                    service_status=int(row[6]),
                    password=row[7]
                )
            return None

    def find_all(self) -> List[RedisInstance]:
        """
        Retrieve all Redis instances from the database
        """
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
                    status=RedisStatus(row[5]),
                    service_status=int(row[6])
                )
                for row in rows
            ]

    def delete(self, redis_id: str):
        """
        Delete a Redis instance from the database
        """
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM redis_instances WHERE id = ?', (redis_id,))
            conn.commit()

    def update_status(self, redis_id: str, status: RedisStatus):
        """
        Update the status of a Redis instance
        """
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE redis_instances 
                SET status = ?
                WHERE id = ?
            ''', (status.value, redis_id))
            conn.commit()

    def update_service_status(self, redis_id: str, service_status: int):
        """
        Update the service_status of a Redis instance
        """
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('''
                UPDATE redis_instances 
                SET service_status = ?
                WHERE id = ?
            ''', (service_status, redis_id))
            conn.commit()

    def find_by_port(self, port: int) -> Optional[RedisInstance]:
        """
        Find a Redis instance by its port
        Returns None if not found
        """
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM redis_instances WHERE port = ?', (port,))
            row = c.fetchone()
            
            if row:
                return RedisInstance(
                    id=row[0],
                    port=row[1],
                    config_path=row[2],
                    data_dir=row[3],
                    created_at=datetime.fromisoformat(row[4]),
                    status=RedisStatus(row[5]),
                    service_status=int(row[6])
                )
            return None

    def exists(self, redis_id: str) -> bool:
        """
        Check if a Redis instance exists in the database
        """
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT 1 FROM redis_instances WHERE id = ?', (redis_id,))
            return c.fetchone() is not None

    def port_exists(self, port: int) -> bool:
        """
        Check if a port is already in use by any Redis instance
        """
        with self.database.get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT 1 FROM redis_instances WHERE port = ?', (port,))
            return c.fetchone() is not None