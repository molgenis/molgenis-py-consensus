package org.molgenis.vkgl.clinvar;

import static java.nio.charset.StandardCharsets.UTF_8;

import com.opencsv.bean.CsvToBean;
import com.opencsv.bean.CsvToBeanBuilder;
import com.opencsv.exceptions.CsvException;
import java.io.IOException;
import java.io.Reader;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CsvReader<T> {

  private static final Logger LOGGER = LoggerFactory.getLogger(CsvReader.class);

  static void handleCsvParseExceptions(List<CsvException> exceptions) {
    exceptions.forEach(
        csvException ->
            LOGGER.error(
                String.format("%s,%s", csvException.getLineNumber(), csvException.getMessage())));
  }

  public List<T> read(Path input, Class<T> targetClass) {
    List<T> lines;
    try (Reader reader = Files.newBufferedReader(input, UTF_8)) {

      CsvToBean<T> csvToBean =
          new CsvToBeanBuilder<T>(reader)
              .withSeparator('\t')
              .withType(targetClass)
              .withThrowExceptions(false)
              .build();
      lines = csvToBean.stream().collect(Collectors.toList());
      handleCsvParseExceptions(csvToBean.getCapturedExceptions());
    } catch (IOException e) {
      throw new UncheckedIOException(e);
    }
    return lines;
  }
}
