from flask import Flask, request, jsonify, Response
import redis
import grpc
import dns_pb2
import dns_pb2_grpc
import matplotlib.pyplot as plt
import io
import time
import numpy as np
from collections import defaultdict
app = Flask(__name__)

redis_partitions = [
    redis.StrictRedis(host='redis-part1', port=6379, decode_responses=True),
    redis.StrictRedis(host='redis-part2', port=6379, decode_responses=True),
    redis.StrictRedis(host='redis-part3', port=6379, decode_responses=True),
    redis.StrictRedis(host='redis-part4', port=6379, decode_responses=True),
    redis.StrictRedis(host='redis-part5', port=6379, decode_responses=True),
    redis.StrictRedis(host='redis-part6', port=6379, decode_responses=True),
    redis.StrictRedis(host='redis-part7', port=6379, decode_responses=True),
    redis.StrictRedis(host='redis-part8', port=6379, decode_responses=True)
]

grpc_channel = grpc.insecure_channel('grpc-server:50051')
grpc_stub = dns_pb2_grpc.DNSResolverStub(grpc_channel)

# Variables para métricas

num_partitions = 2
hit_count = 0
miss_count = 0
response_times = []
partition_requests = [0] * 8  # Contador de peticiones por partición
query_frequency = defaultdict(int)  # Diccionario para contar consultas por dominio
def get_partition_index(domain_name):
    # Convertir el dominio a un valor numérico
    domain_value = sum(ord(c) for c in domain_name)
    
    # Asignar a una partición según el rango
    if num_partitions == 2:
        return 0 if domain_value % 2 == 0 else 1
    elif num_partitions == 4:
        return domain_value % 4
    elif num_partitions == 8:
        return domain_value % 8
    else:
        raise ValueError('Numero de particiones no soportado')

def get_redis_partition(domain_name):
    partition_index = get_partition_index(domain_name)
    partition_requests[partition_index] += 1  # Contar peticiones
    return redis_partitions[partition_index]
    

def resolve_dns(domain_name):
    # Conexión con el servidor gRPC
    try:
        response = grpc_stub.Resolve(dns_pb2.DomainRequest(domain_name=domain_name))
        if response.ip_address:
            return response.ip_address
    except grpc.RpcError as e:
        # Omitir cualquier operación si ocurre un error
        print(f"Error al resolver {domain_name}: {e}")
        return None

@app.route('/resolve', methods=['POST'])
def resolve_domain():
    global hit_count, miss_count
    domain_name = request.json['domain']
    partition = get_redis_partition(domain_name)


    start_time = time.time()  # Iniciar el cronómetro para tiempos de respuesta

    query_frequency[domain_name] += 1
    
    cached_ip = partition.get(domain_name)
    
    if cached_ip:
        hit_count += 1
        status = 'HIT'
        ip = cached_ip
    else:
        miss_count += 1
        ip = resolve_dns(domain_name)
        if ip:  # Si hay una IP válida
            partition.setex(domain_name, 360, ip)  # Guardar en Redis con TTL
            status = 'MISS'
        else:
             return '', 204

    end_time = time.time()  # Terminar cronómetro
    response_times.append(end_time - start_time)

    return jsonify({'status': status, 'ip': ip})

@app.route('/update-partitions', methods=['POST'])
def update_partitions():
    global num_partitions
    data = request.json
    new_partitions = data.get('partitions', 2)

    if new_partitions not in [2, 4, 8]:
        return jsonify({'status': 'error', 'message': 'El numero de particiones debe ser 2, 4 o 8'}), 400

    num_partitions = new_partitions
    return jsonify({'status': 'success', 'message': f'Numero de particiones actualizado a {new_partitions}'})

@app.route('/stats', methods=['GET'])
def hit_miss_graph():
    labels = ['HIT', 'MISS']
    counts = [hit_count, miss_count]
    hit_rate = hit_count / (hit_count + miss_count) * 100 if (hit_count + miss_count) > 0 else 0
    miss_rate = 100 - hit_rate

    # Gráfico de hit/miss rate
    fig, ax = plt.subplots()
    ax.bar(labels, counts, color=['green', 'red'])
    ax.set_ylabel('Cantidad de Consultas')
    ax.set_title('Gráfico de Hits vs Misses')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return Response(img, mimetype='image/png')

@app.route('/stats/response-time', methods=['GET'])
def response_time_graph():
    if response_times:
        avg_response_time = np.mean(response_times)
        std_response_time = np.std(response_times)
    else:
        avg_response_time = 0
        std_response_time = 0

    # Gráfico de tiempos de respuesta (promedio y desviación estándar)
    fig, ax = plt.subplots()
    ax.bar(['Promedio', 'Desviación Estándar'], [avg_response_time, std_response_time], color=['blue', 'orange'])
    ax.set_ylabel('Tiempo (segundos)')
    ax.set_title('Tiempos de Respuesta (Promedio y Desviación Estándar)')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return Response(img, mimetype='image/png')

@app.route('/stats/load-balance', methods=['GET'])
def load_balance_graph():
    labels = [f'Partición {i+1}' for i in range(num_partitions)]
    counts = partition_requests[:num_partitions]

    # Gráfico de balance de carga
    fig, ax = plt.subplots()
    ax.bar(labels, counts, color='purple')
    ax.set_ylabel('Cantidad de Peticiones')
    ax.set_title(f'Balance de Carga por Partición (Total: {num_partitions})')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return Response(img, mimetype='image/png')
@app.route('/stats/query-frequency-graph', methods=['GET'])
def query_frequency_graph():
    # Obtener los datos de frecuencia y ordenarlos
    domains = list(query_frequency.keys())
    frequencies = list(query_frequency.values())

    # Gráfico de distribución de frecuencias
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(domains, frequencies, color='blue')
    ax.set_xlabel('Frecuencia de Consultas')
    ax.set_title('Distribución de Frecuencias de Consultas por Dominio')
    ax.set_xlim(0, max(frequencies) + 1)  # Asegurar que hay espacio en la gráfica

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    return Response(img, mimetype='image/png')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
