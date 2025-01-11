import psutil
from typing import Optional

class ProcessManager:
    @staticmethod
    def find_redis_process(port: int) -> Optional[psutil.Process]:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                if proc.name() == 'redis-server.exe':
                    for conn in proc.connections():
                        if conn.laddr.port == port:
                            return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return None