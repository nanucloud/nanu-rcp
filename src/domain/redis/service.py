import subprocess
import redis
from typing import List, Dict, Optional
import os
from domain.redis.domain import RedisInstance, RedisStatus
from domain.process.service import ProcessManager
import time
from datetime import datetime


redis_path = r"C:\redis-server.exe"
BASE_PATH = "C:/Temp/RedisData"

class PortManager:
    MIN_PORT = 5000
    MAX_PORT = 9999
    
    @staticmethod
    def get_next_available_port(repository) -> int:
        used_ports = {instance.port for instance in repository.find_all()}
        
        for port in range(PortManager.MIN_PORT, PortManager.MAX_PORT + 1):
            if port not in used_ports and not ProcessManager.is_port_in_use(port):
                return port
        raise RuntimeError("No available ports in the specified range")

class RedisService:
    def __init__(self, repository):
        self.repository = repository

    def start_instance(self, redis_id: str) -> RedisInstance:
        instance = self.repository.find_by_id(redis_id)
        if not instance:
            raise ValueError(f"Redis instance {redis_id} not found")
        
        try:
            process = subprocess.Popen([redis_path, instance.config_path])
            time.sleep(2)
            
            # Test connection with password
            client = redis.Redis(
                host='localhost', 
                port=instance.port,
                password=instance.password
            )
            client.ping()
            
            instance.status = RedisStatus.RUNNING
            instance.service_status = 1
            self.repository.save(instance)
            
            return instance
        except Exception as e:
            raise RuntimeError(f"Failed to start Redis instance {redis_id}: {e}")

    def sync_with_filesystem(self):
        if os.path.exists(BASE_PATH):
            fs_instance_ids = {d for d in os.listdir(BASE_PATH) 
                             if os.path.isdir(os.path.join(BASE_PATH, d))}
        else:
            fs_instance_ids = set()

        db_instances = self.repository.find_all()
        db_instance_ids = {instance.id for instance in db_instances}

        for instance in db_instances:
            if instance.id not in fs_instance_ids:
                self.repository.delete(instance.id)

        for fs_id in fs_instance_ids:
            config_path = os.path.join(BASE_PATH, fs_id, "redis.service.conf")
            if os.path.exists(config_path):
                current_instance = self.repository.find_by_id(fs_id)
                
                port = None
                password = None
                with open(config_path, 'r') as f:
                    for line in f:
                        if line.startswith('port'):
                            port = int(line.split()[1])
                        elif line.startswith('requirepass'):
                            password = line.split(None, 1)[1].strip()

                if port:
                    if not current_instance:
                        instance = RedisInstance(
                            id=fs_id,
                            port=port,
                            config_path=config_path,
                            data_dir=os.path.join(BASE_PATH, fs_id, "data"),
                            created_at=datetime.fromtimestamp(os.path.getctime(config_path)),
                            status=RedisStatus.STOPPED,
                            service_status=0,
                            password=password
                        )
                        self.repository.save(instance)

    def create_instance(self, redis_id: str) -> RedisInstance:
        if RedisInstance.exists_on_filesystem(redis_id):
            raise RuntimeError(f"Redis instance {redis_id} already exists")
        
        try:
            port = PortManager.get_next_available_port(self.repository)
            instance = RedisInstance.create(redis_id, port)
            self.repository.save(instance)
            return instance
        except Exception as e:
            print(e)
            try:
                instance_path = f"{BASE_PATH}/{redis_id}"
                if os.path.exists(instance_path):
                    shutil.rmtree(instance_path)
            except:
                pass
            raise RuntimeError(f"Failed to create Redis instance: {e}")

    def delete_instance(self, redis_id: str):
        instance = self.repository.find_by_id(redis_id)
        if not instance:
            raise ValueError(f"Redis instance {redis_id} not found")

        try:
            # Stop the instance if it's running
            process = ProcessManager.find_redis_process(instance.port)
            if process:
                process.terminate()
                process.wait(timeout=5)

            # Delete files
            instance.delete()
            
            # Remove from database
            self.repository.delete(redis_id)
        except Exception as e:
            raise RuntimeError(f"Failed to delete Redis instance: {e}")

    def stop_instance(self, redis_id: str) -> RedisInstance:
        instance = self.repository.find_by_id(redis_id)
        if not instance:
            raise ValueError(f"Redis instance {redis_id} not found")

        try:
            process = ProcessManager.find_redis_process(instance.port)
            if process:
                process.terminate()
                process.wait(timeout=5)
            
            instance.status = RedisStatus.STOPPED
            instance.service_status = 0
            self.repository.save(instance)
            
            return instance
        except Exception as e:
            raise RuntimeError(f"Failed to stop Redis instance {redis_id}: {e}")

    def get_instance_status(self, redis_id: str) -> Dict:
        instance = self.repository.find_by_id(redis_id)
        if not instance:
            raise ValueError(f"Redis instance {redis_id} not found")

        process = ProcessManager.find_redis_process(instance.port)
        return {
            'id': instance.id,
            'running': process is not None,
            'pid': process.pid if process else None,
            'port': instance.port,
            'config_path': instance.config_path,
            'data_dir': instance.data_dir,
            'created_at': instance.created_at.isoformat(),
            'service_status': instance.service_status,
            'status': instance.status.value,
            'exists_on_filesystem': RedisInstance.exists_on_filesystem(redis_id)
        }

    def start_all_instances(self):
        """Start all Redis instances with service_status=1"""
        instances = self.repository.find_all()
        for instance in instances:
            if instance.service_status == 1:
                try:
                    self.start_instance(instance.id)
                except Exception as e:
                    print(f"Failed to auto-start Redis instance {instance.id}: {e}")

    def get_all_instances(self) -> List[RedisInstance]:
        return self.repository.find_all()