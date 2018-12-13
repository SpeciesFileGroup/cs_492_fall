import re
import json

class Journal():
    """ A representation of a BHL Scientific Journal and Implements the Title data type defined in the protobuf. 
    Also contains miscellaneous summary statistics that may be useful. 

    Class Attributes: 
    id - the id of the journal in the database (i.e., index from 1). This is not the same as the volume number. 
    title - the title of the journal, corresponds to the archive_id attribute in the Protobuf
    path - the filepath of the journal 
    lang - the language it was written in 
    """ 
    def __init__(self, volume): 
        self.title = volume.archive_id
        self.id = volume.id
        self.path = volume.path
        self.lang = volume.lang

        match = re.search("\d+", self.title)
        if match == None: 
            self.volume_number = self.id 
        else: 
            self.volume_number = int(self.title[match.start() : match.end()])

        # Summary statistics 
        self.num_pages = 0 
        self.num_names = 0
        self.num_verified_names = 0 
        self.verification_ratio = 0 

        self.page_numbers = [] # Used to avoid duplicate pages 

    def __str__(self): 
        out = self.title
        out += "\nNumber of Pages: {}".format(len(self.num_pages))     
        return out

    def add_page(self, page): 
        """ Receives a page from an RPC stream and looks at its contents to update the summary statistics """
        page_num = page.id[page.id.rfind("_") + 1:]
        if page_num not in self.page_numbers: 
            self.num_pages += 1 
            self.num_names += len(page.names)
            verified = (1, 2, 4) # The int values corresponding to "EXACT", "CANONICAL_EXACT", and "PARTIAL_EXACT" in the MatchType enum 
            for name in page.names: 
                if name.match in verified: 
                    self.num_verified_names += 1 
            if self.num_names != 0: # Divide by 0 error
                self.verification_ratio = self.num_verified_names / self.num_names

    def get_summary_statistics(self): 
        """ Returns the number of pages, the number of names, the number of verified names, and the ratio of verified names in the Journal object """
        return self.num_pages, self.num_names, self.num_verified_names, self.verification_ratio

    def convert_to_dict(self): 
        """ Converts the contents of a Journal object into a dictionary format for the sake of serializing to JSON """
        out = dict()
        out["volumeTitle"] = self.title 
        out["volumeNumber"] = self.volume_number
        out["databaseID"] = self.id
        out["path"] = self.path 
        out["language"] = self.lang
        out["numPages"] = self.num_pages
        out["numNames"] = self.num_names
        out["numVerifiedNames"] = self.num_verified_names
        out["verificationRatio"] = self.verification_ratio
        return out

class JournalCollection(): 
    """ Conglomerates journals together so that we don't have a million data points 
    
    For example, americanjournalo02amer, americanjournalo03amer, americanjournalo05amer, and americanjournalo06amer are different versions 
    of the americanjournal. Instead of having one data point for each, we put all 4 together into the same collection. 
    
    For now, we are only combining the Verified to Unverified Ratio data
    """
    def __init__(self, title): 
        self.title = title 
        self.volumes = dict() # Maps from volume numbers to Journals 

        # Summary statistics 
        self.num_volumes = 0 
        self.num_pages = 0 
        self.num_names = 0 
        self.num_verified_names = 0
        self.average_num_pages = 0 
        self.average_num_names = 0 
        self.average_num_verified_names = 0 
        self.average_verification_ratio = 0

    def add_volume(self, volume): 
        """ Adds a Journal object """
        self.volumes[volume.volume_number] = volume

    def update_stats(self): 
        """ Updates the values of the summary statistics """ 
        self.num_volumes = len(self.volumes)
        for volume in self.volumes.values(): 
            self.num_pages += volume.num_pages
            self.num_names += volume.num_names 
            self.num_verified_names += volume.num_verified_names
        self.average_num_pages = self.num_pages / self.num_volumes 
        self.average_num_names = self.num_names / self.num_volumes 
        self.average_num_verified_names = self.num_verified_names / self.num_volumes 
        if self.num_names != 0: # Divide by zero error
            self.average_verification_ratio = self.num_verified_names / self.num_names

    def convert_to_dict(self): 
        """ Converts the contents of a Journal Collection object into a dictionary format for the sake of serializing to JSON """
        self.update_stats()
        out = dict() 
        out["title"] = self.title
        out["numVolumes"] = self.num_volumes
        out["numPages"] = self.num_pages
        out["numNames"] = self.num_names 
        out["numVerifiedNames"] = self.num_verified_names
        out["averageNumPagesPerVolume"] = self.average_num_pages 
        out["averageNumNamesPerVolume"] = self.average_num_names 
        out["averageNumVerifiedNamesPerVolume"] = self.average_num_verified_names
        out["averageVerificationRatio"] = self.average_verification_ratio

        volumes = [] 
        for volume in self.volumes.values(): 
            volumes.append(volume.convert_to_dict())
        out["volumes"] = volumes

        return out