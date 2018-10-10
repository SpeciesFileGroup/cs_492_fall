import time
from concurrent import futures
import grpc
import viz_stream_pb2 as viz_stream_pb2
import viz_stream_pb2_grpc as viz_stream_pb2_grpc
import plotly_example

class gRPCServer(viz_stream_pb2_grpc.VizStreamServicer):
    def __init__(self):
        print('Initializating server...')

    def Visualize(self, request_iterator, context):
        print('Visualizer starts receiving Journals to stream')

        for journal in request_iterator:
            pass

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    my_service_pb2_grpc.add_VizStreamServicer_to_server(
        gRPCServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()

    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()