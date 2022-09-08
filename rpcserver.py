from concurrent import futures
import grpc
from api import compute_pb2_grpc
import compute

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    compute_pb2_grpc.add_ComputeServicer_to_server(compute.Compute(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    run()