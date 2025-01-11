import subprocess
import redis
from typing import List 
from domain.redis.domain import RedisInstance, RedisStatus
from domain.process.service import ProcessManager
from infra.repository import RedisRepository

class RedisService:
    def __init__(self, repository: RedisRepository):
        self.repository = repository
    
    def create_instance(self, redis_id: str, port: int) -> RedisInstance:
        instance = RedisInstance.create(redis_id, port)
        self.repository.save(instance)
        return instance
    
    def delete_instance(self, redis_id: str):
        instance = self.repository.find_by_id(redis_id)
        if instance:
            process = ProcessManager.find_redis_process(instance.port)
            if process:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except:
                    process.kill()
            
            instance.delete()
            self.repository.delete(redis_id)
    
    def start_instance(self, redis_id: str) -> RedisInstance:
        instance = self.repository.find_by_id(redis_id)
        if not instance:
            raise ValueError(f"Redis instance {redis_id} not found")
        
        if ProcessManager.find_redis_process(instance.port):
            return instance
        
        process = subprocess.Popen(['redis-server.exe', instance.config_path])
        
        # Test connection
        client = redis.Redis(host='localhost', port=instance.port)
        client.ping()
        
        instance.status = RedisStatus.RUNNING
        self.repository.save(instance)
        
        return instance
    
    def stop_instance(self, redis_id: str) -> RedisInstance:
        instance = self.repository.find_by_id(redis_id)
        if not instance:
            raise ValueError(f"Redis instance {redis_id} not found")
        
        process = ProcessManager.find_redis_process(instance.port)
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
        
        instance.status = RedisStatus.STOPPED
        self.repository.save(instance)
        
        return instance
    
    def get_all_instances(self) -> List[RedisInstance]:
        return self.repository.find_all()