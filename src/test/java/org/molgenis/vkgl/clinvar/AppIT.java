package org.molgenis.vkgl.clinvar;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.boot.SpringApplication;
import org.springframework.util.ResourceUtils;

class AppIT {

  @TempDir
  Path sharedTempDir;

  @Test
  void test() throws IOException {
    String consensusFile = ResourceUtils.getFile("classpath:IT_Consensus.tsv").toString();
    String mappingFile = ResourceUtils.getFile("classpath:IT_Mapping.tsv").toString();

    String[] args = {"-i", consensusFile, "-m", mappingFile, "-o", sharedTempDir.toString(), "-r",
        "IT", "-dd" };
    SpringApplication.run(App.class, args);

    File[] expectedFiles = new File("src/test/resources/expected/IT").listFiles();
    testDirectoryContent(expectedFiles);
  }

  private void testDirectoryContent(File[] expectedFiles) throws IOException {
    for (File expected : expectedFiles) {
      String filename = expected.getName();
      Path actual = Path.of(sharedTempDir.toString(), filename);
      Set<String> expectedOutput = getLinesSet(expected.toPath());
      Set<String> actualOutput = getLinesSet(actual);

      System.out.println("Checking " + filename);
      assertEquals(expectedOutput, actualOutput);
      System.out.println("Done checking " + filename);
    }
  }

  private Set<String> getLinesSet(Path path) throws IOException {
    return Arrays.stream(Files.readString(path).replaceAll("\\R", "\n").split("\n")).collect(
        Collectors.toSet());
  }
}
