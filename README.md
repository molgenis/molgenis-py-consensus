# molgenis-py-consensus
This pipeline generates the consensus table for the VKGL project, but can be used for every project
with the same data structure.

## Prerequisites for pipeline
- Molgenis 7.0 or higher
- EMX file in emx directory is imported in molgenis
- Lab tables are filled (for pre-processing raw data see next paragraph)
- Python 3 (tested on 3.7)  
  Python libraries: 
  - `molgenis-py-client (v2.1.0 or higher)`
  - `termcolor (v1.1.0)`
  - `yaspin (v0.14.3)`
  - `progressbar2 (v3.39.3)`

## Pre-processing raw data
To transform raw tables into lab tables, first the mappings need to be uploaded. Then the raw
lab tables should be filled. This can be either via the importer or via the amazon bucket ingest.
Raw data tables that do not have the required columns yet (HGVS notation is used rather than VCF),
can be enriched using the following tool:  
[https://github.com/fdlk/vkgl](https://github.com/fdlk/vkgl).  

After uploading the raw data, the data can be mapped. First map the comments table. After that the
lab tables can be mapped in random order.

## Add last export to history table
At this point, please make sure you transported the lines of the previous consensus table to the
history table. There is a mapping for this, but possibly it's too big to run. Reformatting the 
current consensus table into the format of the history table can be easily achieved by downloading
the current export in the Molgenis Navigator plugin, and using Excel functions to transform the data
into the model of the history table. The transformations that should be done are: 
- The date (`yymm`) should be prepended to the id column (id format is `yymm_chr_start_ref_alt_gene`)
- The lab link columns should be removed
- The comments from the consensus comments table should be moved to the comments column (most of the time there are 
none)  

After these transformations, remove the metadata files and upload the data via the advanced importer 
with the "add data" option. 

## Config
In order to run the script a config file should be added to the folder in which the pipeline is
located. The configfile called `config.txt` should be placed in the `config` directory. Its content should like this:
```
username=yourusername
password=yourpassword
labs=lab1,lab2,lab3
prefix=vkgl_
consensus=consensus
server=http://yourserver/api/
comments=consensus_comments
previous=1805,1810
history=consensus_history
```

### Prefix
The prefix is the characters that are always prepended to a table name in order to get the fully
qualified name (usually this is the package name).

### Labs
Labs is a comma separated list of the labs that should be processed into the consensus table. 
Naturally these names should be the same as the name of the table that contains the data, for 
instance: when specifying `umcg` the data is stored in the `vkgl_umcg` table. 

### Consensus, Comments, and History
The name of the consensus, comments and history table, without the prefix.

### Server
The URL of the API of your server. Don't forget to add the `/api/` behind your URL.

### Previous
A list of numbers representing the previous exports in order to append the history. In this case
we had an export in May 2018 and October 2018, which resulted in `1805,1810`. 

## Running the script
Once the config file is specified and the lab tables are populated, make sure you have initialized 
a virtual environment:
```
python3 -m virtualenv env
```

Now the script should be able to run easily using the following command:
```
source env/bin/activate
pip install -e .
python3 consensus
```
The script will keep you posted on its progress. The main steps of the process are:
1. Retrieving data (of the labs and the history table)
2. Processing variants
3. Deleting the old consensus table (might take a while)
4. Deleting the old comments table (might take a while)
5. Uploading the new comments 
6. Writing the consensus table to file (the more history the longer this takes, with 2 rounds of history +/- 45 minutes)
7. Uploading the consensus table
8. Generating reports:
    - Counts of the classifications in counts.html (to be placed on a Molgenis static content page)
    - Public consensus (will automatically upload)
    - A text file with opposites (opposites_report_yymm.txt)
    - A text file with counts per variant type (in types.txt)
9. Deleting current public consensus export
10. Uploading new public consensus data

Typically the script runs for approximately an hour until it finishes (for two batches of history).

## Running tests
For the complex code functionality tests have been added. To run the tests run the following command
in your virtual environment:
```
python3 setup.py test
```

## Testing integration of pipeline
To test this pipeline:
1. Upload the `test_data/test_emx.xlsx` in Molgenis via the advanced importer.
2. Place the content of the `config.txt` in the config directory by the content of `test_data/test_config.txt`.
3. Run the script (after initializing virtual environment, see "Running the script"):
```
source env/bin/activate
pip install -e .
python3 consensus
```

## Pipeline flow diagram
![alt text](diagrams/flow.svg "Flow diagram")


## Pipeline code diagram
![alt text](diagrams/code.svg "Code diagram")