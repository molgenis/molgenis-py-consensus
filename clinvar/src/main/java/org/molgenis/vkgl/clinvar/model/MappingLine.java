package org.molgenis.vkgl.clinvar.model;

import com.opencsv.bean.CsvBindByName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class MappingLine implements VariantLine {

  @CsvBindByName(column = "chromosome", required = true)
  String chromosome;

  @CsvBindByName(column = "start", required = true)
  Integer start;

  @CsvBindByName(column = "ref", required = true)
  String ref;

  @CsvBindByName(column = "alt", required = true)
  String alt;

  @CsvBindByName(column = "gene", required = true)
  String gene;

  @CsvBindByName(column = "classification", required = true)
  Classification classification;

  @CsvBindByName(column = "lab", required = true)
  String lab;

  @CsvBindByName(column = "clinvar_accession", required = true)
  String clinVarAccession;

  @CsvBindByName(column = "stop", required = true)
  Integer stop;

  @CsvBindByName(column = "comment")
  String comment;
}
