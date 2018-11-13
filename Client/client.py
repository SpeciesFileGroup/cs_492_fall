import os, sys, inspect
import argparse
import grpc
import logging
import json
from multiprocessing import Pool
from geo_mine import geo
from geo_mine import nltk_mine
from geo_mine import nltk_dist
# from Topic_Model import *

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.join(parentdir, "Protobuf")) # Hardcoding the directory that contains the .proto definition

import protob_pb2
import protob_pb2_grpc
import my_service_pb2 as my_service_pb2
import my_service_pb2_grpc as my_service_pb2_grpc
import logging
divider = "======================================================================="

class Topic_Model():
    def __init__(self):
        channel = grpc.insecure_channel('localhost:5003')
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
def myprint(input):
	print(divider)
	print(input)
	print(divider)

def Ver(stub): 
	return stub.Ver(protob_pb2.Void()).value

def path_split(name_string):
	myset = set()
	# for i in name_string:
	# 	if i.path != '':
	# 		myset.update(i.path.split('|'))
	# return myset
	for i in name_string:
		myset.add(str(i.value))
	return list(myset)

def Pages(stub, with_text = 1):
	wt = protob_pb2.WithText(value = with_text)
	pages = stub.Pages(wt)
	title_id = ""
	i = 0
	doc_list = []
	document = ""

	# f = open("myfile.txt", "w+")
	myset = set()
	mydic = {}
	record = 0
	agents = 4
	for page in pages:
		temp_title_id = page.title_id
		record += 1
		print("Number of pages processed: " + str(record))
		list_value = path_split(page.names)
		# print(list_value)
		ret = nltk_dist(page.text, path_split(page.names))
		for ret_key in ret:
			if ret_key not in mydic:
				mydic.update({ret_key: ret[ret_key]})
			else:
				mydic[ret_key].append(ret[ret_key])
		# for key in path_split(page.names):
		# 	if key not in mydic:
		# 		mydic[key] = {}
		# 	for j in geo(page.text):
		# 		if j not in mydic[key]:
		# 			mydic[key][j] = 1
		# 		else:
		# 			mydic[key][j] += 1
		document += page.text
		if temp_title_id != title_id:
			i  = i + 1
			title_id = temp_title_id
			doc_list.append(document) 
			# f.write(document)
		if record >= 10000:
			break

	# for i in mydic:
	# 	ret = []
	# 	for j in (sorted(mydic[i], key=mydic[i].get, reverse=True)[:3]):
	# 		ret.append((j, mydic[i][j]))
	# 	mydic[i] = ret

	# f.close()
	print(mydic)
	with open('my_dict.json', 'w') as f:
		json.dump(mydic, f)
	return doc_list

def run_client(): 
	doc_list = []
	host = '172.22.247.23:8888'
	with grpc.insecure_channel(host) as channel: 
		stub = protob_pb2_grpc.BHLIndexStub(channel)

		Ver(stub)
		doc_list = Pages(stub, with_text = 1)

	print("Documents recieved from " + host)
	# tm = Topic_Model()
	# res = tm.topicModel(break_down_doc(doc_list))
	# print(res.message)

if __name__ == "__main__":
	run_client()