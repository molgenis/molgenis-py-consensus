package org.molgenis.vkgl.clinvar.model;

public interface VariantLine {

  String getChromosome();

  Integer getStart();

  Integer getStop();

  String getRef();

  String getAlt();
}
