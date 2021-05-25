package org.molgenis.vkgl;

import java.nio.file.Path;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.molgenis.vkgl.clinvar.ClinVarWriter;
import org.molgenis.vkgl.model.ClinVarData;
import org.molgenis.vkgl.model.Settings;

public class VkglToClinVarMapper {

  private static final String OPT_INPUT_CONSENSUS = "i";
  private static final String OPT_INPUT_CLINVAR = "c";
  private static final String OPT_VKGL_DIR = "d";
  private static final String OPT_OUTPUT_DIR = "o";
  private static final String OPT_RELEASE_NAME = "r";
  private static final String OPT_FILTER = "f";

  public static void main(String[] args) {
    Settings settings = parseCmd(args);

    ConsensusMatcher matcher = new ConsensusMatcher(settings.getConsensusPath(),
        settings.getClinVarPath(), settings.getBasePath(),
        settings.getNoSubmitClassifications());
    ClinVarData clinVarData = matcher.match();
    ClinVarWriter.write(clinVarData, settings.getReleaseName(), settings.getOutputDir());
  }

  private static Settings parseCmd(String[] args) {
    try {
      CommandLineParser commandLineParser = new DefaultParser();
      Options options = new Options();
      options.addOption(
          Option.builder(OPT_INPUT_CONSENSUS)
              .hasArg(true)
              .required()
              .desc("VKGL nonpublic consensus file in tsv format")
              .build());
      options.addOption(
          Option.builder(OPT_INPUT_CLINVAR)
              .hasArg(true)
              .required()
              .desc("Parsed tsv result from ClinVarXmlParser")
              .build());
      options.addOption(
          Option.builder(OPT_VKGL_DIR)
              .hasArg(true)
              .required()
              .desc("Directory with preprocessed VKGL files (vkgl_[LAB])")
              .build());
      options.addOption(
          Option.builder(OPT_OUTPUT_DIR)
              .hasArg(true)
              .required()
              .desc("Directory where output (clinVar Submission files) should go")
              .build());
      options.addOption(
          Option.builder(OPT_RELEASE_NAME)
              .hasArg(true)
              .required()
              .desc("Name for the release, used in the file names e.g. OKT2017")
              .build());
      options.addOption(
          Option.builder(OPT_FILTER)
              .hasArg(true)
              .desc("Which categories in the consensus should be skipped e.g. 'No Consensus'")
              .build());
      CommandLine commandLine = commandLineParser.parse(options, args);

      Path consensusPath = Path.of(commandLine.getOptionValue(OPT_INPUT_CONSENSUS));
      Path clinVarPath = Path.of(commandLine.getOptionValue(OPT_INPUT_CLINVAR));
      String basePath = commandLine.getOptionValue(OPT_VKGL_DIR);
      List<String> noSubmitClassifications = Collections.emptyList();
      if (commandLine.hasOption(OPT_FILTER)) {
        noSubmitClassifications = Arrays
            .asList(commandLine.getOptionValue(OPT_FILTER).split(","));
      }
      String releaseName = commandLine.getOptionValue(OPT_RELEASE_NAME);
      String outputDir = commandLine.getOptionValue(OPT_OUTPUT_DIR);

      return new Settings(consensusPath, clinVarPath, basePath,
          noSubmitClassifications, outputDir, releaseName);
    } catch (ParseException e) {
      throw new RuntimeException(e);
    }
  }
}
