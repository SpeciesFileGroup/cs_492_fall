from grpc_client import * 
from data_formats import * 
import json, re

if __name__ == "__main__": 
    f_out = "data2.json"
    journalCollections = dict() 

    host = "172.22.247.23:8888" 
    with grpc.insecure_channel(host) as channel: 
        stub = protob_pb2_grpc.BHLIndexStub(channel)
        for title in Titles(stub): 
            print(title.archive_id)
            journal = Journal(title) 
            for page in Pages(stub, titles = [title.id]):
                journal.add_page(page)
            match = re.search("\d+", journal.title)
            if match == None: 
                jc_title = journal.title
            else: 
                jc_title = journal.title[:match.start()]
            jc = journalCollections.get(jc_title, JournalCollection(jc_title))
            jc.add_volume(journal)
            journalCollections[jc_title] = jc
        out = dict() 
        jcs = [] 
        for jc in journalCollections.values(): 
            jcs.append(jc.convert_to_dict())
        out["journalCollections"] = jcs
        with open(f_out, "w") as f: 
            json.dump(out, f)