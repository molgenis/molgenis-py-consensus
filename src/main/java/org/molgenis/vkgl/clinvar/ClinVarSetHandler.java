package org.molgenis.vkgl.clinvar;

import java.util.ArrayList;
import java.util.List;
import org.molgenis.vkgl.model.Result;
import org.xml.sax.Attributes;
import org.xml.sax.helpers.DefaultHandler;

public class ClinVarSetHandler extends DefaultHandler {

  public static final String VKGL_DATA_SHARE_CONSENSUS = "VKGL Data-share Consensus";

  public static final String CLIN_VAR_ASSERTION = "ClinVarAssertion";
  public static final String STUDY_NAME = "StudyName";
  public static final String ATTRIBUTE = "Attribute";
  public static final String ELEMENT_VALUE = "ElementValue";
  public static final String DESCRIPTION = "Description";
  public static final String CLINICAL_SIGNIFICANCE = "ClinicalSignificance";
  public static final String CLIN_VAR_ACCESSION = "ClinVarAccession";
  public static final String SCV = "SCV";
  public static final String CLIN_VAR_SUBMISSION_ID = "ClinVarSubmissionID";
  public static final String RELEASE_SET = "ReleaseSet";

  private Result result;
  private ArrayList<Result> results;
  private boolean isVkgl = false;
  private boolean isCDna = false;
  private boolean inClinSig = false;
  private boolean inAssertion = false;
  private StringBuilder sb = new StringBuilder();
  private boolean startReading = false;

  public ClinVarSetHandler() {
    super();
  }

  @Override
  public void startElement(String uri, String localName, String qName,
      Attributes attributes) {

    if (qName.equals(CLIN_VAR_ASSERTION)) {
      result = new Result();
      inAssertion = true;
      isVkgl = false;
      isCDna = false;
    } else if (qName.equals(RELEASE_SET)) {
      results = new ArrayList<>();
    } else if (inAssertion) {
      if (qName.equals(ATTRIBUTE)) {
        if ("HGVS".equals(attributes.getValue("Type"))) {
          startReading = true;
          isCDna = true;
        } else {
          isCDna = false;
        }
      } else if (qName.equals(CLIN_VAR_SUBMISSION_ID)) {
        result.setLab(attributes.getValue("submitter"));
      } else if (qName.equals(CLIN_VAR_ACCESSION) && (SCV.equals(attributes.getValue("Type")))) {
        result.setSubmissionId(attributes.getValue("Acc"));
      } else if (qName.equals(CLINICAL_SIGNIFICANCE)) {
        inClinSig = true;
      } else if (qName.equals(STUDY_NAME) || qName.equals(ELEMENT_VALUE) || (
          qName.equals(DESCRIPTION) && inClinSig)) {
        startReading = true;
      }
    }
  }

  @Override
  public void endElement(String uri, String localName, String qName) {
    if (inAssertion) {
      if (qName.equals(CLIN_VAR_ASSERTION)) {
        if (results == null) {
          results = new ArrayList<>();
        }
        if (isVkgl) {
          results.add(result);
        }
        inAssertion = false;
      }
      else if (qName.equals(STUDY_NAME)) {
        String study = readStringBuilder();
        if (study.equals(VKGL_DATA_SHARE_CONSENSUS)) {
          isVkgl = true;
        }
        startReading = false;
      }
      else if (qName.equals(ATTRIBUTE)) {
        if (isCDna) {
          result.setCDNA(readStringBuilder());
        }
        isCDna = false;
        startReading = false;
      }
      else if (qName.equals(ELEMENT_VALUE)) {
        result.setGene(readStringBuilder());
        startReading = false;
      }
      else if (qName.equals(DESCRIPTION) && inClinSig) {
        result.setClassification(readStringBuilder());
        startReading = false;
      }
      else if (qName.equals(CLINICAL_SIGNIFICANCE)) {
        inClinSig = false;
      }
    }
  }

  private String readStringBuilder() {
    String value = sb.toString();
    sb = new StringBuilder();
    return value;
  }

  @Override
  public void characters(char[] ch, int start, int length) {
    if (startReading) {
      sb.append(new String(ch, start, length));
    }
  }

  public List<Result> getResults() {
    return results;
  }


}