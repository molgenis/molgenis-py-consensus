package org.molgenis.vkgl.clinvar.model;

import java.util.Set;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import org.springframework.lang.Nullable;

@Data
@AllArgsConstructor
@Builder
public class SubmissionLine {

  public static final int MAX_NON_SV_SIZE = 15;
  ConsensusLine consensusLine;
  Lab lab;
  @Nullable
  MappingLine mappingLine;

  public boolean isChanged() {
    return mappingLine == null || !consensusLine.getClassification(lab)
        .equals(mappingLine.getClassification());
  }

  public boolean isSingleLab() {
    return consensusLine.getNrLabs() == 1;
  }

  public boolean isValidType() {
    Set<Type> validTypes = Set.of(Type.agreement, Type.total_agreement);
    return validTypes.contains(consensusLine.getType());
  }

  public boolean isSv() {
    if (consensusLine.getStop() == null) {
      return false;
    } else if (consensusLine.getStart() >= consensusLine.getStop()) {
      return (consensusLine.getStart() - consensusLine.getStop()) > MAX_NON_SV_SIZE;
    } else {
      return (consensusLine.getStop() - consensusLine.getStart()) > MAX_NON_SV_SIZE;
    }
  }

  public String getClinVarAccession() {
    return mappingLine != null ? mappingLine.getClinVarAccession() : null;
  }

  public void setComment(String comment) {
    if (mappingLine != null) {
      mappingLine.setComment(comment);
    } else {
      throw new MissingMappingLineException();
    }
  }
}
