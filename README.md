# molgenis-py-consensus
This pipeline generates the consensus table for the VKGL project, but can be used for every project
with the same data structure.

## Prerequisites for entire VKGL export
- Molgenis 7.0 or higher
- EMX file in `emx` directory is imported in molgenis
- Install MOLGENIS commander
- Add the output folder of this tool to the `mcmd` config to the dataset_folders
- Copy the `mcmd` scripts from the `mcmd_scripts` directory to the `.mcmd/scripts` folder on your machine
- Set `import_action` in `settings` section of `mcmd.yaml` to `add`
- Set config file (see below)

## Prerequisites for pipeline
- Lab tables are filled (for pre-processing raw data see next paragraph)
- Python 3.7.1 or higher
  Python libraries:
  - `termcolor (v1.1.0)`
  - `yaspin (v0.14.3)`
  - `progressbar2 (v3.39.3)`
  - `pandas (v1.2.3)`
  
## Config
In order to run the scripts, a config file should be added to the folder in which the pipeline is located. The 
configfile called `config.txt` should be placed in the `config` directory. Its content should like this:
```
labs=lab1,lab2,lab3
prefix=vkgl_
consensus=consensus
comments=consensus_comments
previous=1805,1810
history=consensus_history
output=/your/output/dir/
input=/your/input/dir/
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

### Previous
A list of numbers representing the previous exports in order to append the history. In this case
we had an export in May 2018 and October 2018, which resulted in `1805,1810`. 
 
## Summary
![](diagrams/VKGL_pipeline.svg)
  
## 1. Pre-processing raw data
Firstly the tables as delivered by the labs should be transformed into one uniform format. This can be achieved using 
the following pipeline:
[https://github.com/molgenis/data-transform-vkgl](https://github.com/molgenis/data-transform-vkgl).
This pipeline will transform several data formats to the generic VKGL data model. The data formats are described below.

### Alissa format
The header of the tab separated file contains the following values: `"timestamp", "id", "chromosome", "start", "stop", 
"ref", "alt", "gene", "transcript", "c_nomen", "p_nomen", "exon", "variant_type", "location", "effect", 
"classification", "last_updated_by", "last_updated_on"`. Except from `"timestamp"` and `"id"`, these are the columns as 
delivered from Alissa Interpret. They are first imported into MOLGENIS using the "Amazon bucket file ingest"
feature in the [MOLGENIS scheduled jobs plugin](https://molgenis.gitbooks.io/molgenis/content/guide-schedule.html).
From there the files are downloaded as csv and then converted into tab delimited (.txt) files and put into the inbox folder of the pipeline. With the script download_raw_lab_files.sh the Alissa data are automatically downloaded.
Before starting the file ingest make sure that the vkgl_raw_"labname" are empty.

### Radboud/MUMC format
The filename must contain the word "radboud". It is a tab separated file without a header, it should contain columns in
the following order: `"chromosome", "start", "stop", "ref", "alt", "gene", "transcript", "protein", empty column,
"exon", "empty column", "classification"`. 

### LUMC format
A tab separated file with the following columns: `"refseq_build", "chromosome", "gDNA_normalized", "variant_effect", 
"geneid", "cDNA", "Protein"`.

### Run the pipeline  
Remove the error files of the last export from the result folder. Download the most recent HGNC genes file, for more 
information checkout the readme in the `data-transform-vkgl` 
[repository](https://github.com/molgenis/data-transform-vkgl). If you don't have `IntelliJ` installed, run 
`mvn clean spring-boot:run -Dspring-boot.run.arguments=--hgnc.genes="location/of/your/hgnc/genes/file` (runs with 
Java 11) and place the lab files one by one in the inbox (data-transform-vkgl/src/test/inbox) (place the next if the 
previous one is reported to be done). 

If you have `IntelliJ`, run `src/main/java/org/molgenis/core/MySpringBootApplication.java`. Select 
`Edit Configurations`. Add `hgnc.genes=location/to/hgnc_genes.tsv` to `Environment variables`. If the `JRE` was not set
to Java 11 yet, please do this as well. You should now be able to run the pipeline without any problems.

After running the pipeline several files will be produced for each lab: 

| File                      | Description                                                                        |
|---------------------------|------------------------------------------------------------------------------------|
|`vkgl_*labname*.tsv`       | File with the data mapped to the generic VKGL data model (excl the errors)         |
|`*labname*.txt`            | File with the raw data plus the columns generated by the pipeline (excl the errors)|
|`vkgl_*labname*_error.txt` | File with the errors that were filtered out because they are invalid or duplicate  |

Now it's time to cleanup the tables with raw data in your MOLGENIS instance:
```
mcmd run vkgl_cleanup_labs_enriched_raw_data
```

The raw files should be renamed to: `vkgl_raw_*labname*_v2.tsv` and placed in the `output` folder of this tool 
(`molgenis-py-consensus`).
Upload them:
```
mcmd run vkgl_upload_labs_enriched_raw_data
```

The `vkgl_*labname*.tsv`
should be moved to the `input` folder of this tool (`molgenis-py-consensus`).
The error file can be send to the labs after the export is done.

By running the process_result_files.sh script, the renaming, moving to output and input folders as mentioned above is 
done automatically. This script also produces a file with counts per file.

Now go to the `preprocessing` folder of this tool and run `PreProcessor.py`. Make sure your config file is correctly 
set. This script creates the file `vkgl_comments.tsv` in the output folder of the pipeline. 

## 2. Get a test server
For the next couple of steps you want to make sure you don't mess up the production server. That's why it's best to get
a copy from the production server to make sure everything works perfectly fine before you wipe production data. Set this
server as host in using the `mcmd config` command.

## 3. Add last export to history table
At this point, please make sure you transported the lines of the previous consensus table to the
history table. To do so, do the following.

1. Download the data of your current consensus table and consensus comments table using either the 
[EMX downloader](https://github.com/molgenis/molgenis-tools-emx-downloader) or the download feature in the navigator.
2. Save the consensus table as tab separated file named `vkgl_consensus20*yymm of previous export*.tsv`.
3. Save the consensus comments table as separated file named `vkgl_consensus_comments20*yymm of previous export*.tsv`.
4. Run the `HistoryWriter.py` in the `preprocessing` directory.
5. Import the history:
```
mcmd import vkgl_consensus_history.tsv
```
Make sure it's uploaded by checking in your MOLGENIS. Use the 
[EMX downloader](https://github.com/molgenis/molgenis-tools-emx-downloader) to download the updated history table and
put it in the input folder you specified in the config. 

If this looks fine, you can also update the history file on your production server. If you switched hosts in your mcmd
config, make sure you switch back to the test server after this step.

Now use the [EMX downloader](https://github.com/molgenis/molgenis-tools-emx-downloader) to download the updated history
table and put it in the input folder you specified in the config. 
```
java -jar downloader.jar -f consensus_history.zip -u https://yourserver/ -a admin -p password vkgl_consensus_history
```

## 4. Double check
Open the `vkgl_comments.csv` file and check if there are any duplicate lines. If there are any, you possibly have 
encountered a hash collision issue. 
To fix this, go to the `PreProcessor.py` and increase the number of characters to be returned from the hashed id, keep
it as short as possible to keep the performance in MOLGENIS as good as possible.
```python
def _get_id(variant_id, lab):
    prefix = lab.upper().replace('_', '') + '_'
    # Get first 10 of hash
    return prefix + variant_id[0:10]
``` 
If this is the case, you need to rerun the preprocessor. If you had to make this change, make sure that for the next 
export you alter the history writer to work for the 'new ids'.

## 5. Running the script
Once the config file is specified, make sure you have initialized a virtual environment:
```
python3 -m venv env
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
3. Writing the consensus table to file (this takes a long time)
4. Generating reports:
    - Counts of the classifications in counts.html (to be placed on a Molgenis static content page)
    - Public consensus (will automatically upload)
    - A text file with opposites (opposites_report_yymm.txt)
    - A text file with counts per variant type (in types.txt)
  
## 6. Test the output
Make sure your host is set to the testserver.
```
mcmd run vkgl_cleanup_consensus
mcmd run vkgl_cleanup_labs
mcmd delete --data vkgl_comments -f
mcmd import vkgl_comments.csv
mcmd run vkgl_import_labs
mcmd import vkgl_consensus_comments.csv
mcmd import vkgl_consensus.csv
mcmd delete --data vkgl_public_consensus -f
mcmd import vkgl_public_consensus.csv
``` 
If you get a `504` error throughout this process. You can start a `mcmd` script from a certain line using the 
`--from-line` command. Keep retrying until you don't get the `504` anymore. Trust me, it will work.

If it all looks fine, proceed to the next step.

## 7. Time to upload to production
Change the host to the production server in the `mcmd` config. Then put a message on the homepage (edit `home` row in 
`sys_StaticContent` table):
```html
<div class="alert alert-warning" role="alert">
  We are currently working on the new VKGL data release, this means some data might be missing or incorrect. As soon as
  this message is no longer on our homepage, the release is updated and save to use. We thank you for your understanding
  and patience.
</div>
```
Now run the same commands on the production server:
```
mcmd run vkgl_cleanup_consensus
mcmd run vkgl_cleanup_labs
mcmd delete --data vkgl_comments -f
mcmd import vkgl_comments.csv
mcmd run vkgl_import_labs
mcmd import vkgl_consensus_comments.csv
mcmd import vkgl_consensus.csv
mcmd delete --data vkgl_public_consensus -f
mcmd import vkgl_public_consensus.csv
``` 
Copy the content of `counts.html` to the counts page (`news` row of `sys_StaticContent`).

Upload the public consensus to the downloadserver and update the downloads page in the static content table.

Update the name of the export in the menu.

Remove message from homepage.

Send the export to contact persons for acceptance.

Once accepted, report to the labs that the export is finished, let them know which errors were found for their lab and 
which conflicts (`vkgl_opposites_report_*yymm of export*.txt`) were found in the consensus table.

Send the raw Radboud/MUMC file and the raw files from the `Alissa` labs to LUMC to update LOVD and LOVD+.

## 8. Producing an artefacts file
For some labs we might get the artefacts data. To get an artefacts file we can use, follow these steps:
1. Download the artefacts file using the bucket ingest of molgenis
2. Download the table as tsv from molgenis
3. Place it in the inbox folder of `data-transform-vkgl`
4. Run `data-transform-vkgl` using the same genes file as the data release

## 9. Persist source data
Create a directory on the `gearshift cluster`, following this convention: `/groups/umcg-gcc/tmp01/projects/VKGL/yyyymm`

Place the following data in this folder:
- The raw lab files used in data-transform-vkgl
- The `hgnc_genes.tsv` that was used in `data-transform-vkgl`
- The `vkgl_consensus_history.tsv` generated by the HistoryGenerator (in output folder) and rename it to 
  `vkgl_consensus_history_old.tsv`
- The complete `vkgl_consensus_history.tsv` (in input folder) used in `molgenis-py-consensus`
- The `vkgl_consensus.csv` that was generated using `molgenis-py-consensus`
- A readme using the following template: [README template](/templates/cluster_readme_template.txt)
- A directory called: `umcg_artefacts`

Place in the `artefacts` directory:
- The artefacts source file as used in `data-transform-vkgl`
- A readme according to the following template: [README template](/templates/cluster_readme_artefacts_template.txt)

## Step-to-step summary
If you know how to do the export and don't need excessive explanation. Use this summary when doing the data release to 
make sure everything is done correctly.
1. Delete data from vkgl_raw lab tables (`mcmd`) 
2. Download Alissa files into molgenis
3. Upload Radboud/MUMC and LUMC data into raw tables in MOLGENIS
4. Download raw tables from Molgenis (files should be tab-separated)  
5. VUMC data is separated into two tables, merge the files
6. Run `data-transform-vkgl` for all labs (wait for a lab to finish before you place the next):
    - AMC
    - Erasmus
    - LUMC
    - NKI
    - Radboud/MUMC
    - UMCG
    - UMCU
    - VUMC
7. Cleanup raw v2 tables (`mcmd`) 
8. Upload enriched raw tables (`mcmd`) 
9. Download current consensus and consensus comments
10. Place lab files of `data-transform-vkgl` in input folder `molgenis-py-consensus`
11. Run the HistoryWriter and Preprocessor
12. Upload new history on testserver
13. Upload new history on production server
14. Upload raw_v2 data onto testserver and if it looks fine, also on production
15. Download complete history using EMX downloader into input folder `molgenis-py-consensus`
16.Run the consensus script 
17. Check if the data looks alright  
Try to upload files on testserver:
18. `mcmd run vkgl_cleanup_consensus`
19. `mcmd run vkgl_cleanup_labs`
20. `mcmd delete --data vkgl_comments -f`
21. `mcmd import vkgl_comments.csv`
22. `mcmd run vkgl_import_labs`
23. `mcmd import vkgl_consensus_comments.csv`
24. `mcmd import vkgl_consensus.csv`
25. `mcmd delete --data vkgl_public_consensus -f`
26. `mcmd import vkgl_public_consensus.csv`  
If the data looks alright on your testserver, switch your `mcmd` config to the production server and run the same lines 
there.
27. Put a message on the homepage
28. `mcmd run vkgl_cleanup_consensus`
29. `mcmd run vkgl_cleanup_labs`
30. `mcmd delete --data vkgl_comments -f`
31. `mcmd import vkgl_comments.csv`
32. `mcmd run vkgl_import_labs`
33. `mcmd import vkgl_consensus_comments.csv`
34. `mcmd import vkgl_consensus.csv`
35. `mcmd delete --data vkgl_public_consensus -f`
36. `mcmd import vkgl_public_consensus.csv`  
37. Put the public consensus csv on the download server
38. Update the downloads page
39. Update the counts page
40. Remove message from homepage
41. Send email for acceptance
42. Once accepted, report errorfiles back to labs
43. Produce the artefacts file(s) (see step 8 above)
44. Place the source files on the cluster (see step 9 above)

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
