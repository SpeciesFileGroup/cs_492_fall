import re

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
		if numSeen == 0: # Literally no names in the journal. Weird edge case, and I'm not sure how this happens lol 
			return 0 
		return numVerified / numSeen

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
			f.write("Verified to Unverified Ratio: {}\n".format(str(self.get_verified_ratio())))

class JournalCollection(): 
    """ Conglomerates journals together so that we don't have a million data points 
    
    For example, americanjournalo02amer, americanjournalo03amer, americanjournalo05amer, and americanjournalo06amer are different versions 
    of the americanjournal. Instead of having one data point for each, we put all 4 together into the same collection. 
    
    For now, we are only combining the Verified to Unverified Ratio data
    """
    def __init__(self, title): 
        self.title = title 
        self.edition_to_ratio = dict()

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
    		f.write("Average Verified to Unverified Ratio: {}\n".format(str(self.get_average_ratio())))
    		print("Wrote {}".format(self.title))

def extract_journal(name): 
    """ Extracts the journal name and the edition from the raw journal id """
    match = re.search("\d+", name)
    if match != None: 
        return name[:match.start()], int(name[match.start(): match.end()])
    else: 
        return "", 0