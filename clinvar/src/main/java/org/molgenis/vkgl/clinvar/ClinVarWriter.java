package org.molgenis.vkgl.clinvar;

import static java.util.Objects.requireNonNull;

import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.Settings;

public class ClinVarWriter {

  private final VariantWriter variantWriter;
  private final DeleteWriter deleteWriter;
  private final LogWriter logWriter;
  private final Settings settings;

  public ClinVarWriter(Settings settings) {
    this.settings = requireNonNull(settings);
    this.variantWriter = new VariantWriter(settings);
    this.deleteWriter = new DeleteWriter(settings);
    this.logWriter = new LogWriter(settings);
  }

  public void write(SubmissionDecorator submissionDecorator) {
    for (Lab lab : Lab.values()) {
      variantWriter.write(submissionDecorator.getUpdated(lab), lab);
      deleteWriter
          .write(submissionDecorator.getAccessionsToDelete(lab, settings.isDeleteDuplicates()),
              lab);
    }
    logWriter.write(submissionDecorator);
  }
}
