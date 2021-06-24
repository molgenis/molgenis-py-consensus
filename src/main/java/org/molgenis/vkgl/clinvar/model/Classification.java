package org.molgenis.vkgl.clinvar.model;

@SuppressWarnings("java:S115")
public enum Classification {
  b("Benign"), lb("Likely benign"), vus("Uncertain significance"), lp("Likely pathogenic"), p(
      "Pathogenic");

  private final String longName;

  Classification(String longName) {
    this.longName = longName;
  }

  public String getLongName() {
    return longName;
  }
}
