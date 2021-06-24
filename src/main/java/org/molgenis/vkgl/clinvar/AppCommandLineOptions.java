package org.molgenis.vkgl.clinvar;

import static java.lang.String.format;

import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;

class AppCommandLineOptions {

  static final String OPT_INPUT = "i";
  static final String OPT_INPUT_LONG = "input";
  static final String OPT_MAPPING = "m";
  static final String OPT_MAPPING_LONG = "mapping";
  static final String OPT_OUTPUT_DIR = "o";
  static final String OPT_OUTPUT_DIR_LONG = "output";
  static final String OPT_RELEASE_NAME = "r";
  static final String OPT_RELEASE_NAME_LONG = "release";
  static final String OPT_DUPLICATE_MODE = "dd";
  static final String OPT_DUPLICATE_LONG = "delete_duplicated";
  static final String OPT_SINGLE_MODE = "s";
  static final String OPT_SINGLE_MODE_LONG = "include_single_lab";
  static final String OPT_FORCE = "f";
  static final String OPT_FORCE_LONG = "force";
  static final String OPT_DEBUG = "d";
  static final String OPT_DEBUG_LONG = "debug";
  static final String OPT_VERSION = "v";
  static final String OPT_VERSION_LONG = "version";
  private static final Options APP_OPTIONS;
  private static final Options APP_VERSION_OPTIONS;

  static {
    Options appOptions = new Options();
    appOptions.addOption(
        Option.builder(OPT_INPUT)
            .hasArg(true)
            .required()
            .longOpt(OPT_INPUT_LONG)
            .desc("VKGL consensus file (tsv).")
            .build());
    appOptions.addOption(
        Option.builder(OPT_MAPPING)
            .hasArg(true)
            .required()
            .longOpt(OPT_MAPPING_LONG)
            .desc("Mapping file containing position and ClinVar Accessions (tsv).")
            .build());
    appOptions.addOption(
        Option.builder(OPT_OUTPUT_DIR)
            .hasArg(true)
            .required()
            .longOpt(OPT_OUTPUT_DIR_LONG)
            .desc("Directory to write output to.")
            .build());
    appOptions.addOption(
        Option.builder(OPT_RELEASE_NAME)
            .hasArg(true)
            .required()
            .longOpt(OPT_RELEASE_NAME_LONG)
            .desc("Release name to use in ClinVar file names.")
            .build());
    appOptions.addOption(
        Option.builder(OPT_DUPLICATE_MODE)
            .longOpt(OPT_DUPLICATE_LONG)
            .desc("Flag to indicate is existing duplicated should be deleted.")
            .build());
    appOptions.addOption(
        Option.builder(OPT_SINGLE_MODE)
            .longOpt(OPT_SINGLE_MODE_LONG)
            .desc("Flag to indicate that single lab submissions should also be submitted.")
            .build());
    appOptions.addOption(
        Option.builder(OPT_FORCE)
            .longOpt(OPT_FORCE_LONG)
            .desc("Override the output files if output directory already exists.")
            .build());
    appOptions.addOption(
        Option.builder(OPT_DEBUG)
            .longOpt(OPT_DEBUG_LONG)
            .desc("Enable debug mode (additional logging).")
            .build());
    APP_OPTIONS = appOptions;
    Options appVersionOptions = new Options();
    appVersionOptions.addOption(
        Option.builder(OPT_VERSION)
            .required()
            .longOpt(OPT_VERSION_LONG)
            .desc("Print version.")
            .build());
    APP_VERSION_OPTIONS = appVersionOptions;
  }

  private AppCommandLineOptions() {
  }

  static Options getAppOptions() {
    return APP_OPTIONS;
  }

  static Options getAppVersionOptions() {
    return APP_VERSION_OPTIONS;
  }

  static void validateCommandLine(CommandLine commandLine) {
    validateInput(commandLine);
    validateMapping(commandLine);
    validateOutput(commandLine);
  }

  private static void validateInput(CommandLine commandLine) {
    Path inputPath = Path.of(commandLine.getOptionValue(OPT_INPUT));
    validateTsv(inputPath);
  }

  private static void validateMapping(CommandLine commandLine) {
    Path mappingPath = Path.of(commandLine.getOptionValue(OPT_MAPPING));
    validateTsv(mappingPath);
  }

  private static void validateTsv(Path inputPath) {
    if (!Files.exists(inputPath)) {
      throw new IllegalArgumentException(
          format("Input file '%s' does not exist.", inputPath.toString()));
    }
    if (Files.isDirectory(inputPath)) {
      throw new IllegalArgumentException(
          format("Input file '%s' is a directory.", inputPath.toString()));
    }
    if (!Files.isReadable(inputPath)) {
      throw new IllegalArgumentException(
          format("Input file '%s' is not readable.", inputPath.toString()));
    }
    String inputPathStr = inputPath.toString();
    if (!inputPathStr.endsWith(".vcf") && !inputPathStr.endsWith(".tsv")) {
      throw new IllegalArgumentException(
          format("Input file '%s' is not a .tsv file.", inputPathStr));
    }
  }

  private static void validateOutput(CommandLine commandLine) {
    if (!commandLine.hasOption(OPT_OUTPUT_DIR)) {
      return;
    }

    Path outputPath = Path.of(commandLine.getOptionValue(OPT_OUTPUT_DIR));

    if (!commandLine.hasOption(OPT_FORCE) && !Files.isDirectory(outputPath)) {
      throw new IllegalArgumentException(
          format("Output '%s' is not a directory.", outputPath.toString()));
    }

    if (outputPath.toFile().listFiles().length > 0 && !commandLine.hasOption(OPT_FORCE)) {
      throw new IllegalArgumentException(
          format(
              "Output directory '%s' is not empty, use '-f' to overwrite existing files.",
              outputPath.toString()));
    }
  }
}
