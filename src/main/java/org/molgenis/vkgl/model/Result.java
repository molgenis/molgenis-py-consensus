package org.molgenis.vkgl.model;

import lombok.Data;

@Data
public class Result {
  private String submissionId;
  private String lab;
  private String classification;
  private String cDNA;
  private String gene;
}
