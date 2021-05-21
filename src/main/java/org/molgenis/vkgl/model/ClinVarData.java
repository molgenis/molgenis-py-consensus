package org.molgenis.vkgl.model;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import lombok.Data;
import org.molgenis.vkgl.clinvar.model.DeletesLine;
import org.molgenis.vkgl.clinvar.model.VariantLine;

@Data
public class ClinVarData {

  Map<String, List<VariantLine>> variants = new HashMap<>();
  Map<String, List<DeletesLine>> deletes = new HashMap<>();

  public ClinVarData() {
    for (String lab : LabConstants.getAllLabs()) {
      variants.put(lab, new ArrayList<>());
      deletes.put(lab, new ArrayList<>());
    }
  }

  public void addSuccess(String lab, VariantLine variantLine) {
    List<VariantLine> variantLines = variants.get(lab);
    if (lab != null) {
      variantLines.add(variantLine);
      variants.put(lab, variantLines);
    } else {
      throw new IllegalArgumentException("No such lab: " + lab);
    }
  }

  public List<VariantLine> getVariants(String lab) {
    List<VariantLine> variantLines = variants.get(lab);
    if (variantLines != null) {
      return variantLines;
    } else {
      throw new IllegalArgumentException("No such lab: " + lab);
    }
  }

  public List<DeletesLine> getDeletes(String lab) {
    List<DeletesLine> deletesLines = deletes.get(lab);
    if (deletesLines != null) {
      return deletesLines;
    } else {
      throw new IllegalArgumentException("No such lab: " + lab);
    }
  }

  public void addDelete(String clinVarId, String lab) {
    List<DeletesLine> deletesLines = deletes.get(lab);
    if (deletesLines != null) {
      deletesLines.add(new DeletesLine(clinVarId, lab));
      deletes.put(lab, deletesLines);
    } else {
      throw new IllegalArgumentException("No such lab: " + lab);
    }
  }
}
