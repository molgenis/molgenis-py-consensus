package org.molgenis.vkgl.clinvar;

import static java.util.Objects.requireNonNull;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import org.molgenis.vkgl.clinvar.model.ConsensusLine;
import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.MappingLine;
import org.molgenis.vkgl.clinvar.model.SubmissionLine;
import org.molgenis.vkgl.clinvar.model.VariantGeneId;
import org.molgenis.vkgl.clinvar.model.VariantId;

public class LabSubmission {

  private final ClinVarMapping clinVarMapping;
  private final Lab lab;
  private Map<VariantId, SubmissionLine> consensusLines = new HashMap<>();
  private Map<VariantId, Set<SubmissionLine>> duplicateLines = new HashMap<>();
  private Set<SubmissionLine> invalidLines = new HashSet<>();
  private Set<SubmissionLine> unchangedLines = new HashSet<>();
  private Set<SubmissionLine> updatedLines = new HashSet<>();
  private Set<String> accessions = new HashSet<>();

  public LabSubmission(Lab lab, ClinVarMapping mapping) {
    this.lab = requireNonNull(lab);
    this.clinVarMapping = requireNonNull(mapping);
  }

  public void addConsensusLine(ConsensusLine consensusLine) {
    VariantGeneId variantGeneId = new VariantGeneId(consensusLine);
    VariantId variantId = new VariantId(consensusLine);

    MappingLine mappingLine = null;
    if (clinVarMapping.containsKey(lab, variantGeneId)) {
      mappingLine = clinVarMapping.getMapping(lab, variantGeneId);
      accessions.add(mappingLine.getClinVarAccession());
    }
    SubmissionLine submissionLine =
        SubmissionLine.builder()
            .consensusLine(consensusLine)
            .lab(lab)
            .mappingLine(mappingLine)
            .build();
    if (consensusLines.containsKey(variantId)) {
      SubmissionLine existingSubmission = consensusLines.get(variantId);
      consensusLines.remove(variantId);
      addDuplicate(variantId, existingSubmission);
      addDuplicate(variantId, submissionLine);
    } else if (duplicateLines.containsKey(variantId)) {
      addDuplicate(variantId, submissionLine);
    } else {
      consensusLines.put(variantId, submissionLine);
    }
  }

  public void variantTriage(boolean isSubmitSingleLine) {
    consensusLines.values().stream().forEach(line -> processLine(line, isSubmitSingleLine));
  }

  private void processLine(SubmissionLine submissionLine, boolean isSubmitSingleLine) {
    MappingLine mappingLine = submissionLine.getMappingLine();
    if (!submissionLine.isChanged()) {
      unchangedLines.add(submissionLine);
    } else if (((submissionLine.isSingleLab() && !isSubmitSingleLine) || !submissionLine
        .isValidType() || submissionLine.isSv())) {
      processInvalidLine(submissionLine, isSubmitSingleLine, mappingLine);
    } else {
      if (mappingLine != null) {
        submissionLine.setComment(
            String.format(
                "Updated: was '%s' is now '%s'.",
                mappingLine.getClassification(),
                submissionLine.getConsensusLine().getClassification(lab)));
      }
      updatedLines.add(submissionLine);
    }
  }

  private void processInvalidLine(SubmissionLine submissionLine, boolean isSubmitSingleLine,
      MappingLine mappingLine) {
    if (submissionLine.isSv() && submissionLine.getMappingLine() != null) {
      throw new SvWithAccessionException();
    } else if (submissionLine.isSingleLab() && !isSubmitSingleLine && mappingLine != null) {
      submissionLine.setComment("Invalid: classified by a single lab.");
    } else if ((!submissionLine.isValidType()) && submissionLine.getMappingLine() != null) {
      submissionLine.setComment(
          String.format(
              "Invalid consensus type: %s.", submissionLine.getConsensusLine().getType()));
    }
    invalidLines.add(submissionLine);
  }

  private void addDuplicate(VariantId variantId, SubmissionLine submissionLine) {
    Set<SubmissionLine> duplicates = getDuplicateLines(variantId);
    duplicates.add(submissionLine);
    duplicateLines.put(variantId, duplicates);
  }

  private Set<SubmissionLine> getDuplicateLines(VariantId variantId) {
    Set<SubmissionLine> duplicateList;
    if (duplicateLines.containsKey(variantId)) {
      duplicateList = duplicateLines.get(variantId);
    } else {
      duplicateList = new HashSet<>();
    }
    return duplicateList;
  }

  public Set<String> getMissedAccessions() {
    return clinVarMapping.getAllMappingLines(lab).stream()
        .map(MappingLine::getClinVarAccession)
        .filter(accesion -> !accessions.contains(accesion))
        .collect(Collectors.toSet());
  }

  public Set<SubmissionLine> getUpdated() {
    return updatedLines;
  }

  public Set<SubmissionLine> getUnchanged() {
    return unchangedLines;
  }

  public Map<VariantId, Set<SubmissionLine>> getDuplicated() {
    return duplicateLines;
  }

  public Set<SubmissionLine> getInvalid() {
    return invalidLines;
  }

  public Map<VariantId, SubmissionLine> getConsensusLines() {
    return consensusLines;
  }

  // for tests
  protected void setConsensusLines(Map<VariantId, SubmissionLine> consensusLines) {
    this.consensusLines = consensusLines;
  }
}
