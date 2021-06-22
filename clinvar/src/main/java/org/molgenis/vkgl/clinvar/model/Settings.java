package org.molgenis.vkgl.clinvar.model;

import java.nio.file.Path;
import lombok.Builder;
import lombok.Value;

@Value
@Builder
public class Settings {

  Path input;
  Path mapping;
  Path outputDir;
  boolean overwrite;
  boolean debug;
  boolean includeSingleLab;
  boolean deleteDuplicates;
  String release;
}
