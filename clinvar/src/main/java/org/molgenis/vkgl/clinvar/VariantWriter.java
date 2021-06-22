package org.molgenis.vkgl.clinvar;

import static java.util.Objects.requireNonNull;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Path;
import java.util.Collection;
import org.molgenis.vkgl.clinvar.model.Classification;
import org.molgenis.vkgl.clinvar.model.ConsensusLine;
import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.Settings;
import org.molgenis.vkgl.clinvar.model.SubmissionLine;

public class VariantWriter {

  public static final String VARIANT_FORMAT = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%n";
  public static final String VARIANT_SHEET = "Variant.tsv";

  private static final String CHROMOSOME = "Chromosome";
  private static final String START = "Start";
  private static final String STOP = "Stop";
  private static final String REF = "Reference allele";
  private static final String ALT = "Alternate allele";
  public static final String PREFERRED_CONDITION_NAME = "Preferred condition name";
  public static final String CLINICAL_SIGNIFICANCE = "Clinical significance";
  public static final String DATE_LAST_EVALUATED = "Date last evaluated";
  public static final String GENE_SYMBOL = "Gene symbol";
  public static final String CLIN_VAR_ACCESSION = "ClinVarAccession";
  private static final String NOVEL_OR_UPDATE = "Novel or Update";
  public static final String NOT_PROVIDED = "not provided";
  public static final String NOT_SPECIFIED = "not specified";

  private static final String HEADER =
      String.format(
          VARIANT_FORMAT,
          CHROMOSOME,
          START,
          STOP,
          REF,
          ALT,
          PREFERRED_CONDITION_NAME,
          CLINICAL_SIGNIFICANCE,
          DATE_LAST_EVALUATED,
          GENE_SYMBOL,
          CLIN_VAR_ACCESSION,
          NOVEL_OR_UPDATE);
  public static final String UPDATE = "update";
  public static final String NOVEL = "novel";

  private final Path outputDir;
  private final String release;

  public VariantWriter(Settings settings) {
    this.outputDir = requireNonNull(settings.getOutputDir());
    this.release = requireNonNull(settings.getRelease());
  }

  public void write(Collection<SubmissionLine> variants, Lab lab) {
    try (FileOutputStream fileOutputStream =
        new FileOutputStream(
            Path.of(
                outputDir.toString(),
                String.format("%s_%s.%s", lab.name(), release, VARIANT_SHEET))
                .toFile())) {
      fileOutputStream.write(HEADER.getBytes());
      variants.stream()
          .map(this::toTsvString)
          .map(String::getBytes)
          .forEach(
              line -> {
                try {
                  fileOutputStream.write(line);
                } catch (IOException ioException) {
                  throw new UncheckedIOException(ioException);
                }
              });
    } catch (IOException ioException) {
      throw new UncheckedIOException(ioException);
    }
  }

  private String toTsvString(SubmissionLine submissionLine) {
    ConsensusLine line = submissionLine.getConsensusLine();
    String accession = "";
    String type = NOVEL;
    if (submissionLine.getClinVarAccession() != null) {
      accession = submissionLine.getClinVarAccession();
      type = UPDATE;
    }
    return String.format(
        VARIANT_FORMAT,
        line.getChromosome(),
        line.getStart(),
        line.getStop(),
        line.getRef(),
        line.getAlt(),
        getConditionName(line.getClassification(submissionLine.getLab())),
        line.getClassification(submissionLine.getLab()).getLongName(),
        "",
        line.getGene(),
        accession,
        type);
  }

  private static String getConditionName(Classification classification) {
    String conditionName;
    if (classification.equals(Classification.b)) {
      conditionName = NOT_SPECIFIED;
    } else {
      conditionName = NOT_PROVIDED;
    }
    return conditionName;
  }
}
