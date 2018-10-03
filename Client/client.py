import os, sys, inspect
import argparse
import grpc 
import re
# from Topic_Model import *

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.join(parentdir, "Protobuf")) # Hardcoding the directory that contains the .proto definition
sys.path.insert(0, os.path.join(parentdir, "Visualization"))

import protob_pb2
import protob_pb2_grpc
import my_service_pb2 as my_service_pb2
import my_service_pb2_grpc as my_service_pb2_grpc
import plotly_example
import bokeh_example

class Topic_Model():
    def __init__(self):
        channel = grpc.insecure_channel('localhost:5073')
        self.stub = my_service_pb2_grpc.MyServiceStub(channel)

    def topicModel(self, req):
    	print("Client function: topicModel() start executing:")
    	# return self.stub.topicModel(my_service_pb2.QueryRequest(page="test"))
    	return self.stub.topicModel(req)

class Journal():
	def __init__(self, title): 
		self.title = title
		self.num_pages = 0 
		self.pages_to_names = dict() 
		self.pages_to_text = dict() 

	def __str__(self): 
		out = self.title
		out += "\nNumber of Pages: {}".format(self.num_pages)
		# Other stuff 
		return out

	def add_page(self, page_number, names, text): 
		self.num_pages += 1
		self.pages_to_names[page_number] = names
		self.pages_to_text[page_number] = text

	def add_names(self, page_number, names):
		if page_number not in self.pages_to_names.keys(): # I don't like having to check it like this - calculate the hash of the page_number instead
			self.num_pages += 1 
		self.pages_to_names[page_number] = names 

	def add_text(self, page_number, text): 
		if page_number not in self.pages_to_text.keys(): # I don't like having to check it like this - calculate the hash of the page_number instead
			self.num_pages += 1 
		self.pages_to_names[page_number] = names 

def check_journal_name(journal1, journal2): 
	""" Compares the names of two page.title_id strings to see if they are from the same journal 
	
	Simply compares the first 5 characters in the string - if they are the same, 
	""" 
	pass

def pull_journals(stub, num_journals, with_text = 0):
	wt = protob_pb2.WithText(value = with_text)
	pages = stub.Pages(wt) 
	# r = re.compile("([a-zA-Z]+)([0-9]+)([a-zA-Z]+)")
	index = -1
	page_num = 1
	prev_title = "" 
	journals = [] 
	for page in pages: 
		if page.title_id != prev_title: 
			index += 1
			if index >= num_journals: 
				break 
			page_num = 1
			prev_title = page.title_id
			journals.append(Journal(page.title_id))
		if with_text == 1: 
			journals[index].add_page(page_num, page.names, str(page.text)) # Hand-waving the page number 
		else: 
			journals[index].add_names(page_num, page.names) # Hand-waving the page number 
		page_num += 1
	return journals

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
	title_list = []
	document = ""
	for page in pages:
		# print(page.title_id)
		temp_title_id = page.title_id
		document += str(page.text)
		if temp_title_id != title_id:
			i  = i + 1
			title_id = temp_title_id
			doc_list.append(document)
			title_list.append(title_id)
			# file_name = "Output" + str(i) + ".txt"
			# text_file = open(file_name, "w")
			# text_file.write(document)
			# text_file.close()
			document = ""
		if(i >= 100):
			break
	# tm = Topic_Model()
	# tm.train(doc_list, 3, 5)
	# tm.tf_idf()
	# tm.lda() 
	print(title_list)
	return doc_list

def run_client(): 
	doc_list = []
	host = '172.22.247.23:8888'
	with grpc.insecure_channel(host) as channel: 
		stub = protob_pb2_grpc.BHLIndexStub(channel)

		Ver(stub)
		# Pages(stub, with_text = 1)
		# doc_list = Pages(stub, with_text = 1)
		journals = pull_journals(stub, 100, with_text = 0)
		vis = plotly_example.Plotly_Visualization(tile_number = 1, tile_width = 10, tile_height = 10, journal_list = journals)
		vis.visualize_data()
		
	""" 
	print("Documents recieved from " + host)
	tm = Topic_Model()
	res = tm.topicModel(break_down_doc(doc_list))
	print(res.message)
	""" 

if __name__ == "__main__":
	run_client()