package org.molgenis.vkgl.clinvar.model;

import lombok.Data;

@Data
public class VariantLine {
  private String scv;
  private String HGVS;
  private String lab;
  private String classification;
  private String gene;
}
