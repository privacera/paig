import React, { useEffect, useRef, useState } from "react";

import {
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from "@material-ui/core";
import { styled } from "@material-ui/core";

import ReactHighcharts from "common-ui/lib/highcharts/ReactHighcharts";

const optionsTable = {
  chart: {
    type: "bar",
    // plotBackgroundColor: null,
    // plotBorderWidth: null,
    // plotShadow: false,
    height: 50,
    // width: 450
    // spacingTop: 0,
    // spacingRight: 0,
    // spacingBottom: 0,
    // spacingLeft: 0
  },
  title: {
    text: null
  },
  xAxis: {
    visible: false,
    categories: []
  },
  yAxis: {
    visible: false
  },
  legend: {
    enabled: false
  },
  exporting: {
    enabled: false
  },
  tooltip: {
    headerFormat: null,
    pointFormat:
      "{series.name}: <b>{point.percentage:.1f}%</b><br/> Count: <b>{point.y}</b>"
  },
  plotOptions: {
    series: {
      stacking: "normal",
      dataLabels: {
        enabled: false
      }
    },
    bar: {
      pointWidth: 600
    }
  },
  series: [],
  credits: {
    enabled: false
  }
};

const BorderlessTable = styled(Table)({
  border: "none",
  "& th": {
    borderBottom: "none"
  },
  "& td": {
    borderBottom: "none",
    padding: "0px"
  }
});

const ApplicationTable = (props) => {
  const { distributionData, maxQuery } = props;
  const chartRef = useRef(null);
  const [chartWidth, setChartWidth] = useState(300);
  
  if(distributionData.length) {
    optionsTable.yAxis.max = maxQuery;
  }

  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current) {
        const containerWidth = chartRef.current.offsetWidth;
        setChartWidth(containerWidth);
      }
    };

    window.addEventListener("resize", handleResize);
    handleResize();

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  const greyBgSeries = {
    name: 'Greybg Series', //name will not be visible, just for info
    data: [maxQuery],
    grouping: false,
    stacking: false,
		showInLegend: false,
		enableMouseTracking: false,
    zIndex: -1,
    color: '#e6e5e5',
  }

  const optionsTableWithDynamicWidth = {
    ...optionsTable,
    chart: {
      ...optionsTable.chart,
      width: chartWidth,
    },
  };

  return (
    <TableContainer className="dashboard-table-container">
      <BorderlessTable>
        <TableHead>
          <TableRow>
            <TableCell>Tags</TableCell>
            <TableCell>Queries</TableCell>
            <TableCell className="pl-13">Distribution</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {distributionData &&
            distributionData.map((d, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Chip className="table-container-chips" label={d.tag} />
                </TableCell>
                <TableCell >{d.queries}</TableCell>
                <TableCell className="sensitive-data-graph" ref={chartRef} >
                  <ReactHighcharts chartWidth={chartWidth}
                    options={{ ...optionsTable, ...optionsTableWithDynamicWidth, series: [...d.graphData, greyBgSeries] }}
                  />
                </TableCell>
              </TableRow>
            ))}
        </TableBody>
      </BorderlessTable>
    </TableContainer>
  );

};

export { ApplicationTable };
