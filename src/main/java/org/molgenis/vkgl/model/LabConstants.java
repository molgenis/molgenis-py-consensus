package org.molgenis.vkgl.model;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class LabConstants {
  public static final String LUMC = "LUMC";
  public static final String AMC = "AMC";
  public static final String NKI = "NKI";
  public static final String VU = "Genome Diagnostics Laboratory,VU University Medical Center Amsterdam";
  public static final String UMCG = "Diagnostic Laboratory, Department of Genetics,University Medical Center Groningen";
  public static final String UMCU = "Genome Diagnostics Laboratory,University Medical Center Utrecht";
  public static final String RADBOUD = "Radboud";
  public static final String ERASMUS = "DNA and Cytogenetics Diagnostics Unit,Erasmus Medical Center";

  private static final Map<String, String> reversedLookup = new HashMap<>(){{
    put(LUMC, "LUMC");
    put(AMC, "AMC");
    put(NKI, "NKI");
    put(VU, "VU");
    put(UMCG, "UMCG");
    put(UMCU, "UMCU");
    put(RADBOUD, "RADBOUD_MUMC");
    put(ERASMUS, "ERASMUS");
  }};

  public static List<String> getAllLabs(){
    return Arrays.asList(LUMC,AMC,NKI,VU,UMCG,UMCU,RADBOUD,ERASMUS);
  }

  public static String getShortName(String longName){
    return reversedLookup.get(longName);
  }
}
