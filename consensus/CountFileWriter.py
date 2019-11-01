class CountFileWriter:
    def __init__(self, count_obj, single_count_obj, title):
        counts = self.generate_counts(count_obj)
        single_counts = self.generate_counts(single_count_obj)
        consensus_count_obj = count_obj.copy().drop(['Classified by one lab'])
        consensus_counts = self.generate_counts(consensus_count_obj)
        generated_text = self.generate_text(count_obj, single_count_obj)
        self.page = self.generate_page(counts, single_counts, consensus_counts, title, generated_text)

    @staticmethod
    def generate_counts(count_obj):
        count_template = "[['Classification', 'Count'],"
        for classification, count in count_obj.iteritems():
            count_template += "['{}',{}],".format(classification, count)
        count_template = count_template[0:len(count_template) - 1] + ']'
        return count_template

    @staticmethod
    def generate_chart():
        draw_chart = ("{\nvar options = {'title':title, 'width':600, 'height':600, 'pieSliceText': 'value', "
                      "'backgroundColor':'transparent', 'sliceVisibilityThreshold':0}\n"
                      "\t// Display the chart inside the <div> element with id=\"*given id*\"\n"
                      "var chart = new google.visualization.PieChart(document.getElementById(id));\n"
                      "chart.draw(data, options);\n}")
        return draw_chart

    @staticmethod
    def generate_text(count_obj, single_counts):
        counts_html = '<ul>\n'
        one_lab = 'Classified by one lab'
        for classification, count in count_obj.iteritems():
            if classification != one_lab:
                counts_html += '\t<li>{}: {}</li>\n'.format(classification, count)

        counts_html += '\t<li>{} ({}):\n\t\t<ul>\n'.format(one_lab, str(count_obj[one_lab]))

        for classification, count in single_counts.iteritems():
            counts_html += '\t\t\t<li>{}: {}</li>\n'.format(classification, count)
        counts_html += '\t\t</ul>\n\t</li>\n</ul>'
        return counts_html

    @staticmethod
    def generate_data(counts, single_counts, consensus_counts):
        return ("var counts_data = google.visualization.arrayToDataTable({});\n"
                "drawChart('counts-chart', 'All data', counts_data)\n"
                "var consensus_counts_data = google.visualization.arrayToDataTable({});\n"
                "drawChart('consensus-counts-chart', 'Classified by > 1 lab', consensus_counts_data)\n"
                "var single_counts_data = google.visualization.arrayToDataTable({});\n"
                "drawChart('single-counts-chart', 'Classified by one lab', single_counts_data)"
                ).format(counts, consensus_counts, single_counts)

    def generate_page(self, counts, single_counts, consensus_counts, title, generated_text):
        packages = "{'packages':['corechart']}"
        "// Optional; add a title and set the width and height of the chart\n"
        return ("<h1>{}</h1>\n"
                "<div class='row'>\n"
                "<div class='col-md-12'>\n"
                "{}</div>\n"
                "</div>\n"
                "<div class='row'>\n"
                "<div class='col-md-4'>\n"
                "<div id=\"counts-chart\"></div>\n"
                "</div>\n"
                "<div class='col-md-4'>\n"
                "<div id=\"consensus-counts-chart\"></div>\n"
                "</div>\n"
                "<div class='col-md-4'>\n"
                "<div id=\"single-counts-chart\"></div>\n"
                "</div>\n"
                "</div>\n"
                "<script type=\"text/javascript\" src=\"https://www.gstatic.com/charts/loader.js\"></script>\n"
                "<script type=\"text/javascript\">\n"
                "// Load google charts\n"
                "google.charts.load('current', {});\n"
                "google.setOnLoadCallback(\n"
                "function(){}"
                ");"
                "\t// Draw the chart and set the chart values\n"
                "function drawChart(id, title, data) {}\n"
                "</script>\n").format(title, generated_text, packages,
                                      "{" + self.generate_data(counts, single_counts, consensus_counts) + "}",
                                      self.generate_chart())
