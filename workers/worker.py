import redis
import psycopg2
import json
import time
import logging
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
POSTGRES_DB = os.getenv('POSTGRES_DB', 'taskqueue')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Graceful shutdown flag
shutdown_flag = False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global shutdown_flag
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_flag = True

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

# Redis connection
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def process_task(task):
    """Process a task based on its type"""
    task_type = task.get('task_type')
    payload = task.get('payload', {})
    
    logger.info(f"Processing task {task['id']} of type {task_type}")
    
    try:
        # Different task type handlers
        if task_type == 'calculate':
            result = calculate_task(payload)
        elif task_type == 'transform':
            result = transform_task(payload)
        elif task_type == 'aggregate':
            result = aggregate_task(payload)
        else:
            result = default_task(payload)
        
        return {'status': 'success', 'result': result}
        
    except Exception as e:
        logger.error(f"Error processing task {task['id']}: {e}")
        return {'status': 'error', 'error': str(e)}

def calculate_task(payload):
    """Example: Perform calculation"""
    time.sleep(2)  # Simulate work
    
    numbers = payload.get('numbers', [])
    operation = payload.get('operation', 'sum')
    
    if operation == 'sum':
        return {'result': sum(numbers)}
    elif operation == 'product':
        result = 1
        for n in numbers:
            result *= n
        return {'result': result}
    elif operation == 'average':
        return {'result': sum(numbers) / len(numbers) if numbers else 0}
    else:
        return {'result': len(numbers)}

def transform_task(payload):
    """Example: Transform data"""
    time.sleep(1)  # Simulate work
    
    data = payload.get('data', '')
    operation = payload.get('operation', 'uppercase')
    
    if operation == 'uppercase':
        return {'result': data.upper()}
    elif operation == 'lowercase':
        return {'result': data.lower()}
    elif operation == 'reverse':
        return {'result': data[::-1]}
    elif operation == 'wordcount':
        return {'result': len(data.split())}
    else:
        return {'result': data}

def aggregate_task(payload):
    """Example: Aggregate data"""
    time.sleep(3)  # Simulate longer work
    
    items = payload.get('items', [])
    return {
        'count': len(items),
        'unique': len(set(items)),
        'sample': items[:5] if len(items) > 5 else items
    }

def default_task(payload):
    """Default task handler"""
    time.sleep(1)
    return {'message': 'Task processed', 'payload': payload}

def update_task_status(task_id, status, result=None):
    """Update task status in database"""
    conn = get_db_connection()
    if not conn:
        logger.error(f"Cannot update task {task_id}: Database unavailable")
        return
    
    try:
        cursor = conn.cursor()
        
        if status == 'completed':
            cursor.execute(
                """
                UPDATE tasks 
                SET status = %s, result = %s, updated_at = %s, completed_at = %s
                WHERE id = %s
                """,
                (status, json.dumps(result), datetime.utcnow(), datetime.utcnow(), task_id)
            )
        else:
            cursor.execute(
                """
                UPDATE tasks 
                SET status = %s, updated_at = %s
                WHERE id = %s
                """,
                (status, datetime.utcnow(), task_id)
            )
        
        conn.commit()
        cursor.close()
        logger.info(f"Task {task_id} status updated to {status}")
        
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
    finally:
        conn.close()

def worker_loop():
    """Main worker loop"""
    logger.info("Worker started, waiting for tasks...")
    
    while not shutdown_flag:
        try:
            # Blocking pop with timeout
            task_data = redis_client.blpop('task_queue', timeout=1)
            
            if not task_data:
                continue
            
            # Parse task
            task = json.loads(task_data[1])
            task_id = task['id']
            
            logger.info(f"Picked up task {task_id}")
            
            # Update status to processing
            update_task_status(task_id, 'processing')
            
            # Process task
            result = process_task(task)
            
            # Update status to completed
            update_task_status(task_id, 'completed', result)
            
            logger.info(f"Task {task_id} completed successfully")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid task format: {e}")
        except Exception as e:
            logger.error(f"Worker error: {e}")
            time.sleep(1)
    
    logger.info("Worker shutting down gracefully...")

if __name__ == '__main__':
    try:
        # Test connections
        redis_client.ping()
        logger.info("Connected to Redis")
        
        conn = get_db_connection()
        if conn:
            conn.close()
            logger.info("Connected to PostgreSQL")
        
        # Start worker
        worker_loop()
        
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
    except Exception as e:
        logger.error(f"Worker startup error: {e}")
        sys.exit(1)