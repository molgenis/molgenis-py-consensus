package org.molgenis.vkgl.clinvar;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.FileNotFoundException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.molgenis.vkgl.clinvar.model.Classification;
import org.molgenis.vkgl.clinvar.model.ConsensusLine;
import org.molgenis.vkgl.clinvar.model.Type;
import org.springframework.util.ResourceUtils;

class CsvReaderTest {

  @Test
  void read() throws FileNotFoundException {
    CsvReader<ConsensusLine> csvReader = new CsvReader<>();
    Path path = ResourceUtils.getFile("classpath:consensus.tsv").toPath();

    ConsensusLine consensusLine1 =
        new ConsensusLine(
            "1",
            123456,
            123456,
            "C",
            "T",
            "GENE",
            1,
            null,
            Classification.lb,
            null,
            null,
            null,
            null,
            null,
            null,
            Classification.lb,
            Type.total_agreement);
    ConsensusLine consensusLine2 =
        new ConsensusLine(
            "1",
            1234567,
            1234567,
            "C",
            "T",
            "GENE2",
            1,
            null,
            Classification.lb,
            null,
            null,
            null,
            null,
            null,
            null,
            Classification.lb,
            Type.total_agreement);
    List<ConsensusLine> expected = Arrays.asList(consensusLine1, consensusLine2);
    assertEquals(expected, csvReader.read(path, ConsensusLine.class));
  }
}
