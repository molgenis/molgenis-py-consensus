package org.molgenis.vkgl.clinvar;

import java.util.Collection;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.Map;
import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.MappingLine;
import org.molgenis.vkgl.clinvar.model.VariantGeneId;
import org.springframework.stereotype.Component;

@Component
public class ClinVarMapping {

  EnumMap<Lab, Map<VariantGeneId, MappingLine>> mapping = new EnumMap<>(Lab.class);

  private Map<VariantGeneId, MappingLine> getMapping(Lab lab) {
    if (!mapping.containsKey(lab)) {
      Map<VariantGeneId, MappingLine> labMapping = new HashMap<>();
      mapping.put(lab, labMapping);
    }
    return mapping.get(lab);
  }

  public void addMapping(MappingLine mappingLine) {
    Lab lab = Lab.valueOf(mappingLine.getLab());
    Map<VariantGeneId, MappingLine> labMapping = getMapping(lab);
    labMapping.put(new VariantGeneId(mappingLine), mappingLine);
    mapping.put(lab, labMapping);
  }

  public MappingLine getMapping(Lab lab, VariantGeneId variantGeneId) {
    Map<VariantGeneId, MappingLine> labMapping = getMapping(lab);
    return labMapping.get(variantGeneId);
  }

  public Collection<MappingLine> getAllMappingLines(Lab lab) {
    Map<VariantGeneId, MappingLine> labMapping = getMapping(lab);
    return labMapping.values();
  }

  public boolean containsKey(Lab lab, VariantGeneId variantGeneId) {
    Map<VariantGeneId, MappingLine> labMapping = getMapping(lab);
    return labMapping.containsKey(variantGeneId);
  }
}
