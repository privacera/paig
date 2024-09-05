import React from "react";
import Highcharts from "highcharts";

import { Box } from "@material-ui/core";

import ReactHighcharts from "common-ui/lib/highcharts/ReactHighcharts";

Highcharts.setOptions({
  colors: [
    "#2CA02C",
    "#ff9335",
    "#1F77B4",
    "#D62728",
    "#F59E0B",
    "#FACC15",
    "#e4d354",
    "#8085e8",
    "#ffbac7",
    "#91e8e1"
  ]
});

const DataAccessGraph = (props) => {
  const { data, boxProps } = props;
  const { chartData, categories } = data;

  const options = {
    chart: {
      type: "column"
    },
    title: {
      text: null
    },
    xAxis: {
      categories,
      crosshair: true
    },
    yAxis: {
      min: 0,
      title: {
        text: null
      }
    },
    tooltip: {
      headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
      pointFormat:
        '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        '<td style="padding:0"><b>{point.y}</b></td></tr>',
      footerFormat: "</table>",
      shared: true,
      useHTML: true
    },
    legend: {
      itemStyle: {
          cursor: "pointer",
          fontWeight: "400",
          color:"#8693A6"
        }
      },
    exporting: {
      enabled: false
    },
    plotOptions: {
      column: {
        pointPadding: 0.2,
        borderWidth: 0
      },
      series: {
        pointWidth: 10
      }
    },
    series: chartData,
    credits: {
      enabled: false
    }
  };

  return (
    <Box {...boxProps}>
      <ReactHighcharts options={options} />
    </Box>
  );
};

export default DataAccessGraph;
