# test_queue.py
import redis
from rq import Queue
from app.tasks import send_whatsapp_reminder # Importa nossa função de tarefa

# Conecta ao mesmo Redis que o worker
redis_conn = redis.from_url('redis://localhost:6379')
q = Queue(connection=redis_conn)

# Enfileira uma nova tarefa para ser executada pelo worker
job = q.enqueue(send_whatsapp_reminder, 12345) # Passa o nome da função e seus argumentos
print(f"Tarefa adicionada à fila! ID do Job: {job.id}")