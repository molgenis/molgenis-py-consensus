package org.molgenis.vkgl.clinvar;

import static org.molgenis.vkgl.model.LabConstants.getShortName;

import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map.Entry;
import org.molgenis.vkgl.model.ClinVarData;
import org.molgenis.vkgl.clinvar.model.DeletesLine;
import org.molgenis.vkgl.clinvar.model.VariantLine;

public class ClinVarWriter {

  public static final String VARIANT_FORMAT = "%s\t%s\t%s\t%s\t%s\t%s\t%s\n";
  public static final String DELETES_FORMAT = "%s\n";

  public static final String HGVS_NAME = "HGVS name";
  public static final String PREFERRED_CONDITION_NAME = "Preferred condition name";
  public static final String CLINICAL_SIGNIFICANCE = "Clinical significance";
  public static final String DATE_LAST_EVALUATED = "Date last evaluated";
  public static final String GENE_SYMBOL = "Gene symbol";
  public static final String CLIN_VAR_ACCESSION = "ClinVarAccession";
  public static final String AFFECTED_STATUS = "Affected status";
  public static final String NOT_PROVIDED = "not provided";
  public static final String COLLECTION_METHOD_VALUE = "clinical testing";
  public static final String ALLELE_ORIGIN_VALUE = "germline";
  public static final String DATE_VALUE = "";
  public static final String NOT_SPECIFIED = "not specified";
  public static final String BENIGN = "Benign";
  public static final String VARIANT_SHEET = "_Variant.tsv";
  public static final String EVIDENCE_SHEET = "_ExpEvidence.tsv";
  public static final String DELETES_SHEET = "_Deletes.tsv";
  public static final String C_DNA_TSV = "_cDNA.tsv";
  private static final String REFERENCE_SEQUENCE ="Reference sequence";
  private static final String CDNA = "HGVS";

  private ClinVarWriter() {}

  public static void write(ClinVarData clinVarData, String outputDir, String releaseName,
      boolean isUpdateOnly) {

    for (Entry<String, List<VariantLine>> entry : clinVarData.getVariants().entrySet()) {
      writeVariants(releaseName, entry, outputDir, isUpdateOnly);
    }

    for (Entry<String, List<DeletesLine>> entry : clinVarData.getDeletes().entrySet()) {
      writeDeletes(releaseName, entry, outputDir);
    }
  }

  private static void writeDeletes(
      String releaseName, Entry<String, List<DeletesLine>> entry, String outputDir) {
    String lab = entry.getKey();
    try (FileOutputStream outputStream =
        new FileOutputStream(
            Path.of(outputDir, getShortName(lab) + "_" + releaseName + DELETES_SHEET).toFile())) {
      outputStream.write(String.format(DELETES_FORMAT, CLIN_VAR_ACCESSION).getBytes());
      for (DeletesLine deletesLine : entry.getValue()) {
        outputStream.write(String.format(DELETES_FORMAT, deletesLine.getSvc()).getBytes());
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  private static void writeVariants(
      String releaseName, Entry<String, List<VariantLine>> entry, String outputDir, boolean isUpdateOnly) {
    String lab = entry.getKey();
    try (FileOutputStream outputStream =
            new FileOutputStream(
                Path.of(outputDir, getShortName(lab) + "_" + releaseName + VARIANT_SHEET)
                    .toFile());
        FileOutputStream cdnaOutputStream =
            new FileOutputStream(Path.of(outputDir, getShortName(lab) + C_DNA_TSV).toFile())) {
      String header =
          String.format(
              VARIANT_FORMAT,
              REFERENCE_SEQUENCE,
              CDNA,
              PREFERRED_CONDITION_NAME,
              CLINICAL_SIGNIFICANCE,
              DATE_LAST_EVALUATED,
              GENE_SYMBOL,
              CLIN_VAR_ACCESSION);
      outputStream.write(header.getBytes());
      for (VariantLine variantLine : entry.getValue()) {

        if (variantLine.getScv() != null || !isUpdateOnly) {
          String scv = variantLine.getScv() != null ? variantLine.getScv() : "";
          String line =
              String.format(
                  VARIANT_FORMAT,
                  variantLine.getTranscript(),
                  variantLine.getCDNA(),
                  getConditionName(variantLine),
                  map(variantLine.getClassification()),
                  DATE_VALUE,
                  variantLine.getGene(),
                  scv);
          outputStream.write(line.getBytes());
          cdnaOutputStream.write(String.format("%s:%s%n", variantLine.getTranscript(), variantLine.getCDNA()).getBytes());
        }
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  private static String map(String classification) {
    String clinVarClass = classification;
    if(classification.equals("VUS")){
      clinVarClass = "Uncertain significance";
    }
    return clinVarClass;
  }

  private static String getConditionName(VariantLine variantLine) {
    String conditionName;
    if (variantLine.getClassification().equals(BENIGN)) {
      conditionName = NOT_SPECIFIED;
    } else {
      conditionName = NOT_PROVIDED;
    }
    return conditionName;
  }
}
