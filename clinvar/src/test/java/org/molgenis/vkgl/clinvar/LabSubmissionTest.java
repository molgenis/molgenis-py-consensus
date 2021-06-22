package org.molgenis.vkgl.clinvar;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.when;
import static org.molgenis.vkgl.clinvar.model.Lab.umcg;

import java.util.Arrays;
import java.util.Collections;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.molgenis.vkgl.clinvar.model.Classification;
import org.molgenis.vkgl.clinvar.model.ConsensusLine;
import org.molgenis.vkgl.clinvar.model.MappingLine;
import org.molgenis.vkgl.clinvar.model.SubmissionLine;
import org.molgenis.vkgl.clinvar.model.Type;
import org.molgenis.vkgl.clinvar.model.VariantGeneId;
import org.molgenis.vkgl.clinvar.model.VariantId;

@ExtendWith(MockitoExtension.class)
class LabSubmissionTest {

  private LabSubmission labSubmission;

  @Mock
  ClinVarMapping mapping;

  ConsensusLine consensusLine1 =
      ConsensusLine.builder()
          .chromosome("1")
          .start(2)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE")
          .umcg(Classification.lp)
          .nrLabs(1)
          .type(Type.total_agreement)
          .build();
  SubmissionLine submissionLine1 = new SubmissionLine(consensusLine1, umcg, null);

  ConsensusLine consensusLine2 =
      ConsensusLine.builder()
          .chromosome("1")
          .start(2)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE2")
          .umcg(Classification.p)
          .nrLabs(1)
          .type(Type.total_agreement)
          .build();
  MappingLine mappingLine2 =
      MappingLine.builder()
          .chromosome("1")
          .start(2)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE2")
          .clinVarAccession("234")
          .classification(Classification.b)
          .build();
  SubmissionLine submissionLine2 = new SubmissionLine(consensusLine2, umcg, mappingLine2);

  ConsensusLine consensusLine3 =
      ConsensusLine.builder()
          .chromosome("1")
          .start(2)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE3")
          .umcg(Classification.b)
          .nrLabs(1)
          .type(Type.total_agreement)
          .build();
  MappingLine mappingLine3 =
      MappingLine.builder()
          .chromosome("1")
          .start(2)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE3")
          .clinVarAccession("345")
          .classification(Classification.b)
          .build();
  SubmissionLine submissionLine3 = new SubmissionLine(consensusLine3, umcg, mappingLine3);
  ConsensusLine consensusLine4 =
      ConsensusLine.builder()
          .chromosome("1")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE2")
          .umcg(Classification.b)
          .nrLabs(1)
          .type(Type.total_agreement)
          .build();
  MappingLine mappingLine4 =
      MappingLine.builder()
          .chromosome("1")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE3")
          .clinVarAccession("456")
          .classification(Classification.b)
          .build();
  SubmissionLine submissionLine4 = new SubmissionLine(consensusLine4, umcg, mappingLine4);
  ConsensusLine consensusLine5 =
      ConsensusLine.builder()
          .chromosome("3")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE2")
          .umcg(Classification.b)
          .nrLabs(2)
          .type(Type.disagreement)
          .build();
  MappingLine mappingLine5 =
      MappingLine.builder()
          .chromosome("3")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE3")
          .clinVarAccession("567")
          .classification(Classification.p)
          .build();
  SubmissionLine submissionLine5 = new SubmissionLine(consensusLine5, umcg, mappingLine5);
  ConsensusLine consensusLine6 =
      ConsensusLine.builder()
          .chromosome("2")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE2")
          .umcg(Classification.b)
          .nrLabs(2)
          .type(Type.agreement)
          .build();
  MappingLine mappingLine6 =
      MappingLine.builder()
          .chromosome("2")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE3")
          .clinVarAccession("678")
          .classification(Classification.p)
          .build();
  SubmissionLine submissionLine6 = new SubmissionLine(consensusLine6, umcg, mappingLine6);
  ConsensusLine consensusLine7 =
      ConsensusLine.builder()
          .chromosome("4")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE2")
          .umcg(Classification.b)
          .nrLabs(1)
          .type(Type.total_agreement)
          .build();
  MappingLine mappingLine7 =
      MappingLine.builder()
          .chromosome("4")
          .start(3)
          .stop(3)
          .ref("T")
          .alt("A")
          .gene("GENE3")
          .clinVarAccession("789")
          .classification(Classification.p)
          .build();
  SubmissionLine submissionLine7 = new SubmissionLine(consensusLine7, umcg, mappingLine7);

  @BeforeEach
  void setUp() {
    labSubmission = new LabSubmission(umcg, mapping);
  }

  @Test
  void addConsensusLine() {
    Map<VariantId, SubmissionLine> expected =
        Collections.singletonMap(new VariantId("1", 2, 3, "T", "A"), submissionLine1);

    labSubmission.addConsensusLine(consensusLine1);

    assertEquals(expected, labSubmission.getConsensusLines());
  }

  @Test
  void addConsensusLineDuplicated() {
    doReturn(false).when(mapping).containsKey(umcg, new VariantGeneId(consensusLine1));
    doReturn(true).when(mapping).containsKey(umcg, new VariantGeneId(consensusLine2));
    doReturn(mappingLine2).when(mapping).getMapping(umcg, new VariantGeneId(consensusLine2));
    doReturn(true).when(mapping).containsKey(umcg, new VariantGeneId(consensusLine3));
    doReturn(mappingLine3).when(mapping).getMapping(umcg, new VariantGeneId(consensusLine3));

    Map<VariantId, Set<SubmissionLine>> expectedDuplicates =
        Collections.singletonMap(
            new VariantId("1", 2, 3, "T", "A"),
            Set.of(submissionLine1, submissionLine2, submissionLine3));

    labSubmission.addConsensusLine(consensusLine1);
    labSubmission.addConsensusLine(consensusLine2);
    labSubmission.addConsensusLine(consensusLine3);

    assertAll(
        () -> assertEquals(Collections.emptyMap(), labSubmission.getConsensusLines()),
        () -> assertEquals(expectedDuplicates, labSubmission.getDuplicated()));
  }

  @Test
  void variantTriage() {
    labSubmission.setConsensusLines(
        Map.of(
            new VariantId(submissionLine1.getConsensusLine()),
            submissionLine1,
            new VariantId(submissionLine4.getConsensusLine()),
            submissionLine4,
            new VariantId(submissionLine5.getConsensusLine()),
            submissionLine5,
            new VariantId(submissionLine6.getConsensusLine()),
            submissionLine6,
            new VariantId(submissionLine7.getConsensusLine()),
            submissionLine7));

    labSubmission.variantTriage(true);

    assertAll(
        () -> assertEquals(Set.of(submissionLine5), labSubmission.getInvalid()),
        () -> assertEquals(Set.of(submissionLine4), labSubmission.getUnchanged()),
        () ->
            assertEquals(
                Set.of(submissionLine1, submissionLine6, submissionLine7),
                labSubmission.getUpdated())
    );
  }

  @Test
  void variantTriageMin2Labs() {
    labSubmission.setConsensusLines(
        Map.of(
            new VariantId(submissionLine1.getConsensusLine()),
            submissionLine1,
            new VariantId(submissionLine4.getConsensusLine()),
            submissionLine4,
            new VariantId(submissionLine5.getConsensusLine()),
            submissionLine5,
            new VariantId(submissionLine6.getConsensusLine()),
            submissionLine6,
            new VariantId(submissionLine7.getConsensusLine()),
            submissionLine7));

    labSubmission.variantTriage(false);

    assertAll(
        () -> assertEquals(Set.of(submissionLine1, submissionLine5, submissionLine7),
            labSubmission.getInvalid()),
        () -> assertEquals(Set.of(submissionLine4), labSubmission.getUnchanged()),
        () ->
            assertEquals(
                Set.of(submissionLine6),
                labSubmission.getUpdated()),
        () -> assertEquals("Invalid consensus type: disagreement.",
            submissionLine5.getMappingLine().getComment()),
        () -> assertEquals("Updated: was 'p' is now 'b'.",
            submissionLine6.getMappingLine().getComment()),
        () -> assertEquals("Invalid: classified by a single lab.",
            submissionLine7.getMappingLine().getComment()));
  }

  @Test
  void getMissedAccessions() {
    when(mapping.getAllMappingLines(umcg))
        .thenReturn(Arrays.asList(mappingLine2, mappingLine3, mappingLine4, mappingLine5));

    doReturn(false).when(mapping).containsKey(umcg, new VariantGeneId(consensusLine1));
    doReturn(true).when(mapping).containsKey(umcg, new VariantGeneId(consensusLine2));
    doReturn(mappingLine2).when(mapping).getMapping(umcg, new VariantGeneId(consensusLine2));
    doReturn(true).when(mapping).containsKey(umcg, new VariantGeneId(consensusLine4));
    doReturn(mappingLine4).when(mapping).getMapping(umcg, new VariantGeneId(consensusLine4));

    labSubmission.addConsensusLine(consensusLine1);
    labSubmission.addConsensusLine(consensusLine2);
    labSubmission.addConsensusLine(consensusLine4);

    assertEquals(Set.of("345", "567"), labSubmission.getMissedAccessions());
  }
}
