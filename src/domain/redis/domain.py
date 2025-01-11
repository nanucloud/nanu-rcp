from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import os
import shutil

class RedisStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"

@dataclass
class RedisInstance:
    id: str
    port: int
    config_path: str
    data_dir: str
    created_at: datetime
    status: RedisStatus

    @staticmethod
    def create(redis_id: str, port: int, base_path: str = "C:/NANU/NANU_RSR/ClusterData") -> "RedisInstance":
        config_path = f"{base_path}/{redis_id}/redis.service.conf"
        data_dir = f"{base_path}/{redis_id}/data"
        
        # 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)
        
        # Config생성
        config_content = f"""
port {port}
dir {data_dir}
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
            status=RedisStatus.STOPPED
        )
    
    def delete(self):
        base_dir = os.path.dirname(self.config_path)
        if os.path.exists(base_dir):
            shutil.rmtree(base_dir)
