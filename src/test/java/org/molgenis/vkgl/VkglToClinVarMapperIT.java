package org.molgenis.vkgl;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.molgenis.vkgl.model.LabConstants.getShortName;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.molgenis.vkgl.model.LabConstants;
import org.springframework.util.ResourceUtils;

class VkglToClinVarMapperIT {

  @TempDir Path sharedTempDir;

  @Test
  void main() throws IOException {

    String vkglDir = ResourceUtils.getFile("classpath:vkgl").toString();
    String clinVarFile = ResourceUtils.getFile("classpath:clinVar.tsv").toString();
    String consensusFile = ResourceUtils.getFile("classpath:consensus.tsv").toString();

    String[] args = {
      "-i",
      consensusFile,
      "-o",
      sharedTempDir.toString(),
      "-c",
      clinVarFile,
      "-d",
      vkglDir,
      "-r",
      "TEST"
    };
    VkglToClinVarMapper.main(args);

    for (String lab : LabConstants.getAllLabs()) {
      assertAll(
          () ->
              assertEquals(
                  Files.readAllLines(
                      ResourceUtils.getFile(
                              String.format("classpath:%s_TEST_Deletes.tsv", getShortName(lab)))
                          .toPath()),
                  Files.readAllLines(
                      new File(
                              sharedTempDir.toString()
                                  + File.separator
                                  + String.format("%s_TEST_Deletes.tsv", getShortName(lab)))
                          .toPath())),
          () ->
              assertEquals(
                  Files.readAllLines(
                      ResourceUtils.getFile(
                              String.format("classpath:%s_TEST_Variant.tsv", getShortName(lab)))
                          .toPath()),
                  Files.readAllLines(
                      new File(
                              sharedTempDir.toString()
                                  + File.separator
                                  + String.format("%s_TEST_Variant.tsv", getShortName(lab)))
                          .toPath())));
    }
  }

  @Test
  void mainUpdate() throws IOException {

    String vkglDir = ResourceUtils.getFile("classpath:vkgl").toString();
    String clinVarFile = ResourceUtils.getFile("classpath:clinVar.tsv").toString();
    String consensusFile = ResourceUtils.getFile("classpath:consensus.tsv").toString();

    String[] args = {
      "-i",
      consensusFile,
      "-o",
      sharedTempDir.toString(),
      "-c",
      clinVarFile,
      "-d",
      vkglDir,
      "-r",
      "UPDATE",
      "-u"
    };
    VkglToClinVarMapper.main(args);

    assertAll(
        () ->
            assertEquals(
                Files.readAllLines(
                    ResourceUtils.getFile("classpath:ERASMUS_UPDATE_Variant.tsv").toPath()),
                Files.readAllLines(
                    new File(
                            sharedTempDir.toString()
                                + File.separator
                                + String.format("ERASMUS_UPDATE_Variant.tsv"))
                        .toPath())),
        () ->
            assertEquals(
                Files.readAllLines(
                    ResourceUtils.getFile("classpath:UMCG_UPDATE_Variant.tsv").toPath()),
                Files.readAllLines(
                    new File(sharedTempDir.toString() + File.separator + "UMCG_UPDATE_Variant.tsv")
                        .toPath())));
  }
}
