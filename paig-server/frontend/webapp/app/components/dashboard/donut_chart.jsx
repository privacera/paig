import React, { Component, createRef } from "react";
import Highcharts from "highcharts";
import { isEmpty } from "lodash";

import { Box } from "@material-ui/core";

import ReactHighcharts from "common-ui/lib/highcharts/ReactHighcharts";
import { observer } from "mobx-react";

Highcharts.setOptions({
  colors: [
    "#2CA02C",
    "#ff9335",
    "#41546F",
    "#D62728",
    "#F59E0B",
    "#FACC15",
    "#e4d354",
    "#8085e8",
    "#ffbac7",
    "#91e8e1"
  ]
});

@observer
class DonutChart extends Component {
  constructor(props) {
    super(props)
    this.chart = createRef();
  }
  render() {
    const { data, boxProps, chartOptions = {} } = this.props;
    const { title = "", totalCount, chartData } = data;
    const { subtitle = {}, ...restChartOptions } = chartOptions;
    let options = {
      chart: {
        type: "pie",
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        height: "200px",
        marginLeft: 22
      },

      title: {
        text: null
      },
      tooltip: {
        pointFormat:
          "{series.name}: <b>{point.percentage:.1f}%</b><br/> Count: <b>{point.y}</b>"
      },
      legend: {
        layout: "vertical",
        align: "right",
        verticalAlign: "middle",
        itemMarginTop: 3,
        itemMarginBottom: 3,
        symbolPadding: 0,
        itemStyle: {
          padding: 0,
          color: "#8693A6",
          cursor: "pointer",
          fontSize: "10px",
          fontWeight: "400",
          width: "45%", // Set the maximum width for legend items
          whiteSpace: "nowrap", // Prevent text from wrapping
          overflow: "hidden", // Hide overflowing text
          textOverflow: "ellipsis" // Show ellipsis (...) when text is truncated
        }
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
          },
          showInLegend: true
        }
      },
      series: [
        {
          name: title || "Percent",
          colorByPoint: true,
          data: isEmpty(chartData) ? [] : chartData,
          size: "120%"
        }
      ],
      credits: {
        enabled: false
      }
    };

    if (totalCount > 0) {
      options.series[0].innerSize = '60%';
      options.subtitle = {
        useHTML: false,
        text: `<span style="font-size:14px;">Total Count</span> </br> <strong>${totalCount}<strong>`,
        floating: true,
        verticalAlign: "middle",
        style: {
          fontSize: "18px"
        },
        y: 15,
        x: -35,
        ...(subtitle ? { ...subtitle } : {})
      }
    } else {
      options.series[0].data = [];
    }
    Object.assign(options, { ...restChartOptions });
    return (
      <Box {...boxProps}>
        <ReactHighcharts ref={this.chart} options={options} />
      </Box>
    );
  }
}

export default DonutChart;
