package org.molgenis.vkgl.model;

import java.nio.file.Path;
import java.util.List;
import lombok.AllArgsConstructor;
import lombok.Value;

@Value
@AllArgsConstructor
public class Settings {
  Path consensusPath;
  Path clinVarPath;
  String basePath;
  List<String> noSubmitClassifications;
  String releaseName;
  String outputDir;
}
