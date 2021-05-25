package org.molgenis.vkgl.model;

import java.util.Arrays;
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

  private LabConstants(){}

  private static final Map<String, String> reversedLookup = Map.of(
    LUMC, "LUMC",
    AMC, "AMC",
    NKI, "NKI",
    VU, "VU",
    UMCG, "UMCG",
    UMCU, "UMCU",
    RADBOUD, "RADBOUD_MUMC",
    ERASMUS, "ERASMUS"
  );

  public static List<String> getAllLabs(){
    return Arrays.asList(LUMC,AMC,NKI,VU,UMCG,UMCU,RADBOUD,ERASMUS);
  }

  public static String getShortName(String longName){
    return reversedLookup.get(longName);
  }
}
