## FAQ
This document contains:
1. Solutions to known errors/bugs

Q1: Run.sh throws an error during transformation, pretty quick after it starts:
`
ERROR 13188 --- [src/test/inbox/] o.a.c.p.e.DefaultErrorHandler            : Failed delivery for (MessageId: 00F569BB4D2AC6A-00000000000007D1 on ExchangeId: 00F569BB4D2AC6A-00000000000007D1). Exhausted after delivery attempt: 1 caught: java.lang.NullPointerException
`

A1: Solution:  
Decrease the number of COMPLETION_SIZE in [MySpringBootRouter.java](https://github.com/molgenis/data-transform-vkgl/blob/master/src/main/java/org/molgenis/core/MySpringBootRouter.java) 

Q2: Not all data from the last lab that gets transformed, is written to the output file
A2: Increase the sleep before `kill "${javaPid}"` in to run.sh

Q3: Running `liftover_vkgl_consensus.sh` results in the following error when using `tsv-vcf-converter.jar`version 1.0.0:
`
Exception in thread "main" java.lang.UnsupportedClassVersionError: org/molgenis/vip/converter/App has been compiled by a more recent version of the Java Runtime (class file version 55.0), this version of the Java Runtime only recognizes class file versions up to 52.0
`

A3: On Gearshift default Java version = Java/11.0.16 which supports class file version 55.0. 
    It appears however, that after loading picard, this is turned to Java/8-LT. 
    Solution: Add `ml Java` to `liftover_vkgl_consensus.sh` after `ml picard` and `ml BCFtools` 


