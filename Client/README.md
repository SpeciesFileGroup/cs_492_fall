client.py connects to the server and implement the RPC methods defined in protob.proto 

utils.py defines useful Page/Journal/JournalCollection data structures used to organize the streamed data together 
  - Page isn't really implemented yet, get around to doing this later 
  - It would be more efficient/useful if these serialized to Json file formats instead of just writing to file line by line 

The data generated and used for visualization has been stored in journal_data.log, journal_data2.log, journal_collections_data.log, 
journal_collections_data2.log 

There are two jupyter notebooks that read the data files and convert them into interactive heatmaps. Generally refer to the second one.
The first one basically does the same thing, but less elegantly. 

The resulting heatmaps can be found in the two html files
