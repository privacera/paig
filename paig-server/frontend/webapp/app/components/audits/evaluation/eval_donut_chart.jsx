import React, { Component, createRef } from "react";

import { Box } from "@material-ui/core";

import {SEVERITY_MAP} from 'utils/globals';
import ReactHighcharts from "common-ui/lib/highcharts/ReactHighcharts";

class EvalDonutChart extends Component {
  constructor(props) {
    super(props);
    this.chart = createRef();
  }

  getSeverityColor(severity) {
    if (!severity) return `#${SEVERITY_MAP.LOW.DONUTCOLOR}`;
    const upperSeverity = severity.toUpperCase();
    const severityObj = SEVERITY_MAP[upperSeverity];
    return severityObj ? `#${severityObj.DONUTCOLOR}` : `#${SEVERITY_MAP.LOW.DONUTCOLOR}`;
  }


  render() {
    const { appName, data, boxProps, chartOptions = {} } = this.props;
    const { passes = 0, total = 0, severity } = data;
    const severityColor = this.getSeverityColor(severity);
    const chartData = total > 0
      ? [
          { name: "Passes", y: passes, color: severityColor },
          { name: "Failures", y: total - passes, color: "#B0B0B0" }
        ]
      : [];
    // Highcharts options
    let options = {
      chart: {
        type: "pie",
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        height: "150px"
      },
      title: {
        text: null
      },
      tooltip: {
        pointFormat:
          "{series.name}: <b>{point.percentage:.1f}%</b><br/> Count: <b>{point.y}</b>"
      },
      exporting: {
        enabled: false
      },
      plotOptions: {
        pie: {
          allowPointSelect: true,
          cursor: "pointer",
          dataLabels: {
            enabled: false,
            distance: 30
          }
        }
      },
      series: [
        {
          name: appName || "Results",
          colorByPoint: true,
          data: chartData,
          size: "120%"
        }
      ],
      credits: {
        enabled: false
      }
    };

    // Add inner donut text if passes and total are available
    if (total > 0) {
      options.series[0].innerSize = "60%";
      const percentage = Math.round((passes / total) * 100);
      options.subtitle = {
        useHTML: false,
        text: `<strong>${percentage}%</strong>`,
        floating: true,
        verticalAlign: "middle",
        style: {
          fontSize: "18px"
        },
        y: 15
      };
    } else {
      options.series[0].data = [];
    }

    // Merge additional chart options
    Object.assign(options, chartOptions);

    return (
      <Box {...boxProps}>
        <ReactHighcharts ref={this.chart} options={options} />
      </Box>
    );
  }
}

export default EvalDonutChart;