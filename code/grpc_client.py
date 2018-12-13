import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
sys.path.insert(0, os.path.join(parentdir, "Protobuf")) # Hardcoding the directory that contains the .proto definition

import grpc 
import protob_pb2
import protob_pb2_grpc

"""
Implementation of the three RPC services defined in protob.proto 
"""
def Ver(stub): 
    """ Implements the Ver RPC service. Returns the Version. """
    return stub.Ver(protob_pb2.Void()).value

def Pages(stub, withText = False, titles = []): 
    """ Implements the Pages RPC service. Streams Page objects back to the caller.

    If the caller provides a list of Journal titles, they will receive the pages corresponding to those journals. 
    Otherwise, they will receive every page in the database.
    """
    pagesOpt = protob_pb2.PagesOpt(with_text = withText, title_ids = titles)
    pages = stub.Pages(pagesOpt) # A stream of Pages 

    for page in pages: 
        yield page 
        """ 
        if not withText: 
            yield page 
        else: # Decoding from bytes to string 
            text = page.text 
            text = text.replace(b'\r', b'')
            text = text.replace(b'\n', b'')
            text = text.decode("ascii", "ignore")
            page.text = text 
            yield page
        """ 

def Titles(stub): 
    """ Implements the Titles RPC service. Streams Title objects back to the caller. Each Title object carries information about a single Journal """ 
    titles = stub.Titles(protob_pb2.TitlesOpt()) # A stream of Titles 
    for title in titles: 
        yield title

def start_client(): 
    # This doesn't work since the Context Manager closes upon return
    host = "172.22.247.23:8888" 
    with grpc.insecure_channel(host) as channel: 
        stub = protob_pb2_grpc.BHLIndexStub(channel)
        return stub 