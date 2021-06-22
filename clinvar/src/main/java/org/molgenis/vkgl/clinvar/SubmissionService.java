package org.molgenis.vkgl.clinvar;

import static java.util.Objects.requireNonNull;

import org.molgenis.vkgl.clinvar.model.ConsensusLine;
import org.molgenis.vkgl.clinvar.model.Lab;
import org.molgenis.vkgl.clinvar.model.MappingLine;
import org.molgenis.vkgl.clinvar.model.Settings;
import org.springframework.stereotype.Component;

@Component
public class SubmissionService {

  private SubmissionDecorator submissionDecorator;
  private ClinVarMapping clinVarMapping;

  public SubmissionService(SubmissionDecorator submissionDecorator,
      ClinVarMapping clinVarMapping) {
    this.submissionDecorator = requireNonNull(submissionDecorator);
    this.clinVarMapping = requireNonNull(clinVarMapping);
  }

  public void createClinVarSubmission(Settings settings) {
    ClinVarWriter writer = new ClinVarWriter(settings);

    CsvReader<ConsensusLine> consensusReader = new CsvReader<>();
    CsvReader<MappingLine> mappingReader = new CsvReader<>();
    mappingReader.read(settings.getMapping(), MappingLine.class).forEach(this::processMapping);
    consensusReader.read(settings.getInput(), ConsensusLine.class).forEach(this::processConsensus);
    submissionDecorator.variantTraige(settings.isIncludeSingleLab());

    writer.write(submissionDecorator);
  }

  private void processMapping(MappingLine line) {
    clinVarMapping.addMapping(line);
  }

  private void processConsensus(ConsensusLine line) {
    for (Lab lab : Lab.values()) {
      if (line.getClassification(lab) != null) {
        submissionDecorator.addConsensusLine(line, lab);
      }
    }
  }
}
