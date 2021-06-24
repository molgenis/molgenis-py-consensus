package org.molgenis.vkgl.clinvar;

public class SvWithAccessionException extends RuntimeException {

  private static final String MESSAGE =
      "Unsupported structural variants should not have an existing ClinVar Accession.";

  public SvWithAccessionException() {
    super(MESSAGE);
  }
}
