from grpc_client import * 
from data_formats import * 
from nltk.classify import textcat
import json, re

if __name__ == "__main__": 
    f_out = "data_with_languages.json"
    language_classifier = textcat.TextCat()
    journalCollections = dict() 

    host = "172.22.247.23:8888" 
    with grpc.insecure_channel(host) as channel: 
        stub = protob_pb2_grpc.BHLIndexStub(channel)
        for title in Titles(stub): 
            text = "" 
            text_index = 10
            journal = Journal(title) 
            for page in Pages(stub, withText = True, titles = [title.id]):
                if text_index > 0: 
                    txt = page.text 
                    txt = txt.replace(b'\r', b'')
                    txt = txt.replace(b'\n', b'')
                    txt = txt.decode("ascii", "ignore")
                    text += re.sub(r'[^\w]', ' ', txt) # Removes all non-alphanumeric characters
                    text += " "
                journal.add_page(page)
                text_index -= 1
            # Classifying the language parameter 
            journal.lang = language_classifier.guess_language(text.lower())
            print(journal.title, "\t", journal.lang)
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