package org.molgenis.vkgl.clinvar.model;

import lombok.Value;

@Value
public class VariantGeneLabId {

  VariantGeneId variantGeneId;
  Lab lab;
}
