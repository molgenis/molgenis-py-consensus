# molgenis-py-consensus
This pipeline generates the consensus table for the VKGL project, but can be used for every project
with the same data structure.
  
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

## Running the script
Once the config file is specified, make sure you have initialized a virtual environment:
```
python3 -m venv env
```
When the correct data is provided and preprocessed. Run easily using the following command:
```
source env/bin/activate
pip install -e .
python3 consensus
```

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

# VKGL Data release

This guide will explain every step in the VKGL Data release process. Please follow it step by step to guarantee
consistent output for every export.

## Prerequisites

- Install [Molgenis Commander](https://github.com/molgenis/molgenis-tools-commander)
- Paste [these files](https://github.com/molgenis/molgenis-py-consensus/tree/master/mcmd_scripts) in `.mcmd/scripts`
- Add test server as host to commander (`mcmd config add host`)
- Add prod server as host to commander
- Set `import_action` in the `settings` section of `mcmd.yaml` to `add`
- Add the `output` folder of `molgenis-py-consensus` to `dataset_folders` in  `mcmd.yaml`

## Step-by-step guide

1. Request a test server. It should be a copy of the current VKGL molgenis server.
2. Get the Alissa files and store them in some folder.
3. Get the LUMC and Radboud/MUMC files and store them in a separate folder.
4. Get the latest tag of [`data-transform-vkgl`](https://github.com/molgenis/data-transform-vkgl/tags)
   (every release, we create a new tag that uses the newest release in the helper scripts):

```commandline
wget https://github.com/molgenis/data-transform-vkgl/archive/refs/tags/data-release-v*insert versionnumber*.zip
unzip data-release-v*insert versionnumber*.zip
```

5. Go to the `data-release-pipeline` folder of the folder you just unzipped.
6. Run `run.sh` like this:

```
./run.sh -l /path/to/lumc.tsv -r /path/to/radboud_mumc.tsv --aws_credentials /path/to/aws/credentials --aws_config  /path/to/aws/config -s /path/to/folder/with/allissa/data
```

7. Create a screen (VERY important to do that now!). Then validate the output it generated by running the validation
   script:

```commandline
screen
ml PythonPlus
python validator/main.py /folder/created/by/run.sh/
```

8. If all checks are successful, continue, else rerun `run.sh` or pinpoint the issue.
9. Change directory back to Download the most recent version of the
   molgenis [EMX downloader](https://github.com/molgenis/molgenis-tools-emx-downloader):

```commandline
wget https://registry.molgenis.org/repository/maven-releases/org/molgenis/downloader/*insert version here*/downloader-*insert version here*.jar
unzip downloader-*insert newest version here*.zip
```

10. Download the current consensus and consensus comments:

```commandline
java -jar downloader-*insert version here*.jar -f consensus.zip -u https://yourserver/ -a admin vkgl_consensus
```

11. Unzip the downloaded zip

```commandline
unzip consensus.zip
```

12. Now you can either run [this script](https://github.com/molgenis/data-transform-vkgl/pull/50) the following way (
    assuming it's reviewed and merged):
    IMPORTANT: if you're reproducing, make sure you also specify `-m` with the version of `molgenis-py-consensus` that
    was used the last time.

```commandline
python -m venv env
python source env/bin/activate
pip install -e .
python main.py -v /folder/created/by/run.sh/ -l umcg,umcu,nki,amc,vumc,radboud_mumc,lumc,erasmus -i /place/to/store/input/for/molgenis-py-consensus -o /place/to/store/output/for/molgenis-py-consensus -p *comma separated list of yymm dates of all releases* -c unzipped/consensus/folder/vkgl_consensus.tsv -cc unzipped/consensus/folder/vkgl_consensus_comments.tsv
```

Or, do the steps manually:

- Download the latest version (or the one you need) of molgenis-py-consensus
- Create an input and output folder for this tool
- Create a `config.txt` in the `molgenis-py-consensus/config` directory. Example:

```text
labs=umcg,umcu,nki,amc,vumc,radboud_mumc,lumc,erasmus
prefix=vkgl_
consensus=consensus
comments=comments
previous=1805,1810,1906,1912,2003,2006,2009,2101,2104
history=consensus_history
input=place/to/store/input/for/molgenis-py-consensus/
output=place/to/store/output/for/molgenis-py-consensus/
```

Make sure to update the `previous`, `input` and `output`. The other values will (almost) always stay the same.

- Copy the `vkgl_vkgl`-lab files and the `vkgl_` files of radboud and LUMC to the input dir you specified in the config.
- Grant permissions to run the consensus scripts:

```commandline
chmod g+x -R /path/to/molgenis-py-consensus
```

- Change dir to molgenis-py-consensus
- Setup and install molgenis-py-consensus

```commandline
python -m venv env
python source env/bin/activate
pip install -e .
```

- Run the preprocessor:

```commandline
python preprocessor/PreProcessor.py
```

- Run the history writer:

```commandline
python preprocessor/HistoryWriter.py
```

13. Configure molgenis commander host to test server.

``` commandline
mcmd config set host
```

14. Import the consensus history on your testserver

```commandline
mcmd import vkgl_consensus_history.tsv
```

15. Check your molgenis server to make sure the history is uploaded. There should be variants from the previous export
    available in the table. If it looks okay, change the mcmd host to production and run the same command.
16. Go to the folder you want to store the history zip. Download the complete consensus history using the EMX
    downloader:

```commandline
java -jar downloader.jar -f consensus_history.zip -u https://yourserver/ -a admin vkgl_consensus_history
unzip consensus_history.zip
```

17. Place the vkgl_consensus_history.tsv from the zip in your `molgenis-py-consensus` input directory.
18. Run the consensus script:

```commandline
python consensus
```

19. The script takes about 18 hours to run, so detach your screen to make sure your internet connection won't mess up
    the script run, by pressing `ctrl+a d`.

20. Now you have plenty of time to create the ClinVar files. To do this, get the most recent version (or another
    version, if you wish) of [vkgl-clinvar](https://github.com/molgenis/vkgl-clinvar).

21. Go to clinvar, select `Submit` in the dropdown and click `Submission portal` (this way you will be redirected to the
    correct overview). Download `SUB*submission id*_(100)_submitter_report_B.txt` of the previous ClinVar submits for
    all labs.

22. Create an output folder for your clinvar submit files.
23. Run the script:

``` commandline
java -jar vkgl-clinvar-writer.jar -i /output/of/runs.sh/consensus/consensus.tsv -m /path/to/files/from/previous/clinvar/submit/*export name*_DUPLICATED_identifiers.tsv,/path/to/files/from/previous/clinvar/submit/*export name*_REMOVED_identifiers.tsv,/path/to/files/from/previous/clinvar/submit/*export name*_UNCHANGED_identifiers.tsv,/path/to/files/from/previous/clinvar/submit/*export name*_UPDATED_identifiers.tsv -c amc=/path/to/SUB*submission id*_(100)_submitter_report_B.txt,lumc=/path/to/SUB*submission id*_(100)_submitter_report_B.txt,nki=/path/to/SUB*submission id*_(100)_submitter_report_B.txt,umcg=/path/to/SUB*submission id*_(100)_submitter_report_B.txt,radboud_mumc=/path/to/SUB*submission id*_(100)_submitter_report_B.txt,umcu=/path/to/SUB*submission id*_(100)_submitter_report_B.txt,vumc=/path/to/SUB*submission id*_(100)_submitter_report_B.txt,erasmus=/path/to/SUB*submission id*_(100)_submitter_report_B.txt -o /output/folder/for/clinvar/data -r mon_yyyy -f
```

24. Check if your consensus script is still running:

```commandline
screen -r
```

If everything is okay, press `ctrl+a d` again. Now all we need to do is wait until the script is done. After its done,
type `deactivate` to deactivate the virtual environment.

25. Change the mcmd host to the test server again. Test if the output works by uploading it to the test server:

```commandline
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

If you get a `504` error throughout this process. You can start a mcmd script from a certain line using
the `--from-line` command. Keep retrying until you don't get the `504` anymore. Trust me, it will work.

26. Time to upload production. Set a message on the homepage by editing the `home` row in `sys_StaticContent` (don't do
    it via the home page, it will mess up everything!):

```html

<div class="alert alert-warning" role="alert">
    We are currently working on the new VKGL data release, this means some data might be missing or incorrect. As soon
    as
    this message is no longer on our homepage, the release is updated and save to use. We thank you for your
    understanding
    and patience.
</div>
```

27. Set the mcmd host to production and run the following commands on production:

```commandline
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

28. Update the counts page by editing the `news` row in the `sys_StaticContent` table and paste the `counts.html` that
    was produced by `molgenis-py-consensus`.

29. Upload the public consensus to the downloadserver and update the downloads page in the static content table.
30. Update the name of the export in the menu.
31. Update the name of the export on the homepage and remove the message.
32. Send an email to the contact persons for acceptance testing.
33. Once accepted, report to all labs that it's finished and send an email to each lab separately with their errorfiles
    and the ClinVar file, asking for approval to submit it.
34. Send the files from the preprocessed folder of `run.sh` and the raw `Radboud_MUMC` file to the LUMC
35. Do the ClinVar submission for all labs. [Need help?](https://github.com/molgenis/vkgl-clinvar)
36. Persist data on the`gearshift` cluster. Create a new folder with a name like `yyyymm` in
    the `/groups/umcg-gcc/prm03/projects/VKGL/` folder.
37. Create a folder called `raw` with a folder called `alissa` in it and place the raw allisa files (including the
    artefacts file) in there. Add the raw radboud and lumc data to the `raw` folder.
38. Copy the genes file from the downloads folder of `run.sh` to the `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm`
    folder.
39. Copy the molgenis-py-consensus output directory to `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm` (it took 18 hours
    to make it, you want to keep and cherish it).
40. For reproduction purposes, copy the `config/config.txt` and the `vkgl_history.csv` from the `molgenis-py-consensus`
    input folder to `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm`.
41. Copy the `consensus.tsv` from the `consensus` output folder of `run.sh`
    to `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm`
42. Copy the clinvar folder with the files generated by the `vkgl-clinvar-writer`
    to `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm`
43. Make a directory called `artefacts` and place the lonely `vkgl_vkgl_` artefacts file from the `run.sh` `transformed`
    output folder in `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm/artefacts`
44. Create a directory called `errors` in `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm/molgenis` and place
    all `_error.txt` files from the `run.sh` `transformed` folder in this folder.
45. Create a `versions.txt` in `/groups/umcg-gcc/prm03/projects/VKGL/yyyymm/` with the following content:
```text
DATA:
Alissa yyyymmdd
Radboud/MUMC yyyy-mm-dd
LUMC yyyy-mm-dd

Scripts:
data-transform-vkgl and run.sh: data-release-vx.y.z
vkgl-clinvar: vx.y.z
molgenis-py-consensus: x.y.z
```