from flask import Flask, jsonify, request
from infra.database import Database
from infra.repository import RedisRepository
from domain.redis.service import RedisService

app = Flask(__name__)

# Initialize dependencies
database = Database()
repository = RedisRepository(database)
redis_service = RedisService(repository)

@app.route('/redis/create', methods=['POST'])
def create_redis():
    data = request.get_json()
    redis_id = data.get('redis_id')
    port = data.get('port')
    
    if not redis_id or not port:
        return jsonify({'error': 'redis_id and port are required'}), 400
    
    try:
        instance = redis_service.create_instance(redis_id, port)
        return jsonify({
            'message': f'Redis instance {redis_id} created successfully',
            'config_path': instance.config_path,
            'data_dir': instance.data_dir,
            'port': instance.port
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/redis/delete/<redis_id>', methods=['DELETE'])
def delete_redis(redis_id):
    try:
        redis_service.delete_instance(redis_id)
        return jsonify({'message': f'Redis instance {redis_id} deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/redis/<redis_id>/start')
def start_redis(redis_id):
    try:
        instance = redis_service.start_instance(redis_id)
        return jsonify({
            'message': f'Redis {redis_id} started successfully',
            'port': instance.port
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/redis/<redis_id>/stop')
def stop_redis(redis_id):
    try:
        instance = redis_service.stop_instance(redis_id)
        return jsonify({'message': f'Redis {redis_id} stopped successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/redis/status')
def redis_status():
    instances = redis_service.get_all_instances()
    status = {}
    for instance in instances:
        process = ProcessManager.find_redis_process(instance.port)
        status[instance.id] = {
            'running': process is not None,
            'pid': process.pid if process else None,
            'port': instance.port,
            'config_path': instance.config_path,
            'data_dir': instance.data_dir,
            'created_at': instance.created_at.isoformat()
        }
    return jsonify(status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)