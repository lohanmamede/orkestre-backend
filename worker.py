# worker.py
# Este script inicia um worker RQ compatível com Windows, usando SimpleWorker.

import os
import redis
from rq import Queue
from rq.worker import SimpleWorker as Worker  # Importa o SimpleWorker como nossa classe de Worker
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Define em qual fila este worker vai "escutar" por tarefas
listen = ['default']

# Pega a URL do Redis das variáveis de ambiente
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Estabelece a conexão com o Redis
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    # Cria uma instância das filas que o worker vai escutar
    queues = [Queue(name, connection=conn) for name in listen]
    
    # Cria um worker simples que não usa os.fork() e é compatível com Windows
    worker = Worker(queues, connection=conn)
    
    print(f"Worker SIMPLES iniciado (compatível com Windows)...")
    print(f"Escutando nas filas: {', '.join(listen)}")
    
    # Inicia o loop de trabalho do worker.
    # O burst=True faz com que ele execute os jobs na fila e depois saia, 
    # o que é uma forma segura de evitar problemas de timeout no Windows.
    # Para um worker contínuo, precisaríamos de um loop while ou um agendador de tarefas do sistema.
    # Por agora, para testar e para o desenvolvimento, o burst é suficiente.
    worker.work(burst=True)