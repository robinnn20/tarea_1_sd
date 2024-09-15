import subprocess
from concurrent import futures
import grpc
import dns_pb2
import dns_pb2_grpc

class DNSResolverServicer(dns_pb2_grpc.DNSResolverServicer):
    def Resolve(self, request, context):
        domain = request.domain_name
        result = subprocess.run(["dig", "+short", domain], capture_output=True, text=True)
        ip = result.stdout.strip()
        return dns_pb2.DNSResponse(ip_address=ip)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dns_pb2_grpc.add_DNSResolverServicer_to_server(DNSResolverServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
