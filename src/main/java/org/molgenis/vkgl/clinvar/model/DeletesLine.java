package org.molgenis.vkgl.clinvar.model;

import lombok.Data;

@Data
public class DeletesLine {
  private String svc;
  private String lab;

  public DeletesLine(String svc, String lab) {
    this.svc = svc;
    this.lab = lab;
  }
}
