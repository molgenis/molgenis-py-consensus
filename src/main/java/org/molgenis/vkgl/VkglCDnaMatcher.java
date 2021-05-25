package org.molgenis.vkgl;

import java.io.BufferedReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.molgenis.vkgl.model.ScvMappingResult;
import org.molgenis.vkgl.model.SuccessScvMapping;
import org.molgenis.vkgl.utils.IdUtils;

public class VkglCDnaMatcher {

  private static Map<String, String> vkglLines = new HashMap<>();

  private VkglCDnaMatcher(){}

  public static ScvMappingResult match(Path clinVarMappingPath, String vkglBasePath) {

    ScvMappingResult result = new ScvMappingResult();

    List<Path> vkglPaths = new ArrayList<>();
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_erasmus.tsv"));
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_radboud_mumc.tsv"));
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_umcg.tsv"));
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_umcu.tsv"));
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_nki.tsv"));
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_lumc.tsv"));
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_vumc.tsv"));
    vkglPaths.add(Paths.get(vkglBasePath, "vkgl_amc.tsv"));

    try (BufferedReader clinVarReader = Files.newBufferedReader(clinVarMappingPath); ) {
      for (Path vkglPath : vkglPaths) {
        try (BufferedReader vkglReader = Files.newBufferedReader(vkglPath)) {
          vkglReader
              .lines()
              .skip(1)
              .forEach(
                  line -> vkglLines.put(mapVgkl(line), line));
        }
      }
      clinVarReader
          .lines()
          .skip(1)
          .forEach(
              line -> check(line, result));
    } catch (Exception e) {
      e.printStackTrace();
    }

    return result;
  }

  private static void check(String line, ScvMappingResult result) {
    String clinVarCDna = mapClinVar(line);
    String clinVarID = line.split("\t")[1];
    String clinVarLab = line.split("\t")[4];
    if (vkglLines.containsKey(clinVarCDna)) {
      SuccessScvMapping success =
          new SuccessScvMapping(
              clinVarID, IdUtils.createId(vkglLines.get(clinVarCDna)), clinVarLab, clinVarCDna);
      result.addSuccess(success);
    } else {
      result.addDelete(clinVarID, clinVarLab);
    }
  }

  private static String mapClinVar(String line) {
    String[] split = line.split("\t");
    String transcript = split[0].split(":")[0].split("\\.")[0];
    String cDNA = split[0].split(":")[1];
    return String.format("%s:%s", transcript, cDNA);
  }

  private static String mapVgkl(String line) {
    String[] split = line.split("\t");
    String transcript = split[9].split("\\.")[0];
    return String.format("%s:%s", transcript, split[6]);
  }
}
