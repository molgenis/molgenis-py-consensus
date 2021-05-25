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

  public static final String EXP_EVIDENCE_FORMAT = "%s\t%s\t%s\t%s\t%s\n";
  public static final String VARIANT_FORMAT = "%s\t%s\t%s\t%s\t%s\t%s\n";
  public static final String DELETES_FORMAT = "%s\n";

  public static final String HGVS_NAME = "HGVS name";
  public static final String PREFERRED_CONDITION_NAME = "Preferred condition name";
  public static final String CLINICAL_SIGNIFICANCE = "Clinical significance";
  public static final String DATE_LAST_EVALUATED = "Date last evaluated";
  public static final String GENE_SYMBOL = "Gene symbol";
  public static final String CLIN_VAR_ACCESSION = "ClinVarAccession";
  public static final String VARIANT_NAME = "Variant name";
  public static final String COLLECTION_METHOD = "Collection method";
  public static final String ALLELE_ORIGIN = "Allele origin";
  public static final String AFFECTED_STATUS = "Affected status";
  public static final String NOT_PROVIDED = "Not Provided";
  public static final String COLLECTION_METHOD_VALUE = "clinical testing";
  public static final String ALLELE_ORIGIN_VALUE = "germline";
  public static final String AFFECTED_STATUS_VALUE = "yes";
  public static final String DATE_VALUE = "";
  public static final String NOT_SPECIFIED = "not specified";
  public static final String BENIGN = "Benign";
  public static final String VARIANT_SHEET = "_Variant.tsv";
  public static final String EVIDENCE_SHEET = "_ExpEvidence.tsv";
  public static final String DELETES_SHEET = "_Deletes.tsv";

  private ClinVarWriter(){}

  public static void write(ClinVarData clinVarData, String outputDir, String releaseName) {

    for (Entry<String, List<VariantLine>> entry : clinVarData.getVariants().entrySet()) {
      writeVariants(releaseName, entry, outputDir);
      writeExpEvidence(releaseName, entry, outputDir);
    }

      for (Entry<String, List<DeletesLine>> entry : clinVarData.getDeletes().entrySet()) {
        writeDeletes(releaseName, entry, outputDir);
      }
  }

  private static void writeDeletes(String releaseName, Entry<String, List<DeletesLine>> entry,
      String outputDir) {
    String lab = entry.getKey();
    try (FileOutputStream outputStream = new FileOutputStream(Path.of(
        outputDir, getShortName(lab) + "_" + releaseName + DELETES_SHEET).toFile())) {
      outputStream.write(String.format(DELETES_FORMAT, CLIN_VAR_ACCESSION).getBytes());
      for (DeletesLine deletesLine : entry.getValue()) {
        outputStream.write(String.format(DELETES_FORMAT, deletesLine.getSvc()).getBytes());
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  private static void writeExpEvidence(String releaseName, Entry<String, List<VariantLine>> entry,
      String outputDir) {
    String lab = entry.getKey();
    try (FileOutputStream outputStream = new FileOutputStream(Path.of(
        outputDir, getShortName(lab) + "_" + releaseName + EVIDENCE_SHEET).toFile())) {
      String header = String
          .format(EXP_EVIDENCE_FORMAT, VARIANT_NAME, PREFERRED_CONDITION_NAME, COLLECTION_METHOD,
              ALLELE_ORIGIN,
              AFFECTED_STATUS);
      outputStream.write(header.getBytes());
      for (VariantLine variantLine : entry.getValue()) {
          String line = String
              .format(EXP_EVIDENCE_FORMAT, variantLine.getHgvs(), getConditionName(variantLine),
                  COLLECTION_METHOD_VALUE, ALLELE_ORIGIN_VALUE, AFFECTED_STATUS_VALUE);
          outputStream.write(line.getBytes());
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
  }

  private static void writeVariants(String releaseName, Entry<String, List<VariantLine>> entry,
      String outputDir) {
    String lab = entry.getKey();
    try (FileOutputStream outputStream = new FileOutputStream(Path.of(
        outputDir, getShortName(lab) + "_" + releaseName + VARIANT_SHEET).toFile())) {
      String header = String
          .format(VARIANT_FORMAT, HGVS_NAME, PREFERRED_CONDITION_NAME, CLINICAL_SIGNIFICANCE,
              DATE_LAST_EVALUATED, GENE_SYMBOL, CLIN_VAR_ACCESSION);
      outputStream.write(header.getBytes());
      for (VariantLine variantLine : entry.getValue()) {

          String scv = variantLine.getScv() != null ? variantLine.getScv() : "";
          String line = String
              .format(VARIANT_FORMAT, variantLine.getHgvs(), getConditionName(variantLine),
                  variantLine.getClassification(),
                  DATE_VALUE, variantLine.getGene(), scv);
          outputStream.write(line.getBytes());
      }
    } catch (IOException e) {
      e.printStackTrace();
    }
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
