+========================================================================================+
|+++++++++++++++++++++++++++++++++++ VKGL Data release ++++++++++++++++++++++++++++++++++|
+========================================================================================+
| Release date: {{release date}}			  				   		    				 |
+----------------------------------------------------------------------------------------+
| INPUT DATA							  						  						 |
+----------------------------------------------------------------------------------------+
| LUMC: {{lumc export date}}										  				     |
| Radboud/MUMC: {{radboud/mumc export date}}		  			    					 |
| Alissa: {{alissa export date}}				        		  						 |
+----------------------------------------------------------------------------------------+
| VERSIONS							  			    			  						 |
+----------------------------------------------------------------------------------------+
| data-transform-vkgl: v{{version}}					       		  						 |
| molgenis-py-consensus: v{{version}}				       		  						 |
+----------------------------------------------------------------------------------------+
| SETTINGS  						  			    			  						 |
+----------------------------------------------------------------------------------------+

labs={{labs}}
prefix={{prefix}}
consensus={{consensus}}
comments={{consensus_comments}}
previous={{dates}}
history={{consensus_history}}
input=input/
output=output/

+----------------------------------------------------------------------------------------+
| STEPS FOR REPRODUCTION				   		  			    			  			 |
+----------------------------------------------------------------------------------------+
1. Download the lab files and vkgl_consensus_history.tsv onto your device
2. Configure hgnc_genes.tsv as genes input file for data-transform-vkgl
3. Run data-transform-vkgl for all labs (wait for a lab to finish before you place the
next in the inbox folder):
    {{ '- '+lab for lab in labs}}
4. If there is no input or output folder in the molgenis-py-consensus directory, create
them.
5. Take the labfiles (the ones like vkgl_UMCG.tsv) and put them in the input folder of
molgenis-py-consensus
6. Put vkgl_consensus_history.tsv in the input folder of molgenis-py-consensus
7. Place the configuration file in the config directory of molgenis-py-consensus
8. Run the PreProcessor and History writer in the preprocessing directory of
molgenis-py-consensus
9. Run the consensus script:
python3 -m venv env
source env/bin/activate
pip install -e .
python3 consensus
