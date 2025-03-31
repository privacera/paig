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
    const percentage = total > 0 ? Math.round((passes / total) * 100) : 0;
    // Highcharts options
    let options = {
      chart: {
        type: "pie",
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        height: "150px",
        width: 300,
        custom: {},
        events: {
          render() {
            const chart = this,
              series = chart.series[0];
            let customLabel = chart.options.chart.custom.label;

            if (!customLabel) {
              customLabel = chart.options.chart.custom.label = chart.renderer
                .label(
                  `<strong>${percentage}%</strong>`, // Dynamic percentage text
                  0,
                  0
                )
                .css({
                  color: "#000",
                  textAnchor: "middle",
                  fontWeight: "bold"
                })
                .add();
            }

            const x = series.center[0] + chart.plotLeft,
              y = series.center[1] + chart.plotTop - customLabel.attr("height") / 2;

            customLabel.attr({
              x,
              y
            });

            // Dynamically adjust font size based on chart diameter
            customLabel.css({
              fontSize: `${series.center[2] / 10}px`
            });
          }
        }
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
          allowPointSelect: false,
          cursor: "pointer",
          dataLabels: {
            enabled: false,
            distance: 30
          },
          states: {
            hover: {
              enabled: false
            }
          }
        }
      },
      series: [
        {
          name: appName || "Results",
          colorByPoint: true,
          data: chartData,
          size: "120%",
          innerSize: "60%",
          center: ["50%", "50%"]
        }
      ],
      credits: {
        enabled: false
      }
    };

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