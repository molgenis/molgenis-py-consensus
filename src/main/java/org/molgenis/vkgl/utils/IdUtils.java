package org.molgenis.vkgl.utils;

public class IdUtils {

  public static String createId(String vkglLine) {
    String[] split = vkglLine.split("\t");
    String chrom = split[0];
    String start = split[1];
    String stop = split[2];
    String ref = split[3];
    String alt = split[4];
    String gene = split[5];
    return String.format("%s_%s_%s_%s_%s_%s",chrom,start,stop,ref,alt,gene);
  }

  public static String createIdConsensus(String consensusLine) {
    String[] split = consensusLine.split("\t");
    String chrom = split[1];
    String start = split[2];
    String stop = split[3];
    String ref = split[4];
    String alt = split[5];
    String gene = split[6];
    return String.format("%s_%s_%s_%s_%s_%s",chrom,start,stop,ref,alt,gene);
  }
}
