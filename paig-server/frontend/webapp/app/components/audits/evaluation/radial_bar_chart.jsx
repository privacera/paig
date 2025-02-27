import React from "react";
import Highcharts from "highcharts";
import ReactHighcharts from "common-ui/lib/highcharts/ReactHighcharts";

const RadialBarChart = ({ chartData, title }) => {
  const options = {
    chart: {
      type: "column",
      inverted: true,
      polar: true,
      height: "250px",
      plotBorderWidth: null
    },
    title: {
      text: title
    },
    tooltip: {
      outside: true
    },
    pane: {
      size: "85%",
      innerSize: "20%",
      endAngle: 260,
      center: ["60%", "50%"],
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
      tickInterval: 25,
      reversedStacks: false,
      endOnTick: true,
      showLastLabel: true,
      gridLineWidth: 0
    },
    legend: {
      layout: "vertical",
      align: "right",
      verticalAlign: "middle",
      itemMarginTop: 3,
      itemMarginBottom: 3,
      symbolPadding: 5,
      itemStyle: {
        padding: 0,
        color: "#8693A6",
        cursor: "pointer",
        fontSize: "10px",
        fontWeight: "400",
        whiteSpace: "normal",
        overflow: "visible",
        textOverflow: "clip"
      },
      maxHeight: 200,
      width: 100,
    },
    plotOptions: {
      column: {
        stacking: "normal",
        borderWidth: 0,
        pointPadding: 0,
        groupPadding: 0.15,
        showInLegend: true
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
