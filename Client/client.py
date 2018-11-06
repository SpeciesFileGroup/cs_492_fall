import os, sys, inspect
import argparse
import grpc 
import re
import difflib
import matplotlib.pyplot as plt
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
	id - the id of the journal in the database 
	title - the title of the journal 
	path - the filepath of the journal 
	lang - the language it was written in 

	pages_to_names - a dictionary that maps from the page in the journal to a list of NameString present on that page 
	pages_to_text - a dictionary that maps from the page in the journal to the text present on that page
					For now, the text is not processed at all before stored in the dictionary (i.e., still has whitespace characters)

	The length of these two dictionaries should always be the same and is equal to the number of pages in the dictionary
	""" 
	def __init__(self, title, id = 0, path = "" , lang = ""): 
		self.id = id 
		self.title = title
		self.path = path 
		self.lang = lang 

		self.pages_to_names = dict() 
		self.pages_to_text = dict() 

	def __str__(self): 
		out = self.title
		out += "\nNumber of Pages: {}".format(len(self.pages_to_names))		
		return out

	def add_page(self, page_number, names, text): 
		""" Adds the contents of a Page to the class dictionaries 

		Names are of type NameString and have the fields defined in the protocol buffer

		Input: 
			page_number: int32, the page number 
			names: protobuf repeated field, an iterable of the names identified on the page 
			text: string, the text on the page 
		""" 
		pageNames = self.pages_to_names.get(page_number, [])
		pageText = self.pages_to_text.get(page_number, "")

		for name in names: 
			pageNames.append(name)
		pageText += text 
		self.pages_to_names[page_number] = pageNames
		self.pages_to_text[page_number] = pageText

	def add_names(self, page_number, names):
		""" Adds the identified NameString objects on a Page to the page_to_names dictionary 
	
		Names are of type NameString and have the fields defined in the protocol buffer

		Input: 
			page_number: int32, the page number 
			names: protobuf repeated field, an iterable of the names identified on the page 
		""" 
		pageNames = self.pages_to_names.get(page_number, [])
		for name in names: 
			pageNames.append(name)
		self.pages_to_names[page_number] = pageNames

	def add_text(self, page_number, text): 
		""" Adds the Page's text to the page_to_text dictionary 

		Input: 
			page_number: int32, the page number 
			text: string, the text on the page 
		""" 
		pageText = self.pages_to_text.get(page_number, "")
		pageText += text 
		self.pages_to_text[page_number] = pageText

	def get_verified_ratio(self): 
		""" Returns the ratio of Verified Names to Unverified Names 

		A NameString is "verified" if the value of its MatchType field is equal to "EXACT", "CANONICAL_EXACT", or "PARTIAL_EXACT". If this field is empty or if it 
		is equal to "NONE", "CANONICAL_FUZZY", or "PARTIAL_FUZZY", it is considered "unverified"
		"""
		if len(self.pages_to_names) == 0: # There are no names in this journal 
			return 0 
		verified = (1, 2, 4) # The int values corresponding to "EXACT", "CANONICAL_EXACT", and "PARTIAL_EXACT" in the MatchType enum
		numVerified = 0
		numSeen = 0 
		for names in self.pages_to_names.values(): # Lists of NameString Objects
			numSeen += len(names)
			for name in names: 
				if name.match in verified: 
					numVerified += 1
		return numVerified / numSeen

def break_down_doc(doc_list):  
    reqs = []
    for doc in doc_list:	
        reqs.append(my_service_pb2.QueryRequest(page=doc))
    for req in reqs:
        yield req

def Ver(stub): 
	return stub.Ver(protob_pb2.Void()).value

def Pages(stub, withText = 0): 
	""" Streams back the pages to the caller """ 
	pagesOpt = protob_pb2.PagesOpt(with_text = withText, title_ids = []) 
	pages = stub.Pages(pagesOpt) # A stream of pages 

	for page in pages: 
		print(page.id)
		yield page 

def collect_journals_from_titles(stub, withText = 0, titleIds = []):
	""" Retrieves the pages belonging to the requested journals, collects them into Journal objects, and streams them back to the caller.

	The format of a page id is "JournalName_PageNumber". For example, "americanjournalo03amer_0497" indicates the journal name is "americanjournalo03amer" and we are 
	looking at page 0497. The page number corresponds to the keys the Journal object's dictionaries

	Inputs:
	withText - Either 0 or 1, indicating whether or not we want to stream the pages with their associated text. By default, we do not stream the page's associated text.
	titleIds - A list of journal ids that we are interested in. These correspond to the indices of the journals in the database. If this field is [], we collect 
				every journal 
	""" 
	pagesOpt = protob_pb2.PagesOpt(with_text = withText, title_ids = titleIds) 
	pages = stub.Pages(pagesOpt) # A stream of Page objects 

	prev_title = "" 
	first = True 
	journal = None 

	for page in pages:
		if page.title_id != prev_title: 
			if not first: # Yield what we have currently before creating a new journal 
				yield journal 
			else: 
				first = False 
			journal = Journal(page.title_id) # Create a new journal without information about its id, path, or language 
			prev_title = page.title_id 
		if withText == 1: 
			page_num = page.id[page.id.find("_") + 1:] 
			journal.add_page(page_num, page.names, str(page.text))
		else: 
			journal.add_names(page_num, page.names)

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
	host = '172.22.247.23:8888'
	with grpc.insecure_channel(host) as channel: 
		stub = protob_pb2_grpc.BHLIndexStub(channel)
		# num_Journals = 100
		titles = []
		for title in Titles(stub):
			# if num_Journals < 0: 
				# break 
			titles.append(title)
			# num_Journals -= 1

		total_names = 0
		names_verified_v1, names_verified_v2 = 0, 0

		prev_title = ''
		ratios_v1, ratios_v2, journal_names = [], [], []
		journals_seen = 0

		for journal in Pages(stub, withText = 0, titleIds = [x.id for x in titles]): 
			journals_seen += 1

			if prev_title != '':
				if difflib.SequenceMatcher(None, prev_title, journal.title).ratio() < 0.8:
					mob = re.search('\d', prev_title)

					if mob:
						journal_names.append(prev_title[:mob.start()])
					else:
						journal_names.append(prev_title)

					if total_names != 0:
						ratios_v1.append(names_verified_v1/total_names)
						ratios_v2.append(names_verified_v2/total_names)
					else:
						ratios_v1.append(0)
						ratios_v2.append(0)
					total_names, names_verified_v1, names_verified_v2 = 0, 0, 0

			for page_number in journal.pages_to_names:
				names_on_page = journal.pages_to_names[page_number]
				for name in names_on_page:
					total_names += 1

					if name.match == 1 or name.match == 2 or name.match == 4:
						names_verified_v1 += 1
					if name.match != 0:
						names_verified_v2 += 1
			
			prev_title = journal.title

			if len(journal_names) == 100:
				break

		plt.xlabel('Journals')
		plt.ylabel('Ratio of verified names to total names')

		x = [i for i in range(len(journal_names))]
		plt.plot(x, ratios_v1)

		plt.xticks(x, journal_names)
		plt.xticks(rotation = 60)
		plt.grid(True)
		plt.show()

		print('Journals seen: ' + str(journals_seen))


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

# Basically find a way to summarize all of the data wrt MatchType