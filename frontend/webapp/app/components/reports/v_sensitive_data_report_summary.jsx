import React, { Component } from 'react';
import { observer } from 'mobx-react';
import { startCase, sortBy } from 'lodash';

import { Box, Grid, Paper, Typography, Chip, Tooltip } from '@material-ui/core';
import TableCell from "@material-ui/core/TableCell";
import FiberManualRecordIcon from '@material-ui/icons/FiberManualRecord';

import f from 'common-ui/utils/f';
import { Loader, getSkeleton } from 'common-ui/components/generic_components'
import { DATE_UNITS_GAP } from 'utils/globals';
import DonutChart from "components/dashboard/donut_chart";
import Table from "common-ui/components/table";
import ReactHighcharts from "common-ui/lib/highcharts/ReactHighcharts";
import { MultibarHighcharts, WordCloudChart } from 'common-ui/components/charts';

const PaperCard = (props) => {
  const { children, boxProps = {}, ...paperProps } = props;
  return (
    <Paper {...paperProps}>
      <Box {...boxProps}>{children}</Box>
    </Paper>
  );
};

const pieChartOptions = {
  chart: {
    type: "pie",
    plotBackgroundColor: null,
    plotBorderWidth: null,
    plotShadow: false,
    height: "200px",
    marginLeft: 22
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
      color: "rgba(0, 0, 0, 0.87)",
      cursor: "pointer",
      fontWeight: "400",
      width: "200px",
      whiteSpace: "nowrap",
      overflow: "hidden",
      textOverflow: "ellipsis",
      fontSize: '14px',
    },
    labelFormatter: function () {
      return "&nbsp" + this.name + " (" + this.y + ")";
    }
  },
  subtitle: {
    x: -55
  },
  exporting: {
    url: false,
    enabled: false,
    sourceWidth: 400,
    sourceHeight: 250,
    marginLeft: 0,
    allowHTML: false,
    fallbackToExportServer: false
  },
  credits: {
    enabled: false
  }
}

@observer
class VMetricData extends Component {
  render() {
    const { options } = this.props;
    const { _vState } = options
    return (
      <Grid container spacing={3} className="align-items-center m-b-sm m-t-sm">
        <Grid item md={4} sm={6} data-track-id="apps-with-sensitive-data">
          <PaperCard boxProps={{ p: 2 }}>
            <Tooltip arrow placement="top-start" title={"Number of applications containing sensitive data. Indicates the scope of data protection required across applications."}>
              <Typography variant="h6" className="graph-title inline-block">Apps With Sensitive Data</Typography>
            </Tooltip>
            <Typography variant="h5">{_vState.applicationAccessCount}</Typography>
          </PaperCard>
        </Grid>
        <Grid item md={4} sm={6} data-track-id="sensitive-data-access-count">
          <PaperCard boxProps={{ p: 2 }}>
            <Tooltip arrow placement="top-start" title={"Total instances of sensitive data being accessed. Reflects the frequency of interaction with sensitive data."}>
              <Typography variant="h6" className="graph-title inline-block">Sensitive Data Access Count</Typography>
            </Tooltip>
            <Typography variant="h5">{_vState.sensitiveAccessCount}</Typography>
          </PaperCard>
        </Grid>
        <Grid item md={4} sm={6} data-track-id="users-accessing-sensitive-data">
          <PaperCard boxProps={{ p: 2 }}>
            <Tooltip arrow placement="top-start" title={"Count of unique users who accessed sensitive data. Helps in identifying user engagement with protected data."} >
              <Typography variant="h6" className="graph-title inline-block">Users Accessing Sensitive Data</Typography>
            </Tooltip>
            <Typography variant="h5">{_vState.sensitiveTagsCount}</Typography>
          </PaperCard>
        </Grid>
      </Grid>
    );
  }
}

@observer
class VSensitiveDataAccess extends Component {
  formatBarGraphDataForField = (_data = []) => {
    const { options } = this.props;
    const { _vState, moment } = options;
    const gapObj = DATE_UNITS_GAP[_vState.gap?.toUpperCase()];
    const obj = {
      categories: [],
      data: []
    };
    const innerObj = {};
    _data = sortBy(_data, 'name');
    _data.forEach((d) => {
      let name = d.name;
      if (gapObj) {
        const date = moment(d.name);
        name = date.format(gapObj.format);
      }
      obj.categories.push(name);
      d.data.forEach(_d => {
        if (!innerObj[_d.type]) {
          innerObj[_d.type] = { name: _d.type, data: [] };
        }
        innerObj[_d.type].data.push(_d.count);
      })
    });
    obj.data = Object.values(innerObj);
    return obj;
  }
  render() {
    const { options, title } = this.props;
    const { cSensitiveDataAccess } = options;
    const chartOptions = {
      chart: {
        type: "column",
        spacing: [10, 25, 10, 25]
      },
      plotOptions: {
        column: {
          stacking: 'normal',
          dataLabels: {
            enabled: false
          },
          groupPadding: 1,
          pointWidth: 30
        }
      },
      xAxis: {
        gridLineWidth: 1,
        lineWidth: 1
      },
      yAxis: {
        title: "",
        gridLineWidth: 1,
        lineWidth: 1
      },
      legend: {
        align: 'right',
        verticalAlign: 'top',
        x: 0,
        y: 0,
        floating: true,
        borderWidth: 1,
        backgroundColor: "#fff",
        shadow: false
      },
      exporting: {
        url: null,
        enabled: false,
        sourceWidth: 700,
        sourceHeight: 400,
        chartOptions: {
          chart: {
            marginTop: 50
          },
          legend: {
            itemStyle: {
              fontSize: '14px',
              textOverflow: null
            }
          },
          plotOptions: {
            column: {
              dataLabels: {
                enabled: true
              }
            },
            xAxis: {
              labels: {
                style: {
                  fontSize: '14px'
                }
              }
            },
            yAxis: {
              labels: {
                style: {
                  fontSize: '14px'
                }
              }
            }
          }
        },
        fallbackToExportServer: false
      }
    }
    return (
      <PaperCard boxProps={{ p: 2 }} data-track-id="access-type-for-sensitive-data">
         <Tooltip arrow placement="top-start" title={"Breakdown of sensitive data access by type: Allowed, Denied, Masked. Provides insights into data protection enforcement."} >
          <Typography className='graph-title inline-block' gutterBottom>
            {title}
          </Typography>
        </Tooltip>
        <MultibarHighcharts
          ref={ref => this.sensitiveDataChart = ref}
          chartOptions={chartOptions}
          data={cSensitiveDataAccess}
          formatData={(data) => this.formatBarGraphDataForField(data)}
          xAxisText=""
          yAxisText=""
        />
      </PaperCard>
    );
  }
}

@observer
class VUserPrompt extends Component {
  render() {
    const { cUserPrompt, title } = this.props;
    return (
      <PaperCard boxProps={{ p: 2 }}>
        <Tooltip arrow placement="top-start" title={"Distribution of sensitive data access in prompts: Allowed, Denied, Masked. Shows how data protection policies are applied to user prompts."} >
          <Typography className='graph-title inline-block' gutterBottom>
            {title}
          </Typography>
        </Tooltip>
        <Loader promiseData={cUserPrompt} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
          <DonutChart
            ref={ref => this.userPromptChart = ref}
            chartOptions={pieChartOptions}
            data={f.models(cUserPrompt).length ? f.models(cUserPrompt)[0] : {}}
          />
        </Loader>
      </PaperCard>
    )
  }
}

@observer
class VRepliesPrompt extends Component {
  render() {
    const { options, title } = this.props;
    const { cRepliesPrompt } = options;
    return (
      <PaperCard boxProps={{ p: 2 }}>
        <Tooltip arrow placement="top-start" title={"Distribution of sensitive data access in replies: Allowed, Denied, Masked. Illustrates the effectiveness of data protection in AI responses."} >
          <Typography className='graph-title inline-block' gutterBottom>
            {title}
          </Typography>
        </Tooltip>
        <Loader promiseData={cRepliesPrompt} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
          <DonutChart
            ref={ref => this.repliesPromptChart = ref}
            chartOptions={pieChartOptions}
            data={f.models(cRepliesPrompt).length ? f.models(cRepliesPrompt)[0] : {}}
          />
        </Loader>
      </PaperCard>
    )
  }
}

@observer
class VSensitiveWordCould extends Component {
  render() {
    const { options, title } = this.props;
    const { cSensitiveWorldCloud } = options;
    const chartOptions = {
      chart: {
        type: 'wordcloud',
        height: "490px"
      },
      plotOptions: {
        wordcloud: {
          minFontSize: 5,
          maxFontSize: 55
        }
      },
      exporting: {
        url: null,
        enabled: false,
        sourceWidth: 700,
        sourceHeight: 400,
        title: {
          itemStyle: {
            fontSize: "14px"
          }
        }
      }
    };
    return (
      <PaperCard boxProps={{ p: 2 }} data-track-id="sensitive-data-word-cloud">
        <Tooltip arrow placement="top-start" title={"Visual representation of sensitive data frequency. The size of each term correlates with its access frequency."} >
          <Typography className='graph-title inline-block' gutterBottom>
            {title}
          </Typography>
        </Tooltip>
        <WordCloudChart
          ref={ref => this.wordCloudChart = ref}
          chartOptions={chartOptions}
          data={cSensitiveWorldCloud}
        />
      </PaperCard>
    );
  }
}

@observer
class VSensitiveTagsDistribution extends Component {
  optionsTable = {
    chart: {
      type: "bar",
      height: 50,
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
  getHeaders = () => {
    return [
      <TableCell key="1" column="tag">Tags</TableCell>,
      <TableCell key="2" column="queries">Queries</TableCell>,
      <TableCell key="3" column="graphData" className="pl-13">Distribution</TableCell>
    ];
  }
  getRows = model => {
    const { options } = this.props;
    const { _vState } = options;
    this.optionsTable.yAxis.max = _vState.maxQueryCount;
    const greyBgSeries = {
      name: 'Greybg Series',
      data: [_vState.maxQueryCount],
      grouping: false,
      stacking: false,
      showInLegend: false,
      enableMouseTracking: false,
      zIndex: -1,
      color: '#e6e5e5',
    }
    const rows = [
      <TableCell key="1" column="tag">
        <Chip className="table-container-chips" label={model.tag} />
      </TableCell>,
      <TableCell key="2" column="queries">{model.queries}</TableCell>,
      <TableCell key="3" column="graphData" width="100%">
        <ReactHighcharts ref={ref => this[model.tag + 'ChartRef'] = ref} options={{ ...this.optionsTable, series: [...model.graphData, greyBgSeries] }} />
      </TableCell>
    ];
    return rows;
  }

  render() {
    const { options, title } = this.props;
    const { cSensitiveTagDistribution, appNameColorMap, _vState } = options;
    const appNames = Array.from(appNameColorMap.entries());
    return (
      <PaperCard boxProps={{ p: 2 }} data-track-id="sensitive-data-distribution-by-app">
        <Tooltip arrow placement="top-start" title={"Shows how sensitive data is distributed across different applications."} >
          <Typography className='graph-title inline-block' gutterBottom>
            {title}
          </Typography>
        </Tooltip>
        {
          appNames.length > 0 && (
            <div className='d-flex flex-wrap m-t-md'>
              {
                appNames.map((app, index) => {
                  const [name, color] = app;
                  return (
                    <div key={index} className={`d-flex m-r-md`}>
                      <FiberManualRecordIcon style={{color}} />
                      <Typography variant='body1'>{name}</Typography>
                    </div>
                  )
                })
              }
            </div>
          )
        }
        <Table
          tableClassName="report-table-border-less m-t-md"
          data={cSensitiveTagDistribution}
          getHeaders={this.getHeaders}
          getRowData={this.getRows}
          hasElevation={false}
          pagination={false}
        />
      </PaperCard>
    )
  }
}

@observer
class VAccessTrendsOverTime extends Component {
  formatBarGraphDataForField = (_data = []) => {
    const { options } = this.props;
    const { _vState, moment } = options;
    const gapObj = DATE_UNITS_GAP[_vState.gap?.toUpperCase()];
    const obj = {
      categories: [],
      data: []
    };
    const innerObj = {};
    _data = sortBy(_data, 'name');
    _data.forEach((d) => {
      let name = d.name;
      if (gapObj) {
        const date = moment(d.name);
        name = date.format(gapObj.format);
      }
      obj.categories.push(name);
      d.data.forEach(_d => {
        if (!innerObj[_d.type]) {
          innerObj[_d.type] = { name: _d.type, data: [] };
        }
        innerObj[_d.type].data.push(_d.count);
      })
    });
    obj.data = Object.values(innerObj);
    return obj;
  }
  render() {
    const { options, title } = this.props;
    const { cSensitiveDataAccess } = options;
    const chartOptions = {
      chart: {
        type: "spline",
        spacing: [10, 25, 10, 25]
      },
      plotOptions: {
        column: {
          dataLabels: {
            enabled: false
          },
          groupPadding: 1,
          pointWidth: 30
        }
      },
      xAxis: {
        gridLineWidth: 1,
        lineWidth: 1
      },
      yAxis: {
        title: "",
        gridLineWidth: 1,
        lineWidth: 1
      },
      legend: {
        align: 'right',
        verticalAlign: 'top',
        x: 0,
        y: 0,
        floating: true,
        borderWidth: 1,
        backgroundColor: "#fff",
        shadow: false
      },
      exporting: {
        url: null,
        enabled: false,
        sourceWidth: 700,
        sourceHeight: 400,
        chartOptions: {
          chart: {
            marginTop: 50
          },
          legend: {
            itemStyle: {
              fontSize: '14px',
              textOverflow: null
            }
          },
          plotOptions: {
            column: {
              dataLabels: {
                enabled: true
              }
            },
            xAxis: {
              labels: {
                style: {
                  fontSize: '14px'
                }
              }
            },
            yAxis: {
              labels: {
                style: {
                  fontSize: '14px'
                }
              }
            }
          }
        },
        fallbackToExportServer: false
      }
    }
    return (
      <PaperCard boxProps={{ p: 2 }} data-track-id="access-trend-by-time">
        <Tooltip arrow placement="top-start" title={"Visualizes the frequency of user content view by admins over time, aiding in identifying spikes and compliance investigations."} >
          <Typography className='graph-title inline-block' gutterBottom>
            {title}
          </Typography>
        </Tooltip>
        <MultibarHighcharts
          ref={ref => this.accessTrendsChart = ref}
          chartOptions={chartOptions}
          data={cSensitiveDataAccess}
          formatData={(data) => this.formatBarGraphDataForField(data)}
          xAxisText=""
          yAxisText=""
        />
      </PaperCard>
    );
  }
}

export {
  VMetricData,
  VUserPrompt,
  VRepliesPrompt,
  VSensitiveDataAccess,
  VSensitiveWordCould,
  VSensitiveTagsDistribution,
  VAccessTrendsOverTime
}