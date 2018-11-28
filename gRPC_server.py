#title           :gRPC_server.py
#author          :Herbert Wang
#date            :20181120
#notes           :stand alone server that take stream of pages from a gRPC client, a plungin idea demonstration
#usage           :python gRPC_server.py
#python_version  :Python 2.7.15rc1
#==============================================================================
from concurrent import futures
import time
import grpc
import my_service_pb2 as my_service_pb2
import my_service_pb2_grpc as my_service_pb2_grpc
from Topic_Model import *

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class gRPCServer(my_service_pb2_grpc.MyServiceServicer):
    def __init__(self):
        print('Topic Model Server Initialization')

    # Upon receiving stream of pages from client, call topic model library and stream result back
    # This is a poin of demonstration of a gRPC plungin  
    def topicModel(self, request_iterator, context):
        print("topicModel() start recieving stream")
        doc_list = [] 
        ret = ""
        for i in request_iterator:
            doc_list.append(i.page)
        tm = Topic_Model()
        tm.train(doc_list, 3, 5)
        ret += tm.tf_idf()
        ret += tm.lda() 
        return my_service_pb2.QueryResponse(message=ret)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    my_service_pb2_grpc.add_MyServiceServicer_to_server(gRPCServer(), server)
    server.add_insecure_port('[::]:5003')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()