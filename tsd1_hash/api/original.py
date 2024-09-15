from flask import Flask, request, jsonify, Response
import redis
import grpc
import dns_pb2
import dns_pb2_grpc
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Conexiones a Redis
redis_part1 = redis.StrictRedis(host='redis-part1', port=6379, decode_responses=True)
redis_part2 = redis.StrictRedis(host='redis-part2', port=6379, decode_responses=True)

# Contadores de hits y misses
hit_count = 0
miss_count = 0

def get_redis_partition(domain_name):
    # Implementación de partición simple por hash
    return redis_part1 if hash(domain_name) % 2 == 0 else redis_part2

def resolve_dns(domain_name):
    # Conexión con el servidor gRPC
    with grpc.insecure_channel('grpc-server:50051') as channel:
        stub = dns_pb2_grpc.DNSResolverStub(channel)
        response = stub.Resolve(dns_pb2.DomainRequest(domain_name=domain_name))
        return response.ip_address

@app.route('/resolve', methods=['POST'])
def resolve_domain():
    global hit_count, miss_count
    domain_name = request.json['domain']
    partition = get_redis_partition(domain_name)
    cached_ip = partition.get(domain_name)

    if cached_ip:
        hit_count += 1  # Incrementar contador de hits
        return jsonify({'status': 'HIT', 'ip': cached_ip})
    else:
        miss_count += 1  # Incrementar contador de misses
        ip = resolve_dns(domain_name)
        partition.setex(domain_name, 3600, ip)  # Guardar con TTL de 1 hora
        return jsonify({'status': 'MISS', 'ip': ip})

@app.route('/stats/hit-miss-graph', methods=['GET'])
def hit_miss_graph():
    # Crear la gráfica de hits vs misses
    labels = ['HIT', 'MISS']
    counts = [hit_count, miss_count]
    
    fig, ax = plt.subplots()
    ax.bar(labels, counts, color=['green', 'red'])
    ax.set_ylabel('Cantidad de Consultas')
    ax.set_title('Gráfico de Hits vs Misses')

    # Guardar la gráfica en un objeto de memoria
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Devolver la gráfica como imagen PNG
    return Response(img, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
