package org.molgenis.vkgl.clinvar;

import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.molgenis.vkgl.clinvar.model.Lab.amc;
import static org.molgenis.vkgl.clinvar.model.Lab.erasmus_mc;
import static org.molgenis.vkgl.clinvar.model.Lab.lumc;
import static org.molgenis.vkgl.clinvar.model.Lab.nki;
import static org.molgenis.vkgl.clinvar.model.Lab.radboud_mumc;
import static org.molgenis.vkgl.clinvar.model.Lab.umc_utrecht;
import static org.molgenis.vkgl.clinvar.model.Lab.umcg;
import static org.molgenis.vkgl.clinvar.model.Lab.vumc;

import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.molgenis.vkgl.clinvar.model.ConsensusLine;
import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.MappingLine;
import org.molgenis.vkgl.clinvar.model.SubmissionLine;
import org.molgenis.vkgl.clinvar.model.VariantId;

@ExtendWith(MockitoExtension.class)
class SubmissionDecoratorTest {

  @Mock
  ClinVarMapping mapping;
  @Mock
  LabSubmission umcgLabSubmission;
  @Mock
  LabSubmission amcLabSubmission;
  @Mock
  LabSubmission otherLabSubmission;
  @Mock
  SubmissionLine submissionLine1;
  @Mock
  SubmissionLine submissionLine2;
  @Mock
  SubmissionLine submissionLine3;
  @Mock
  SubmissionLine submissionLine4;
  @Mock
  MappingLine mappingLine1;
  @Mock
  MappingLine mappingLine3;
  @Mock
  MappingLine mappingLine4;

  private SubmissionDecorator submissionDecorator;

  @BeforeEach
  void setUp() {
    submissionDecorator = new SubmissionDecorator(mapping);
    Map<Lab, LabSubmission> labSubmissionMap =
        Map.of(
            umcg,
            umcgLabSubmission,
            umc_utrecht,
            otherLabSubmission,
            vumc,
            otherLabSubmission,
            amc,
            amcLabSubmission,
            nki,
            otherLabSubmission,
            radboud_mumc,
            otherLabSubmission,
            erasmus_mc,
            otherLabSubmission,
            lumc,
            otherLabSubmission);
    submissionDecorator.setSubmissionLabContextMap(labSubmissionMap);
  }

  @Test
  void getUpdated() {
    when(umcgLabSubmission.getUpdated()).thenReturn(Set.of(submissionLine1, submissionLine2));
    assertEquals(Set.of(submissionLine1, submissionLine2), submissionDecorator.getUpdated(umcg));
  }

  @Test
  void getInvalid() {
    when(umcgLabSubmission.getInvalid()).thenReturn(Set.of(submissionLine1, submissionLine2));
    assertEquals(Set.of(submissionLine1, submissionLine2), submissionDecorator.getInvalid(umcg));
  }

  @Test
  void getDuplicates() {
    when(umcgLabSubmission.getDuplicated())
        .thenReturn(
            Map.of(new VariantId("1", 1, 2, "T", "A"), Set.of(submissionLine1, submissionLine2)));
    assertEquals(
        Map.of(new VariantId("1", 1, 2, "T", "A"), Set.of(submissionLine1, submissionLine2)),
        submissionDecorator.getDuplicated(umcg));
  }

  @Test
  void addConsensusLine() {
    ConsensusLine line = mock(ConsensusLine.class);
    submissionDecorator.addConsensusLine(line, umcg);

    verify(umcgLabSubmission).addConsensusLine(line);
  }

  @Test
  void getDuplicatedMappings() {
    doReturn(mappingLine1).when(submissionLine1).getMappingLine();
    doReturn(mappingLine3).when(submissionLine3).getMappingLine();
    doReturn(mappingLine4).when(submissionLine4).getMappingLine();
    when(umcgLabSubmission.getDuplicated())
        .thenReturn(
            Map.of(
                new VariantId("1", 1, 2, "T", "A"),
                Set.of(submissionLine1, submissionLine2),
                new VariantId("2", 1, 2, "T", "A"),
                Set.of(submissionLine3, submissionLine4)));
    assertEquals(
        Set.of(mappingLine1, mappingLine3, mappingLine4),
        submissionDecorator.getDuplicatedMappings());
  }

  @Test
  void getInvalidMappings() {
    doReturn(mappingLine1).when(submissionLine1).getMappingLine();
    doReturn(mappingLine3).when(submissionLine3).getMappingLine();
    doReturn(mappingLine4).when(submissionLine4).getMappingLine();
    when(amcLabSubmission.getInvalid()).thenReturn(Set.of(submissionLine1, submissionLine2));
    when(umcgLabSubmission.getInvalid()).thenReturn(Set.of(submissionLine3, submissionLine4));
    assertEquals(
        Set.of(mappingLine1, mappingLine3, mappingLine4), submissionDecorator.getInvalidMappings());
  }

  @Test
  void getUnchangedMappings() {
    doReturn(mappingLine1).when(submissionLine1).getMappingLine();
    doReturn(mappingLine3).when(submissionLine3).getMappingLine();
    doReturn(mappingLine4).when(submissionLine4).getMappingLine();
    when(amcLabSubmission.getUnchanged()).thenReturn(Set.of(submissionLine1, submissionLine2));
    when(umcgLabSubmission.getUnchanged()).thenReturn(Set.of(submissionLine3, submissionLine4));
    assertEquals(
        Set.of(mappingLine1, mappingLine3, mappingLine4),
        submissionDecorator.getUnchangedMappings());
  }

  @Test
  void getUpdatedMappings() {
    doReturn(mappingLine1).when(submissionLine1).getMappingLine();
    doReturn(mappingLine3).when(submissionLine3).getMappingLine();
    doReturn(mappingLine4).when(submissionLine4).getMappingLine();
    when(amcLabSubmission.getUpdated()).thenReturn(Set.of(submissionLine1, submissionLine2));
    when(umcgLabSubmission.getUpdated()).thenReturn(Set.of(submissionLine3, submissionLine4));
    assertEquals(
        Set.of(mappingLine1, mappingLine3, mappingLine4), submissionDecorator.getUpdatedMappings());
  }

  @Test
  void getAccessionsToDelete() {
    doReturn("123").when(submissionLine1).getClinVarAccession();
    doReturn("234").when(submissionLine3).getClinVarAccession();
    doReturn("345").when(submissionLine4).getClinVarAccession();

    doReturn(mappingLine1).when(submissionLine1).getMappingLine();
    doReturn(mappingLine3).when(submissionLine3).getMappingLine();
    doReturn(mappingLine4).when(submissionLine4).getMappingLine();
    when(umcgLabSubmission.getDuplicated())
        .thenReturn(
            Map.of(new VariantId("1", 1, 2, "T", "A"), Set.of(submissionLine1, submissionLine2)));
    when(umcgLabSubmission.getInvalid()).thenReturn(Set.of(submissionLine3, submissionLine4));

    assertEquals(
        Set.of("123", "345", "234"),
        submissionDecorator.getAccessionsToDelete(umcg, true));
  }

  @Test
  void variantTriage() {
    submissionDecorator.variantTraige(true);

    assertAll(
        () -> verify(umcgLabSubmission).variantTriage(true),
        () -> verify(amcLabSubmission).variantTriage(true),
        () -> verify(otherLabSubmission, times(6)).variantTriage(true));
  }
}
