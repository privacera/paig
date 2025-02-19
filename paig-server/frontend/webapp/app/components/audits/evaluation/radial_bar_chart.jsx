import React from "react";
import Highcharts from "highcharts";
import ReactHighcharts from "common-ui/lib/highcharts/ReactHighcharts";

const RadialBarChart = ({ chartData, title }) => {
  const options = {
    chart: {
      type: "column",
      inverted: true,
      polar: true,
    },
    title: {
      text: title,
    },
    tooltip: {
      outside: true
    },
    pane: {
      size: "85%",
      innerSize: "20%",
      endAngle: 260,
    },
    xAxis: {
      categories: chartData.categories,
      tickInterval: 1,
      labels: {
        align: "right",
        allowOverlap: true,
        step: 1,
        y: 3,
        style: { fontSize: "13px" }
      },
      lineWidth: 0,
      gridLineWidth: 0,
    },
    yAxis: {
      tickInterval: 5,
      reversedStacks: false,
      endOnTick: true,
      showLastLabel: true,
      gridLineWidth: 0
    },
    plotOptions: {
      column: {
        stacking: "normal",
        borderWidth: 0,
        pointPadding: 0,
        groupPadding: 0.15
      },
    },
    series: chartData.series,
    exporting: {
      enabled: false
    },
    credits: {
      enabled: false
    }
  };

  return <ReactHighcharts highcharts={Highcharts} options={options} />;
};

export default RadialBarChart;
