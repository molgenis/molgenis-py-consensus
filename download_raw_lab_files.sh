# Script to download the Alissa data from Molgenis
# Raw data of lumc and radboudmumc is in Molgenis, but different headers
# use the files send by e-mail

# File extension options for the commander are .xlsx and .zip
# In the zip-file a .tsv is created => therefore download a zip-file,
# unzip it and rename the .tsv to a .txt

downloader=/Users/dieuwke.roelofs-prins/molgenis/tools/emx-downloader/downloader.jar
output_folder=export_jun-2020/raw_lab_files
labs="amc erasmus nki umcg umcu vumc"
url=https://molgenis122.gcc.rug.nl/
account=admin
if [ "$1" = "" ]; then
    echo "Start the script with the password for $url"
    exit
fi

pwd=$1

for lab in $labs;
 do
   output_file="$output_folder/vkgl_raw_$lab.zip"
   entity="vkgl_raw_$lab"
   java -jar $downloader -f $output_file -u $url -a $account -p $pwd -D -s 10000 $entity
   unzip -d $output_folder $output_file
   mv ${output_file/zip/tsv} ${output_file/zip/txt}
   rm $output_file
done
