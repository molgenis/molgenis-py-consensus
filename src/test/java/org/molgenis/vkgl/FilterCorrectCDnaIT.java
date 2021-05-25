package org.molgenis.vkgl;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.molgenis.vkgl.FilterCorrectCDna.FILTERED;
import static org.molgenis.vkgl.model.LabConstants.getShortName;

import java.io.File;
import java.io.FileNotFoundException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.springframework.util.ResourceUtils;

class FilterCorrectCDnaIT {

  @Test
  void filter() throws FileNotFoundException {
    String vkglDir = ResourceUtils.getFile("classpath:filter").toString();
    Path expectedVariant = ResourceUtils.getFile("classpath:expectedVariant.tsv").toPath();
    Path expectedEvidence = ResourceUtils.getFile("classpath:expectedEvidence.tsv").toPath();
    FilterCorrectCDna.filterLab(vkglDir,"TEST","Diagnostic Laboratory, Department of Genetics,University Medical Center Groningen");

    assertAll(
        () ->
            assertEquals(
                Files.readAllLines(
                    expectedEvidence),
                Files.readAllLines(
                        Path.of(vkglDir.toString(), FILTERED, "UMCG_TEST_ExpEvidence.tsv"))),
            () ->
                assertEquals(
                    Files.readAllLines(expectedVariant),
                    Files.readAllLines(
                        Path.of(vkglDir.toString(), FILTERED, "UMCG_TEST_Variant.tsv"))));
  }
}