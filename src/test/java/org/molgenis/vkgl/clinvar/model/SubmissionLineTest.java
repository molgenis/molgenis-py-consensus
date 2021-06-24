package org.molgenis.vkgl.clinvar.model;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class SubmissionLineTest {

  @ParameterizedTest
  @CsvSource({"b,lb,true", "p,p,false", "vus,vus,false"})
  void isChanged(Classification consensusClass, Classification mappingClass, boolean expected) {
    ConsensusLine consensusLine = ConsensusLine.builder().amc(consensusClass).build();
    MappingLine mappingLine = MappingLine.builder().classification(mappingClass).build();
    SubmissionLine submissionLine =
        SubmissionLine.builder().lab(Lab.amc).consensusLine(consensusLine).mappingLine(mappingLine)
            .build();
    assertEquals(expected, submissionLine.isChanged());
  }

  @ParameterizedTest
  @CsvSource({"1,true", "2,false", "3,false"})
  void isSingleLab(int labs, boolean expected) {
    ConsensusLine consensusLine = ConsensusLine.builder().nrLabs(labs).build();
    SubmissionLine submissionLine = SubmissionLine.builder().consensusLine(consensusLine).build();
    assertEquals(expected, submissionLine.isSingleLab());
  }

  @ParameterizedTest
  @CsvSource({
      "agreement,true",
      "total_agreement,true",
      "disagreement,false",
      "total_disagreement,false"
  })
  void isValidType(Type type, boolean expected) {
    ConsensusLine consensusLine = ConsensusLine.builder().type(type).build();
    SubmissionLine submissionLine = SubmissionLine.builder().consensusLine(consensusLine).build();
    assertEquals(expected, submissionLine.isValidType());
  }

  @ParameterizedTest
  @CsvSource({"1,1,false", "1,17,true", "17,1,true", "17,,false"})
  void isSv(int start, Integer stop, boolean expected) {
    ConsensusLine consensusLine = ConsensusLine.builder().start(start).stop(stop).build();
    SubmissionLine submissionLine = SubmissionLine.builder().consensusLine(consensusLine).build();
    assertEquals(expected, submissionLine.isSv());
  }
}
