# SOP:

## 1) Parse the ClinVar XML
run ```ClinVarXmlParser```  from intellij with the params:

```
-i "path/to/ClinVarFullRelease_2021-05.xml" 
-o "path/to/clinvar_IDs.txt"
```

## 2) Map the identifiers and create the ClinVar sheets
run ```VkglToClinVarMapper``` from intellij with the params:

```
-i "path/to/vkgl_consensus_apr2021.tsv" 
-c "path/to/clinvar_IDs.txt" 
-d "path/to/preprocessed" --> preprocessed file from the VKGL data release (vkgl_[LAB])
-f "No consensus,Classified by one lab,Opposite classifications" 
-r "APR2021" 
-o "path/to/VKGL/"
```

## 3) Run mutalizer name validation in batch validation mode
- https://mutalyzer.nl/batch-jobs?job_type=name-checker
 with the results files that are postfixed with "_cDNA" from step 2

- Rename the results to [LAB IDENTIFIER]_validated.tsv
- make sure the ClinVar submission files and the create validated files are in the same directory

## 4) Filter the clinVar sheets
run ```FilterCorrectCDna``` from intellij with the params:
```
-i C:/Users/bartc/Documents/VKGL/ 
-r APR2021
```
