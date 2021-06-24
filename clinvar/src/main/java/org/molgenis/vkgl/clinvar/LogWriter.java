package org.molgenis.vkgl.clinvar;

import static java.util.Objects.requireNonNull;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Path;
import java.util.Set;
import org.molgenis.vkgl.clinvar.model.MappingLine;
import org.molgenis.vkgl.clinvar.model.Settings;

public class LogWriter {

  public enum LineType {
    UNCHANGED,
    UPDATED,
    REMOVED,
    DUPLICATED
  }

  public static final String FILE_NAME_FORMAT = "%s_%s_%s";
  public static final String POSTFIX = "log.tsv";
  private final Settings settings;
  private static final String HEADER =
      "chromosome\tstart\tstop\tref\talt\tgene\tclinvar_accession\tclassification\tlab\tcomment\n";

  public LogWriter(Settings settings) {
    this.settings = requireNonNull(settings);
  }

  public void write(SubmissionDecorator submissionDecorator) {
    write(submissionDecorator.getDuplicatedMappings(), LineType.DUPLICATED);
    write(submissionDecorator.getInvalidMappings(), LineType.REMOVED);
    write(submissionDecorator.getUnchangedMappings(), LineType.UNCHANGED);
    write(submissionDecorator.getUpdatedMappings(), LineType.UPDATED);
  }

  private void write(Set<MappingLine> lines, LineType type) {
    try (FileOutputStream fileOutputStream =
        new FileOutputStream(
            Path.of(
                settings.getOutputDir().toString(),
                String.format(FILE_NAME_FORMAT, settings.getRelease(), type, POSTFIX))
                .toFile())) {
      fileOutputStream.write(HEADER.getBytes());
      lines.stream()
          .map(this::format)
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

  private String format(MappingLine line) {
    return String.format(
        "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%n",
        line.getChromosome(),
        line.getStart(),
        line.getStop(),
        line.getRef(),
        line.getAlt(),
        line.getGene(),
        line.getClinVarAccession(),
        line.getClassification(),
        line.getLab(),
        line.getComment() == null ? "" : (String.format("%s(%s)",line.getComment(), settings.getRelease())));
  }
}
