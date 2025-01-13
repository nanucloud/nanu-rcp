from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import string
import secrets
import os
import shutil

class RedisStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class RedisInstance:
    id: str
    port: int
    config_path: str
    data_dir: str
    created_at: datetime
    status: RedisStatus
    service_status: int = 0
    password: str = ""

    @staticmethod
    def generate_password(length: int = 32) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def create(redis_id: str, port: int, base_path: str = "C:/NANU/NANU_RSR/ClusterData") -> "RedisInstance":
        try:
            config_path = f"{base_path}/{redis_id}/redis.service.conf"
            data_dir = f"{base_path}/{redis_id}/data"
            
            # Generate random password
            password = RedisInstance.generate_password()
            
            os.makedirs(data_dir, exist_ok=True)
            
            config_content = f"""
port {port}
dir {data_dir}
requirepass {password}
            """.strip()
            
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                f.write(config_content)
                
            return RedisInstance(
                id=redis_id,
                port=port,
                config_path=config_path,
                data_dir=data_dir,
                created_at=datetime.now(),
                status=RedisStatus.STOPPED,
                service_status=0,
                password=password
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create Redis instance: {e}")
        
    def delete(self):
        try:
            base_dir = os.path.dirname(self.config_path)
            if os.path.exists(base_dir):
                shutil.rmtree(base_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to delete Redis instance files: {e}")

    @staticmethod
    def exists_on_filesystem(redis_id: str, base_path: str = "C:/NANU/NANU_RSR/ClusterData") -> bool:
        instance_path = f"{base_path}/{redis_id}"
        return os.path.exists(instance_path)