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
	""" A representation of a BHL Scientific Journal. Contains a collection of the names and text that exists in the journal. 

	Class Attributes: 
	title - the title of the journal 
	num_pages - the number of pages in the journal
	pages_to_names - a dictionary that maps from the page in the journal (indexed from 0) to a list of names present on that page 
	pages_to_text - a dictionary that maps from the page in the journal (indexed from 0) to the text present on that page
					For now, the text is not processed at all before stored in the dictionary (i.e., still has whitespace characters)
	""" 
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

def break_down_doc(doc_list):  
    reqs = []
    for doc in doc_list:	
        reqs.append(my_service_pb2.QueryRequest(page=doc))
    for req in reqs:
        yield req

def Ver(stub): 
	return stub.Ver(protob_pb2.Void()).value

def Pages(stub, withText = 1, titleIds = []): 
	""" Retrieves the pages belonging to the requested journals and streams it back to the caller 

	By default, we stream all of the pages with their associated text

	Inputs:
	withText - Either 0 or 1, indicating whether or not we want to stream the pages with their associated text 
	titleIds - A list of journal ids that we are interested in. These correspond to the indices of the journals in the database
	""" 
	pagesOpt = protob_pb2.PagesOpt(with_text = withText, title_ids = titleIds) 
	pages = stub.Pages(pagesOpt) # A stream of pages 

	prev_title = "" 
	first = True 
	journal = None 

	for page in pages: 
		if page.title_id != prev_title: 
			if not first: # Yield what we have currently before creating a new journal 
				yield journal 
			else: 
				first = False 
			journal = Journal(page.title_id) # Create a new journal 
			prev_title = page.title_id 
			page_num = 1
		if withText == 1: 
			journal.add_page(page_num, page.names, str(page.text))
		else: 
			journal.add_names(page_num, page.names)
		page_num += 1

"""
# Old code that uses the previous Protocol Buffer definition
# May be useful as reference 
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
"""

def Titles(stub): 
	""" Implements the Titles rpc defined in protob.proto 

	Sends no parameters to the server and receives a list of all of the Journal titles that exist on the server's database 
	Each Title received from the server contains a unique id, its archive_id, its filepath on the server, and the language 
	the Journal was written in. 
	""" 
	titles = stub.Titles(protob_pb2.TitlesOpt())
	for title in titles:
		yield title

def run_client(): 
	doc_list = []
	host = '172.22.247.23:8888'
	with grpc.insecure_channel(host) as channel: 
		stub = protob_pb2_grpc.BHLIndexStub(channel)
		for title in Titles(stub):
			print(title)
		
		# Ver(stub)
		# Pages(stub, with_text = 1)
		# doc_list = Pages(stub, with_text = 1)
		# journals = pull_journals(stub, 100, with_text = 0)
		# vis = plotly_example.Plotly_Visualization(tile_number = 1, tile_width = 10, tile_height = 10, journal_list = journals)
		# vis.visualize_data()
		
	""" 
	print("Documents recieved from " + host)
	tm = Topic_Model()
	res = tm.topicModel(break_down_doc(doc_list))
	print(res.message)
	""" 

if __name__ == "__main__":
	run_client()