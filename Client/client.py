import os, sys, inspect
import argparse
import grpc 
# from Topic_Model import *

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.join(parentdir, "Protobuf")) # Hardcoding the directory that contains the .proto definition

import protob_pb2
import protob_pb2_grpc
import my_service_pb2 as my_service_pb2
import my_service_pb2_grpc as my_service_pb2_grpc

class Topic_Model():
    def __init__(self):
        channel = grpc.insecure_channel('localhost:5073')
        self.stub = my_service_pb2_grpc.MyServiceStub(channel)

    def topicModel(self, req):
    	print("Client function: topicModel() start executing:")
    	# return self.stub.topicModel(my_service_pb2.QueryRequest(page="test"))
    	return self.stub.topicModel(req)

def break_down_doc(doc_list):  
    reqs = []
    for doc in doc_list:	
        reqs.append(my_service_pb2.QueryRequest(page=doc))
    for req in reqs:
        yield req

def Ver(stub): 
	return stub.Ver(protob_pb2.Void()).value

def Pages(stub, with_text = 1):
	wt = protob_pb2.WithText(value = with_text)
	pages = stub.Pages(wt)
	title_id = ""
	i = 0
	doc_list = []
	document = ""
	for page in pages:
		temp_title_id = page.title_id
		document += page.text
		if temp_title_id != title_id:
			i  = i + 1
			title_id = temp_title_id
			doc_list.append(document)
			# file_name = "Output" + str(i) + ".txt"
			# text_file = open(file_name, "w")
			# text_file.write(document)
			# text_file.close()
			document = ""
		if(i >= 5):
			break
	# tm = Topic_Model()
	# tm.train(doc_list, 3, 5)
	# tm.tf_idf()
	# tm.lda() 
	return doc_list

def run_client(): 
	doc_list = []
	host = '172.22.247.23:8888'
	with grpc.insecure_channel(host) as channel: 
		stub = protob_pb2_grpc.BHLIndexStub(channel)

		Ver(stub)
		doc_list = Pages(stub, with_text = 1)

	print("Documents recieved from " + host)
	tm = Topic_Model()
	res = tm.topicModel(break_down_doc(doc_list))
	print(res.message)

if __name__ == "__main__":
	run_client()