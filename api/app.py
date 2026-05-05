from flask import Flask, request, jsonify
from flask_cors import CORS
import redis
import psycopg2
import json
import uuid
import logging
from datetime import datetime
from config import Config
from prometheus_flask_exporter import PrometheusMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Redis connection
redis_client = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    db=Config.REDIS_DB,
    decode_responses=True
)

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(Config.DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id VARCHAR(36) PRIMARY KEY,
                    task_type VARCHAR(50) NOT NULL,
                    payload JSONB,
                    status VARCHAR(20) DEFAULT 'pending',
                    result JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            conn.commit()
            cursor.close()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
        finally:
            conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # Check Redis
    try:
        redis_client.ping()
        health_status['services']['redis'] = 'healthy'
    except Exception as e:
        health_status['services']['redis'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Check PostgreSQL
    conn = get_db_connection()
    if conn:
        health_status['services']['postgres'] = 'healthy'
        conn.close()
    else:
        health_status['services']['postgres'] = 'unhealthy'
        health_status['status'] = 'degraded'
    
    # Check queue size
    try:
        queue_size = redis_client.llen('task_queue')
        health_status['queue_size'] = queue_size
    except:
        health_status['queue_size'] = 'unknown'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/api/tasks', methods=['POST'])
def submit_task():
    """Submit a new task to the queue"""
    try:
        data = request.get_json()
        
        if not data or 'task_type' not in data:
            return jsonify({'error': 'task_type is required'}), 400
        
        queue_size = redis_client.llen('task_queue')
        if queue_size >= Config.MAX_QUEUE_SIZE:
            return jsonify({'error': 'Queue is full'}), 503
        
        task_id = str(uuid.uuid4())
        task = {
            'id': task_id,
            'task_type': data['task_type'],
            'payload': data.get('payload', {}),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (id, task_type, payload, status)
                VALUES (%s, %s, %s, %s)
                """,
                (task_id, task['task_type'], json.dumps(task['payload']), 'pending')
            )
            conn.commit()
            cursor.close()
            conn.close()
        
        redis_client.rpush('task_queue', json.dumps(task))
        
        logger.info(f"Task submitted: {task_id}")
        
        return jsonify({
            'task_id': task_id,
            'status': 'queued',
            'message': 'Task submitted successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get task status and result"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database unavailable'}), 503
        
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, task_type, payload, status, result, 
                   created_at, updated_at, completed_at
            FROM tasks WHERE id = %s
            """,
            (task_id,)
        )
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Task not found'}), 404
        
        task = {
            'id': row[0],
            'task_type': row[1],
            'payload': row[2],
            'status': row[3],
            'result': row[4],
            'created_at': row[5].isoformat() if row[5] else None,
            'updated_at': row[6].isoformat() if row[6] else None,
            'completed_at': row[7].isoformat() if row[7] else None
        }
        
        return jsonify(task), 200
        
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    """List all tasks with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        status_filter = request.args.get('status')
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database unavailable'}), 503
        
        cursor = conn.cursor()
        
        if status_filter:
            query = """
                SELECT id, task_type, status, created_at, completed_at
                FROM tasks WHERE status = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (status_filter, per_page, offset))
        else:
            query = """
                SELECT id, task_type, status, created_at, completed_at
                FROM tasks
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (per_page, offset))
        
        rows = cursor.fetchall()
        
        count_query = "SELECT COUNT(*) FROM tasks"
        if status_filter:
            count_query += " WHERE status = %s"
            cursor.execute(count_query, (status_filter,))
        else:
            cursor.execute(count_query)
        
        total = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        tasks = [
            {
                'id': row[0],
                'task_type': row[1],
                'status': row[2],
                'created_at': row[3].isoformat() if row[3] else None,
                'completed_at': row[4].isoformat() if row[4] else None
            }
            for row in rows
        ]
        
        return jsonify({
            'tasks': tasks,
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def root():
    """Root endpoint with API info"""
    return jsonify({
        'service': 'Task Queue API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'submit_task': 'POST /api/tasks',
            'get_task': 'GET /api/tasks/<task_id>',
            'list_tasks': 'GET /api/tasks',
            'metrics': '/metrics'
        }
    })

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)