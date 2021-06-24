package org.molgenis.vkgl.clinvar;

import static java.util.Objects.requireNonNull;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Path;
import java.util.Collection;
import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.Settings;

public class DeleteWriter {

  public static final String DELETES_FORMAT = "%s%n";
  public static final String CLIN_VAR_ACCESSION = "ClinVarAccession\n";
  public static final String DELETES_SHEET = "Deletes.tsv";

  private static final String HEADER = CLIN_VAR_ACCESSION;

  private final Path outputDir;
  private final String release;

  public DeleteWriter(Settings settings) {
    this.outputDir = requireNonNull(settings.getOutputDir());
    this.release = requireNonNull(settings.getRelease());
  }

  public void write(Collection<String> deletedAccessions, Lab lab) {
    try (FileOutputStream fileOutputStream =
        new FileOutputStream(
            Path.of(outputDir.toString(),
                String.format("%s_%s.%s", lab.name(), release, DELETES_SHEET))
                .toFile())) {
      fileOutputStream.write(HEADER.getBytes());
      deletedAccessions.stream()
          .map(accession -> String.format(DELETES_FORMAT, accession))
          .map(String::getBytes)
          .forEach(
              accession -> {
                try {
                  fileOutputStream.write(accession);
                } catch (IOException ioException) {
                  throw new UncheckedIOException(ioException);
                }
              });
    } catch (IOException ioException) {
      throw new UncheckedIOException(ioException);
    }
  }
}
