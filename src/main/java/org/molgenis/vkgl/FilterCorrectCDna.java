package org.molgenis.vkgl;

import static org.molgenis.vkgl.clinvar.ClinVarWriter.EVIDENCE_SHEET;
import static org.molgenis.vkgl.clinvar.ClinVarWriter.VARIANT_SHEET;
import static org.molgenis.vkgl.model.LabConstants.getShortName;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.molgenis.vkgl.model.LabConstants;

public class FilterCorrectCDna {

  public static final String FILTERED = "filtered";
  private static final String OPT_INPUT = "i";
  private static final String OPT_RELEASE = "r";

  public static void main(String[] args) {
    String input;
    String release;
    try {
      CommandLineParser commandLineParser = new DefaultParser();
      Options options = new Options();
      options.addOption(
          Option.builder(OPT_INPUT)
              .hasArg(true)
              .required()
              .desc("Directory with the ClinVar submission files + mutalyzer results")
              .build());
      options.addOption(Option.builder(OPT_RELEASE)
          .hasArg(true)
          .required()
          .desc("Release name")
          .build());

      CommandLine commandLine = commandLineParser.parse(options, args);

      input = commandLine.getOptionValue(OPT_INPUT);
      release = commandLine.getOptionValue(OPT_RELEASE);
    } catch (Exception e) {
      e.printStackTrace();
      throw new RuntimeException(e);
    }

    filter(input, release);
  }

  public static void filter(String basePath, String release) {
    for (String labName : LabConstants.getAllLabs()) {
      filterLab(basePath, release, labName);
    }
    }

  protected static void filterLab(String basePath, String release, String labName) {
    String lab = getShortName(labName);
    String variantsFile = String.format("%s_%s%s", lab, release, VARIANT_SHEET);
    String evidenceFile = String.format("%s_%s%s", lab, release, EVIDENCE_SHEET);
    String validationFile = String.format("%s_validated.tsv", lab);
    List<String> validatedCdna = new ArrayList<>();
    createDir(basePath, FILTERED);
    try (BufferedReader validationReader = Files.newBufferedReader(Path.of(basePath, validationFile));
        BufferedReader evidenceReader = Files.newBufferedReader(Path.of(basePath, evidenceFile));
        BufferedReader variantsReader = Files.newBufferedReader(Path.of(basePath, variantsFile));
        FileOutputStream variantsOutputStream =
            new FileOutputStream(Path.of(basePath, FILTERED, variantsFile).toFile());
        FileOutputStream evidenceOutputStream =
            new FileOutputStream(Path.of(basePath, FILTERED, evidenceFile).toFile())) {
      validationReader
          .lines()
          .skip(1)
          .forEach(
              line -> {
                String[] split = line.split("\t", -1);
                if (split[1].isEmpty()) {
                  validatedCdna.add(split[0]);
                }
              });
      variantsReader
          .lines()
          .skip(1)
          .forEach(
              line -> {
                String[] split = line.split("\t");
                if (validatedCdna.contains(split[0])) {
                  try {
                    variantsOutputStream.write(String.format("%s%n",line).getBytes());
                  } catch (IOException e) {
                    throw new UncheckedIOException(e);
                  }
                }
              });
      evidenceReader
          .lines()
          .skip(1)
          .forEach(
              line -> {
                String[] split = line.split("\t");
                if (validatedCdna.contains(split[0])) {
                  try {
                    evidenceOutputStream.write(String.format("%s%n",line).getBytes());
                  } catch (IOException e) {
                    throw new UncheckedIOException(e);
                  }
                }
              });
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }

  private static void createDir(String basePath, String... parts) {
    try {
      Path path = Path.of(basePath, parts);
      if (!path.toFile().exists()) {
        Files.createDirectory(path);
      }
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
  }
}
