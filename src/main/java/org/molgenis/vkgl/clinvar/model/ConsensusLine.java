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
public class ConsensusLine implements VariantLine {

  @CsvBindByName(column = "chromosome", required = true)
  String chromosome;

  @CsvBindByName(column = "start", required = true)
  Integer start;

  @CsvBindByName(column = "stop", required = true)
  Integer stop;

  @CsvBindByName(column = "ref", required = true)
  String ref;

  @CsvBindByName(column = "alt", required = true)
  String alt;

  @CsvBindByName(column = "gene", required = true)
  String gene;

  @CsvBindByName(column = "nr_labs", required = true)
  Integer nrLabs;

  @CsvBindByName(column = "amc")
  Classification amc;

  @CsvBindByName(column = "erasmus_mc")
  Classification erasmusMc;

  @CsvBindByName(column = "lumc")
  Classification lumc;

  @CsvBindByName(column = "nki")
  Classification nki;

  @CsvBindByName(column = "radboud_mumc")
  Classification radboudMumc;

  @CsvBindByName(column = "umc_utrecht")
  Classification umcUtrecht;

  @CsvBindByName(column = "umcg")
  Classification umcg;

  @CsvBindByName(column = "vumc")
  Classification vumc;

  @CsvBindByName(column = "consensus")
  Classification consensus;

  @CsvBindByName(column = "type", required = true)
  Type type;

  public Classification getClassification(Lab lab) {
    switch (lab) {
      case amc:
        return amc;
      case umcg:
        return umcg;
      case umc_utrecht:
        return umcUtrecht;
      case vumc:
        return vumc;
      case radboud_mumc:
        return radboudMumc;
      case lumc:
        return lumc;
      case erasmus_mc:
        return erasmusMc;
      case nki:
        return nki;
      default:
        throw new IllegalArgumentException(lab.name());
    }
  }
}
