package org.molgenis.vkgl.model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

import lombok.Data;
import org.molgenis.vkgl.clinvar.model.DeletesLine;

@Data
public class ScvMappingResult {
  private List<SuccessScvMapping> successScvMappings;
  private Map<String, List<DeletesLine>> failedScvMappings = new HashMap<>();

  public ScvMappingResult() {
      successScvMappings = new ArrayList<>();
    for (String lab : LabConstants.getAllLabs()) {
      failedScvMappings.put(lab, new ArrayList<>());
    }
  }

  public void addSuccess(SuccessScvMapping successScvMapping) {
      successScvMappings.add(successScvMapping);
  }

  public List<DeletesLine> getDeletes(String lab) {
    List<DeletesLine> deletesLines = failedScvMappings.get(lab);
    if (deletesLines != null) {
      return deletesLines;
    } else {
      throw new IllegalArgumentException("No such lab: " + lab);
    }
  }

  public void addDelete(String clinVarId, String lab) {
    List<DeletesLine> deletesLines = failedScvMappings.get(lab);
    if (deletesLines != null) {
      deletesLines.add(new DeletesLine(clinVarId, lab));
      failedScvMappings.put(lab, deletesLines);
    } else {
      throw new IllegalArgumentException("No such lab: " + lab);
    }
  }
  public List<SuccessScvMapping> getVariants(){
    return successScvMappings;
  }

  public List<DeletesLine> getDeletesAllLabs(){
    List<DeletesLine> result = new ArrayList<>();
    for (String lab : LabConstants.getAllLabs()) {
      result.addAll(failedScvMappings.get(lab));
    }
    Set<String> set = result.stream().map(delete -> delete.getSvc()).collect(Collectors.toSet());
    return result;
  }
}
