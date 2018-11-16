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
from utils import *
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

def retrieve_journals_from_titles(stub, withText = 0, titleIds = []):
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
		page_num = page.id[page.id.rfind("_") + 1:] 
		if page.title_id != prev_title: 
			if not first: # Yield what we have currently before creating a new journal 
				yield journal 
			else: 
				first = False 
			journal = Journal(page.title_id) # Create a new journal without information about its id, path, or language 
			prev_title = page.title_id 
		if withText == 1: 
			journal.add_page(page_num, page.names, str(page.text))
		else: 
			journal.add_names(page_num, page.names)

def retrieve_journals(stub, withText = 0): 
	""" Retrieves the pages belonging to all of the journals in the database, collects them into Journal objects, and streams them back to the caller """ 
	titles = stub.Titles(protob_pb2.TitlesOpt())
	for title in titles: 
		pagesOpt = protob_pb2.PagesOpt(with_text = withText, title_ids = [title.id])
		journal = Journal(title.archive_id, title.id, title.path, title.lang)
		for page in stub.Pages(pagesOpt): # A stream of Page objects 
			page_num = int(page.id[page.id.rfind("_") + 1:])
			if withText == 1: 
				journal.add_page(page_num, page.names, str(page.text))
			else: 
				journal.add_names(page_num, page.names)
		yield journal

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
		""" 
		num_Journals = 10
		titles = []
		for title in Titles(stub):
			if num_Journals < 0: 
				break 
			titles.append(title)
			num_Journals -= 1
		"""
		for journal in retrieve_journals(stub, withText = 0): 
			verified, seen, ratio = journal.get_verified_ratio()
			print("Verified: {}\tSeen: {}\tRatio:{}".format(verified, seen, ratio))
			journal.write_to_file(journalsPath)

def collect_journals(filepath): 
	""" Aggregates the different volumes of a Journal into a single JournalCollection item, which summarizes the attributes of each volume

	Currently the only data that we are interested in is the Verified to Unverified Ratio of each Journal 

	Input: 
		filepath: A (valid) file. The lines of the file should alternate between "journal name" and "ratio"
	Output: 
		A dictionary that maps the Journal Name to a JournalCollection object 
	""" 
	journalCollections = dict() 
	with open(filepath, "r") as f: 
		while True: 
			name = f.readline() 
			verified = f.readline()
			names = f.readline() 
			ratio = f.readline() 
			if name == "": 
				break 
			name, edition = extract_journal(name)
			verified = float(verified.strip().split()[-1])
			names = float(names.strip().split()[-1])
			ratio = float(ratio.strip().split()[-1])
			journal = journalCollections.get(name, JournalCollection(name))
			journal.edition_to_verified_names[edition] = verified
			journal.edition_to_total_names[edition] = names
			journal.edition_to_ratio[edition] = ratio
			journalCollections[name] = journal
	return journalCollections

################################################### 
## Main
###################################################
journalsPath = "journal_data2.log"
collectionsPath = "journal_collections_data2.log"
if __name__ == "__main__":
	# run_client()
	journalCollections = collect_journals(journalsPath)
	for journalCollection in journalCollections.values():
		journalCollection.write_to_file(collectionsPath)

"""
# Old code for run_client
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
"""