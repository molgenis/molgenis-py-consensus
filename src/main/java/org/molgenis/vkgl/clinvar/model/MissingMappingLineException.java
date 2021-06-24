package org.molgenis.vkgl.clinvar.model;

public class MissingMappingLineException extends RuntimeException {

  private static final String MESSAGE =
      "Cannot set a comment for a submission without an existing ClinVarMapping.";

  public MissingMappingLineException() {
    super(MESSAGE);
  }
}