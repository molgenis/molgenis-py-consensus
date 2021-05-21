package org.molgenis.vkgl.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class SuccessScvMapping {
  private String scv;
  private String variantIdentifier;
  private String clinVarLab;
  private String clinVarCdna;
}
