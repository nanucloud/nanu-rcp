import psutil
from typing import Optional
import socket

class ProcessManager:
    @staticmethod
    def find_redis_process(port: int) -> Optional[psutil.Process]:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == 'redis-server.exe':
                        for conn in proc.connections():
                            if conn.laddr.port == port:
                                return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Error checking process: {e}")
        return None

    @staticmethod
    def is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return False
            except socket.error:
                return True