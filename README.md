

## Folder structure
The repo has been organized into code, data and Protobuf folders. 

- The code contains the python notebooks used to generate the visuazliations as well the client and utils files to connect to the gRPC server and implement the RPC Methods defined in the proto file within the Protobuf folder.
- The data folder contains geo_entity_data which has been processed into data for countries and cities separately, which are used for the geo-entity visualziations. It also contains journal and journal collection data used for generating the verification ratio heatmaps and langauge data for the language heatmap.
- The protobuf folder contains a single .proto file on which our case is based.

## Setting up environment
There is a requirements.txt file, doing a direct ```pip -r install requirements.txt``` should be sufficient. 

## Running the code
Run jupyter notebook in a terminal, and you should be able to execute all 3 iPython notebooks (they all pull data from files in the data folder)


