package org.molgenis.vkgl.clinvar.model;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class DeletesLine {
  private String svc;
  private String lab;
  private String reason;
}
