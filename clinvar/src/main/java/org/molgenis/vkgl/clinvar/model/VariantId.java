package org.molgenis.vkgl.clinvar.model;

import lombok.AllArgsConstructor;
import lombok.Value;

@Value
@AllArgsConstructor
public class VariantId {

  String chromosome;
  Integer start;
  Integer stop;
  String ref;
  String alt;

  public VariantId(VariantLine line) {
    this.chromosome = line.getChromosome();
    this.start = line.getStart();
    this.stop = line.getStop();
    this.ref = line.getRef();
    this.alt = line.getAlt();
  }
}
