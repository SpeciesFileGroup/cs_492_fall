import re
import json

class Page():
    """ A representation of a page in a BHL Scientific Journal. 
    
    Corresponds to the Page data type defined in the Protocol Buffer. However, some values in the Protocol Buffer are not used: 
        - title_id is the name of the journal. Since Pages will be collected into Journal objects that already store this value, this is ignored 
        - title_path is the filepath of the journal. This is ignored for the same reason as title_id

    Additionally, while the offset variable is stored, it's not used for anything at the moment
    """ 

    def __init__(self, page_num, offset, text, names):
        self.page_num = page_num
        self.offset = offset 
        self.text = text # Assume this has already been converted from bytes to string 
        self.names = [] 
        for name in names: 
            self.names.append(name)

class Journal():
    """ A representation of a BHL Scientific Journal. Contains a collection of Page objects.

    MODIFY THIS TO MATCH THE NEW PAGE OBJECTS 

    Class Attributes: 
    id - the id of the journal in the database
    title - the title of the journal, corresponds to the archive_id attribute in the Protobuf
    path - the filepath of the journal 
    lang - the language it was written in 

    pages_to_names - a dictionary that maps from the page in the journal to a list of NameString present on that page 
    pages_to_text - a dictionary that maps from the page in the journal to the text present on that page
                    For now, the text is not processed at all before stored in the dictionary (i.e., still has whitespace characters)

    The length of these two dictionaries should always be the same and is equal to the number of pages in the dictionary
    """ 
    def __init__(self, title, id = 0, path = "" , lang = ""): 
        self.title = title
        self.id = id 
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

        NOTE: modified to also return the numVerified and numSeen values

        A NameString is "verified" if the value of its MatchType field is equal to "EXACT", "CANONICAL_EXACT", or "PARTIAL_EXACT". If this field is empty or if it 
        is equal to "NONE", "CANONICAL_FUZZY", or "PARTIAL_FUZZY", it is considered "unverified"
        """
        if len(self.pages_to_names) == 0: # There are no pages in this journal 
            return 0, 0, 0 
        verified = (1, 2, 4) # The int values corresponding to "EXACT", "CANONICAL_EXACT", and "PARTIAL_EXACT" in the MatchType enum
        numVerified = 0
        numSeen = 0 
        for names in self.pages_to_names.values(): # Lists of NameString Objects
            numSeen += len(names)
            for name in names: 
                if name.match in verified: 
                    numVerified += 1
        if numSeen == 0: # Literally no names in the journal. Weird edge case, and I'm not sure how this happens lol 
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

class JournalCollection(): 
    """ Conglomerates journals together so that we don't have a million data points 
    
    For example, americanjournalo02amer, americanjournalo03amer, americanjournalo05amer, and americanjournalo06amer are different versions 
    of the americanjournal. Instead of having one data point for each, we put all 4 together into the same collection. 
    
    For now, we are only combining the Verified to Unverified Ratio data
    """
    def __init__(self, title): 
        self.title = title 
        self.edition_to_verified_names = dict()
        self.edition_to_total_names = dict()
        self.edition_to_ratio = dict()

    def get_average_num_verified(self):
        if len(self.edition_to_verified_names) == 0: 
            return 0
        return sum(self.edition_to_verified_names.values()) / len(self.edition_to_verified_names)

    def get_average_num_names(self):
        if len(self.edition_to_total_names) == 0: 
            return 0
        return sum(self.edition_to_total_names.values()) / len(self.edition_to_total_names)

    def get_average_ratio(self): 
        """ Returns the arithmetic mean of the Verified to Unverified Ratio data """
        if len(self.edition_to_ratio) == 0: 
            return 0 
        return sum(self.edition_to_ratio.values()) / len(self.edition_to_ratio)

    def write_to_file(self, filepath, mode = "a"): 
        """ Writes the contents of this Journal Collection to the specified filepath using the specified mode 

        Currently writes the Journal Collection's title and the average Verified to Unverified Ratio

        Inputs: 
            filepath: string, a (valid) filepath 
            mode: the access mode that we want to open the file with. This is set to append by default. 
        """ 
        if "r" in mode: 
            print("Only accepts write and append modes")
            return 
        with open(filepath, mode) as f:
            f.write("{}\n".format(self.title))
            f.write("Verified: {}\n".format(str(self.get_average_num_verified())))
            f.write("Names: {}\n".format(str(self.get_average_num_names())))
            f.write("Ratio: {}\n".format(str(self.get_average_ratio())))
            print("Wrote {}".format(self.title))

def extract_journal(name): 
    """ Extracts the journal name and the edition from the raw journal id """
    match = re.search("\d+", name)
    if match != None: 
        return name[:match.start()], int(name[match.start(): match.end()])
    else: 
        return "", 0