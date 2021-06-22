package org.molgenis.vkgl.clinvar.model;

import lombok.AllArgsConstructor;
import lombok.Value;

@Value
@AllArgsConstructor
public class VariantGeneId {

  VariantId variantId;
  String gene;

  public VariantGeneId(ConsensusLine consensusLine) {
    this.variantId = new VariantId(consensusLine);
    this.gene = consensusLine.getGene();
  }

  public VariantGeneId(MappingLine mappingLine) {
    this.variantId = new VariantId(mappingLine);
    this.gene = mappingLine.getGene();
  }

  public VariantGeneId(SubmissionLine submissionLine) {
    this.variantId = new VariantId(submissionLine.getConsensusLine());
    this.gene = submissionLine.getConsensusLine().getGene();
  }
}
