package org.molgenis.vkgl.clinvar;

import static java.util.Objects.requireNonNull;

import java.util.Collection;
import java.util.EnumMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import org.molgenis.vkgl.clinvar.model.ConsensusLine;
import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.MappingLine;
import org.molgenis.vkgl.clinvar.model.SubmissionLine;
import org.molgenis.vkgl.clinvar.model.VariantId;
import org.springframework.stereotype.Component;

@Component
public class SubmissionDecorator {

  private final ClinVarMapping clinVarMapping;

  private Map<Lab, LabSubmission> submissionLabContextMap = new EnumMap<>(Lab.class);

  public SubmissionDecorator(ClinVarMapping clinVarMapping) {
    this.clinVarMapping = requireNonNull(clinVarMapping);
  }

  private LabSubmission getSubmissionContext(Lab lab) {
    if (!submissionLabContextMap.containsKey(lab)) {
      LabSubmission labSubmission = new LabSubmission(lab, clinVarMapping);
      submissionLabContextMap.put(lab, labSubmission);
    }
    return submissionLabContextMap.get(lab);
  }

  public void addConsensusLine(ConsensusLine line, Lab lab) {
    LabSubmission labSubmission = getSubmissionContext(lab);
    labSubmission.addConsensusLine(line);
  }

  public Set<SubmissionLine> getUpdated(Lab lab) {
    LabSubmission labSubmission = getSubmissionContext(lab);
    return labSubmission.getUpdated();
  }

  public Set<SubmissionLine> getUnchanged(Lab lab) {
    LabSubmission labSubmission = getSubmissionContext(lab);
    return labSubmission.getUnchanged();
  }

  public Map<VariantId, Set<SubmissionLine>> getDuplicated(Lab lab) {
    LabSubmission labSubmission = getSubmissionContext(lab);
    return labSubmission.getDuplicated();
  }

  public Set<SubmissionLine> getInvalid(Lab lab) {
    LabSubmission labSubmission = getSubmissionContext(lab);
    return labSubmission.getInvalid();
  }

  private Set<String> getMissedAccessions(Lab lab) {
    LabSubmission labSubmission = getSubmissionContext(lab);
    return labSubmission.getMissedAccessions();
  }

  public Set<MappingLine> getDuplicatedMappings() {
    Set<MappingLine> mappings = new HashSet<>();
    for (Lab lab : Lab.values()) {
      getDuplicated(lab).values().stream()
          .forEach(
              duplicates ->
                  duplicates.stream()
                      .filter(line -> (line.getMappingLine() != null))
                      .forEach(line -> mappings.add(line.getMappingLine())));
    }
    return mappings;
  }

  public Set<MappingLine> getInvalidMappings() {
    Set<MappingLine> mappings = new HashSet<>();
    for (Lab lab : Lab.values()) {
      getInvalid(lab).stream()
          .filter(line -> (line.getMappingLine() != null))
          .forEach(line -> mappings.add(line.getMappingLine()));
    }
    return mappings;
  }

  public Set<MappingLine> getUpdatedMappings() {
    Set<MappingLine> mappings = new HashSet<>();
    for (Lab lab : Lab.values()) {
      getUpdated(lab).stream()
          .filter(line -> (line.getMappingLine() != null))
          .forEach(line -> mappings.add(line.getMappingLine()));
    }
    return mappings;
  }

  public Set<MappingLine> getUnchangedMappings() {
    Set<MappingLine> mappings = new HashSet<>();
    for (Lab lab : Lab.values()) {
      getUnchanged(lab).stream()
          .filter(line -> (line.getMappingLine() != null))
          .forEach(line -> mappings.add(line.getMappingLine()));
    }
    return mappings;
  }

  public Collection<String> getAccessionsToDelete(Lab lab, boolean isDeleteDuplicates) {
    Set<String> accessions = new HashSet<>();
    if (isDeleteDuplicates) {
      getDuplicated(lab).values().stream()
          .forEach(
              duplicates ->
                  duplicates.stream()
                      .filter(line -> (line.getMappingLine() != null))
                      .forEach(line -> accessions.add(line.getClinVarAccession())));
    }
    getInvalid(lab).stream()
        .filter(line -> (line.getMappingLine() != null))
        .forEach(line -> accessions.add(line.getClinVarAccession()));
    getMissedAccessions(lab).forEach(accessions::add);
    return accessions;
  }

  public void variantTraige(boolean includeSingleLab) {
    for (Lab lab : Lab.values()) {
      LabSubmission labSubmission = getSubmissionContext(lab);
      labSubmission.variantTriage(includeSingleLab);
    }
  }

  //for testing
  public void setSubmissionLabContextMap(
      Map<Lab, LabSubmission> submissionLabContextMap) {
    this.submissionLabContextMap = submissionLabContextMap;
  }
}
