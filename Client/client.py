import os, sys, inspect
import argparse
import grpc 

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.join(parentdir, "Protobuf")) # Hardcoding the directory that contains the .proto definition

import protob_pb2
import protob_pb2_grpc


def Ver(stub): 
	return stub.Ver(protob_pb2.Void()).value

def Pages(stub, with_text = 1):
	wt = protob_pb2.WithText(value = with_text)
	pages = stub.Pages(wt)

	for page in pages:
		print(page.title_id)	

	# We can pull the entire database down using this 
	# Probably want to collect them based on title

def run_client(): 
	with grpc.insecure_channel('172.22.247.23:8888') as channel: 
		stub = protob_pb2_grpc.BHLIndexStub(channel)

		Ver(stub)
		Pages(stub, with_text = 1)

if __name__ == "__main__":
	# Use argparse to make this into more of a CLI

	run_client()