import re
import json

class Name():
    """ A representation of a name in a BHL Scientific Journal. Corresponds to the NameString data type defined in the Protocol Buffer. 

    NameString objects seldom have values assigned to all of their fields. In those cases, we default to the type-specific default value. 
    For example, most NameString objects don't have a value for the edit_distance field - in that case, we assume an edit_distance of 0. 
    This conforms with the Protocol Buffer specification
    """ 
    def __init__(self, nameString):
        """ Initializes a Name object from a collection of data received from the gRPC stream """
        self.value = nameString.value 
        self.odds = nameString.odds
        self.path = nameString.path
        self.curated = nameString.curated
        self.edit_distance = nameString.edit_distance
        self.edit_distance_stem = nameString.edit_distance_stem
        self.source_id = nameString.source_id
        self.match = nameString.match 
        self.offset_start = nameString.offset_start 
        self.offset_end = nameString.offset_end 

    def convertToDict(self): 
        """ Converts the contents of a Name object to a dictionary in order serialize to JSON """ 
        out = dict()
        out["Value"] = self.value 
        out["Odds"] = self.odds 
        out["Path"] = self.path
        out["Curated"] = self.curated 
        out["Edit Distance"] = self.edit_distance 
        out["Edit Distance Stem"] = self.edit_distance_stem
        out["Source ID"] = self.source_id
        out["Match"] = self.match 
        out["Offset Start"] = self.offset_start 
        out["Offset End"] = self.offset_end
        return out 

class Page():
    """ A representation of a page in a BHL Scientific Journal. 
    
    Corresponds to the Page data type defined in the Protocol Buffer. However, some values in the Protocol Buffer are not used: 
        - title_id is the name of the journal. Since Pages will be collected into Journal objects that already store this value, this is ignored 
        - title_path is the filepath of the journal. This is ignored for the same reason as title_id

    Additionally, while the offset variable is stored, it's not used for anything at the moment
    """ 

    def __init__(self, page): 
        """ Initializes a Page object from a collection of data received from the gRPC stream """ 
        self.page_num = page.id[page.id.rfind("_") + 1:]
        self.offset = page.offset
        text = page.text
        text = text.replace(b'\r', b'')
        text = text.replace(b'\n', b'') # Cleaning up the contents of the bytes 
        self.text = text.decode("ascii", "ignore") # Converting from bytes to string
        self.names = [] 
        for nameString in page.names: 
            name = Name(nameString)  
            self.names.append(name)

    def convertToDict(self): 
        out = dict() 
        out["Page Number"] = self.page_num
        out["Offset"] = self.offset 
        out["Text"] = self.text
        names = [] 
        for name in self.names: 
            names.append(name.convertToDict())
        out["Names"] = names
        return out 

class Journal():
    """ A representation of a BHL Scientific Journal.

    Mostly corresponds to the Title data type defined in the Protocol Buffer, but also contains a collection of Page objects. These are the pages of the journal. 

    Class Attributes: 
    id - the id of the journal in the database
    title - the title of the journal, corresponds to the archive_id attribute in the Protobuf
    path - the filepath of the journal 
    lang - the language it was written in 
    pages - a list of Page objects 
    """ 
    def __init__(self, edition): 
        self.title = edition.archive_id
        self.id = edition.id 
        self.path = edition.path
        self.lang = edition.lang 
        self.pages = [] 

    def __str__(self): 
        out = self.title
        out += "\nNumber of Pages: {}".format(len(self.pages))     
        return out

    def add_page(self, page): 
        """ Adds the contents of a Page to the list of pages
        
        page should be directly received from the gRPC string, not a Page object 
        """ 
        self.pages.append(Page(page))

    def get_verified_ratio(self): 
        """ Returns the ratio of Verified Names to Unverified Names 

        NOTE: modified to also return the numVerified and numSeen values

        A NameString is "verified" if the value of its MatchType field is equal to "EXACT", "CANONICAL_EXACT", or "PARTIAL_EXACT". If this field is empty or if it 
        is equal to "NONE", "CANONICAL_FUZZY", or "PARTIAL_FUZZY", it is considered "unverified"
        """
        if len(self.pages) == 0: # There are no pages in this journal 
            return 0, 0, 0
        verified = (1, 2, 4) 
        numVerified = 0 
        numSeen = 0 
        for page in self.pages: 
            numSeen += len(page.names) # page.names is a list of Name objects 
            for name in page.names: 
                if name.match in verified: 
                    numVerified += 1
        if numSeen == 0: # No names in any of the pages of the journal 
            return 0, 0, 0
        return numVerified, numSeen, numVerified / numSeen 

    def write_to_file(self, filepath, mode = "a"): 
        """ Writes the contents of this Journal object to the specified filepath using the specified mode

        Currently writes the Journal's title and its Verified to Unverified Ratio 

        Inputs:
            filepath: string, a (valid) filepath  
            mode: the access mode that we want to open the file with. This is set to append by default. 
        """ 
        if "r" in mode: 
            print("Only accepts write and append modes")
            return 
        with open(filepath, mode) as f: 
            f.write("{}\n".format(self.title))
            verified, seen, ratio = self.get_verified_ratio()
            f.write("Verified Names: {}\n".format(str(verified)))
            f.write("Names: {}\n".format(str(seen)))
            f.write("Ratio: {}\n".format(str(ratio)))

    def convertToDict(self, withTitle = False): 
        """ Converts the contents of a Journal object to a dictionary in order to serialize to JSON """ 
        out = dict() 
        if withTitle:
            out["Title"] = self.title
        out["ID"] = self.id
        out["Path"] = self.path 
        out["Language"] = self.lang
        pages = [] 
        for page in self.pages: 
            pages.append(page.convertToDict())
        out["Pages"] = pages
        return out

class JournalCollection(): 
    """ Conglomerates journals together so that we don't have a million data points 
    
    For example, americanjournalo02amer, americanjournalo03amer, americanjournalo05amer, and americanjournalo06amer are different versions 
    of the americanjournal. Instead of having one data point for each, we put all 4 together into the same collection. 
    
    For now, we are only combining the Verified to Unverified Ratio data
    """
    def __init__(self, title): 
        self.title = title 
        self.editions = dict()

        """ 
        self.edition_to_verified_names = dict()
        self.edition_to_total_names = dict()
        self.edition_to_ratio = dict()
        """ 

    def add_edition(self, edition): 
        """ Adds a specific edition of this JournalCollection """ 
        self.editions[edition.id] = edition 

    def add_page(self, edition_id, page): 
        """ Adds a page to a Journal """ 
        journal = self.editions.get(edition_id, None)
        if journal == None: 
            raise ValueError("This edition of the Journal Collection does not exist")
        else: 
            journal.add_page(page)

    def convertToDict(self): 
        """ Converts the contents of a JournalCollection object to a dictionary in order to serialize to JSON """ 
        out = dict() 
        out["Title"] = self.title 
        editions = []
        for edition in self.editions.values(): 
            editions.append(edition.convertToDict(withTitle = False))
        out["Editions"] = editions
        return out 

def extract_journal(name): 
    """ Extracts the journal name and the edition from the raw journal id """
    match = re.search("\d+", name)
    if match != None: 
        return name[:match.start()], int(name[match.start(): match.end()])
    else: 
        return "", 0