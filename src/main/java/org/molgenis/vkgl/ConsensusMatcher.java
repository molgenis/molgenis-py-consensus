package org.molgenis.vkgl;

import static org.molgenis.vkgl.model.LabConstants.AMC;
import static org.molgenis.vkgl.model.LabConstants.ERASMUS;
import static org.molgenis.vkgl.model.LabConstants.LUMC;
import static org.molgenis.vkgl.model.LabConstants.NKI;
import static org.molgenis.vkgl.model.LabConstants.RADBOUD;
import static org.molgenis.vkgl.model.LabConstants.UMCG;
import static org.molgenis.vkgl.model.LabConstants.UMCU;
import static org.molgenis.vkgl.model.LabConstants.VU;

import java.io.BufferedReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import org.molgenis.vkgl.model.ClinVarData;
import org.molgenis.vkgl.clinvar.model.DeletesLine;
import org.molgenis.vkgl.clinvar.model.VariantLine;
import org.molgenis.vkgl.model.ScvMappingResult;
import org.molgenis.vkgl.model.SuccessScvMapping;
import org.molgenis.vkgl.utils.IdUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConsensusMatcher {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConsensusMatcher.class);

  public static final int CLASSIFICATION_IDX = 11;
  public static final int LUMC_IDX = 13;
  public static final int AMC_IDX = 15;
  public static final int NKI_IDX = 17;
  public static final int VU_IDX = 19;
  public static final int UMCG_IDX = 21;
  public static final int UMCU_IDX = 23;
  public static final int RADBOUD_IDX = 25;
  public static final int ERASMUS_IDX = 27;

  private static List<String> usedScvMappings = new ArrayList<>();
  private Path consensusPath;
  private Path parsedClinVarPath;
  private String vkglBasePath;
  private List<String> noSubmitClassifications;

  public ConsensusMatcher(Path consensusPath, Path parsedClinVarPath, String vkglBasePath,
      List<String> noSubmitClassifications) {
    this.consensusPath = consensusPath;
    this.parsedClinVarPath = parsedClinVarPath;
    this.vkglBasePath = vkglBasePath;
    this.noSubmitClassifications = noSubmitClassifications;
  }

  public ClinVarData match(){
    ClinVarData clinVarData = new ClinVarData();

    Map<String, Integer> labMapping = new HashMap<>();
      labMapping.put(UMCG, UMCG_IDX);
      labMapping.put(UMCU, UMCU_IDX);
      labMapping.put(LUMC, LUMC_IDX);
      labMapping.put(VU, VU_IDX);
      labMapping.put(AMC, AMC_IDX);
      labMapping.put(RADBOUD, RADBOUD_IDX);
      labMapping.put(NKI, NKI_IDX);
      labMapping.put(ERASMUS, ERASMUS_IDX);

    try (
        BufferedReader consensusReader = Files.newBufferedReader(consensusPath);
    ) {
      ScvMappingResult scvMappingResult = VkglCDnaMatcher.match(parsedClinVarPath, vkglBasePath);
      consensusReader
          .lines()
          .skip(1)
          .filter(line -> !line.isEmpty())
          .filter(
              line ->
                  noSubmitClassifications.isEmpty()
                      || !noSubmitClassifications.contains(line.split("\t")[CLASSIFICATION_IDX]))
          .forEach(
              line -> {
                String[] split = line.split("\t");
                String id = IdUtils.createIdConsensus(line);
                for (Entry<String, Integer> entry : labMapping.entrySet()) {
                  if (!split[entry.getValue()].isEmpty()) {
                    VariantLine result =
                        createResult(
                            scvMappingResult.getVariants(),
                            split,
                            id,
                            entry.getKey(),
                            entry.getValue());
                    if (result != null) {
                      clinVarData.addSuccess(entry.getKey(), result);
                    }
                  }
                }
              });
      int count = 0;
      for(DeletesLine deletesLine : scvMappingResult.getDeletesAllLabs()){
        clinVarData.addDelete(deletesLine.getSvc(), deletesLine.getLab(), "unmappable 1");
        count++;
      }
      for(SuccessScvMapping variant : scvMappingResult.getVariants()){
        if(variant.getScv() != null &&!usedScvMappings.contains(variant.getScv())){
          clinVarData.addDelete(variant.getScv(), variant.getClinVarLab(), "unmappable 2");
          count++;
        }
      }
      LOGGER.info("Number of unmatched clinVar SVCs: {}", count);
    } catch (Exception e) {
      e.printStackTrace();
    }
    return clinVarData;
  }

  private static VariantLine createResult(List<SuccessScvMapping> scvMappings, String[] split,
      String id, String lab, int labIndex) {
    String cDNA = split[7];
    String transcript = split[8];
    VariantLine result = null;
    if (!cDNA.isEmpty() && !cDNA.contains(",") && !transcript.contains(",")) {
      result = new VariantLine();
      result.setLab(lab);
      result.setHgvs(String.format("%s:%s", transcript, cDNA));
      result.setGene(split[6]);
      result.setClassification(split[labIndex]);
      for (SuccessScvMapping mapping : scvMappings) {
        if (mapping.getVariantIdentifier().equals(id) && mapping.getClinVarLab().equals(lab)) {
          result.setScv(mapping.getScv());
          usedScvMappings.add(mapping.getScv());
        }
      }
    }
    return result;
  }

}
