package org.molgenis.vkgl.clinvar;

import static org.junit.jupiter.api.Assertions.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.util.ResourceUtils;

class ClinVarXmlParserIT {

  @TempDir
  Path sharedTempDir;

  @Test
  void main() throws IOException {
    String inputFile = ResourceUtils.getFile("classpath:clinVar.xml").toString();
    Path outputFile = sharedTempDir.resolve("clinVarActual.tsv");
    File expectedFile = ResourceUtils.getFile("classpath:clinVarExpected.tsv");

    String[] args = {"-i",inputFile,"-o",outputFile.toString()};
    ClinVarXmlParser.main(args);

    assertEquals(Files.readAllLines(expectedFile.toPath()), Files.readAllLines(outputFile));
  }
}