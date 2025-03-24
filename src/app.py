from flask import Flask, jsonify, request
from infra.database import Database
from flask_cors import CORS
from infra.repository import RedisRepository
from domain.redis.service import RedisService
from domain.process.service import ProcessManager
from threading import Thread
import psutil
from datetime import datetime

app = Flask(__name__)
CORS(app)

database = Database()
repository = RedisRepository(database)
redis_service = RedisService(repository)

@app.route('/api/redis', methods=['POST'])
def create_redis():
    data = request.get_json()
    redis_id = data.get('redis_id')
    
    if not redis_id:
        return jsonify({'error': 'redis_id is required'}), 400
    
    try:
        instance = redis_service.create_instance(redis_id)
        print(instance)
        return jsonify({
            'id': instance.id,
            'port': instance.port,
            'config_path': instance.config_path,
            'data_dir': instance.data_dir,
            'status': instance.status.value,
            'service_status': instance.service_status,
            'created_at': instance.created_at.isoformat(),
            'redis_password': instance.password
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redis/<redis_id>', methods=['DELETE'])
def delete_redis(redis_id):
    try:
        redis_service.delete_instance(redis_id)
        return '', 204
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redis/<redis_id>/start', methods=['POST'])
def start_redis(redis_id):
    try:
        instance = redis_service.start_instance(redis_id)
        return jsonify({
            'id': instance.id,
            'port': instance.port,
            'status': instance.status.value,
            'service_status': instance.service_status
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redis/<redis_id>/stop', methods=['POST'])
def stop_redis(redis_id):
    try:
        instance = redis_service.stop_instance(redis_id)
        return jsonify({
            'id': instance.id,
            'port': instance.port,
            'status': instance.status.value,
            'service_status': instance.service_status
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redis', methods=['GET'])
def list_redis():
    try:
        instances = redis_service.get_all_instances()
        return jsonify([{
            'id': instance.id,
            'port': instance.port,
            'status': instance.status.value,
            'service_status': instance.service_status,
            'config_path': instance.config_path,
            'data_dir': instance.data_dir,
            'created_at': instance.created_at.isoformat()
        } for instance in instances])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/redis/<redis_id>/status', methods=['GET'])
def get_redis_status(redis_id):
    try:
        status = redis_service.get_instance_status(redis_id)
        return jsonify(status)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def start_instances_in_background():
    redis_service.start_all_instances()

if __name__ == '__main__':
    thread = Thread(target=start_instances_in_background)
    thread.start()

    redis_service.sync_with_filesystem()
    app.run(host='0.0.0.0', port=14911)
