package org.molgenis.vkgl.clinvar;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import javax.xml.XMLConstants;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.molgenis.vkgl.model.Result;
import org.xml.sax.SAXException;

public class ClinVarXmlParser {


  public static final String FORMAT = "%s\t%s\t%s\t%s\t%s\n";
  private static final String OPT_INPUT = "i";
  private static final String OPT_OUTPUT = "o";

  public static void main(String[] args) {
    Path input;
    Path output;
    try {
      CommandLineParser commandLineParser = new DefaultParser();
      Options options = new Options();
      options.addOption(
          Option.builder(OPT_INPUT)
              .hasArg(true)
              .required()
              .desc("ClinVar XML file")
              .build());
      options.addOption(
          Option.builder(OPT_OUTPUT)
              .hasArg(true)
              .required()
              .desc("Output tsv file")
              .build());

      CommandLine commandLine = commandLineParser.parse(options, args);

      input = Path.of(commandLine.getOptionValue(OPT_INPUT));
      output = Path.of(commandLine.getOptionValue(OPT_OUTPUT));
    } catch (Exception e) {
      throw new RuntimeException(e);
    }

    parse(input, output);
  }

  private static void parse(Path input, Path output) {
    SAXParserFactory factory = SAXParserFactory.newInstance();
    SAXParser parser;
    try {
      parser = factory.newSAXParser();
      parser.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, ""); // Compliant
      parser.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, ""); // compliant

      File file = input.toFile();
      ClinVarSetHandler clinVarSetHandler = new ClinVarSetHandler();
      parser.parse(file, clinVarSetHandler);
      List<Result> results = clinVarSetHandler.getResults();
      try (FileOutputStream outputStream = new FileOutputStream(
          output.toFile())) {
        String header = String.format(FORMAT, "cDNA", "submissionId", "gene", "class", "lab");
        outputStream.write(header.getBytes());
        for (Result result : results) {
          String line = String
              .format(FORMAT, result.getCDNA(), result.getSubmissionId(), result.getGene(),
                  result.getClassification(), result.getLab());
          outputStream.write(line.getBytes());
        }
      }
    } catch (ParserConfigurationException | SAXException | IOException e) {
      e.printStackTrace();
    }
  }

}
