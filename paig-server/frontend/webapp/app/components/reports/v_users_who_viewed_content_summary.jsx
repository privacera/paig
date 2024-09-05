import React, { Component } from 'react';
import { observer } from 'mobx-react';
import { sortBy } from 'lodash';

import { Grid } from '@material-ui/core';

import f from 'common-ui/utils/f';
import { DATE_UNITS_GAP, REPORT_GRID_LABELS } from 'utils/globals';
import { BarHighcharts, MultibarHighcharts } from 'common-ui/components/charts';
import { PaperCard, TitleItem, MetricItemBox } from 'components/reports/report_components'

@observer
class VMetricDataGrid extends Component {
  render() {
    const { options } = this.props;
    const { _vState } = options
    return (
      <Grid container spacing={3} className="align-items-center m-b-sm m-t-sm">
        <MetricItemBox
          _vState={_vState}
          fieldName="adminContentViewCount"
          toolTipLabel={REPORT_GRID_LABELS.ADMIN_CONTENT_COMPLIANCE.LABEL}
          toolTipTitle={REPORT_GRID_LABELS.ADMIN_CONTENT_COMPLIANCE.TOOLTIP}
        />
        <MetricItemBox
          _vState={_vState}
          fieldName="reviewedMessageCount"
          toolTipLabel={REPORT_GRID_LABELS.REVIEWED_MESSAGE.LABEL}
          toolTipTitle={REPORT_GRID_LABELS.REVIEWED_MESSAGE.TOOLTIP}
        />
        <MetricItemBox
          _vState={_vState}
          fieldName="uniqUserReviewCount"
          toolTipLabel={REPORT_GRID_LABELS.UNIQ_USERS.LABEL}
          toolTipTitle={REPORT_GRID_LABELS.UNIQ_USERS.TOOLTIP}
        />
      </Grid>
    );
  }
}

@observer
class VComplianceReviewTrends extends Component {
  formatBarGraphDataForField = (data = []) => {
    const { options } = this.props;
    const { _vState, moment } = options;
    const obj = {
      categories: [],
      data: []
    }
    data = sortBy(data, 'name');
    const gapObj = DATE_UNITS_GAP[_vState.gap?.toUpperCase()];
    data.forEach(d => {
      let name = d.name;
      if (gapObj) {
        const date = moment(d.name);
        name = date.format(gapObj.format);
      }
      obj.categories.push(name);
      const o = { y: parseInt(d.count) };
      obj.data.push(o);
    });
    return obj;
  }
  render() {
    const { options } = this.props;
    const { cComplianceViewTrends } = options;
    return (
      <PaperCard boxProps={{ p: 2 }}>
        <TitleItem
          label={REPORT_GRID_LABELS.COMPLIANCE_REVIEW_TRENDS.LABEL}
          toolTipTitle={REPORT_GRID_LABELS.COMPLIANCE_REVIEW_TRENDS.TOOLTIP}
        />
        <BarHighcharts
          ref={ref => this.complianceChart = ref}
          data={cComplianceViewTrends}
          formatData={(data) => this.formatBarGraphDataForField(data)}
          xAxisText=""
          yAxisText=""
          chartOptions={{
            chart: {
              type: "line",
              spacing: [10, 25, 10, 25],
              height: 400
            },
            colors: ["#69C9F9"],
            xAxis: {
              title: "",
              gridLineWidth: 1,
              lineWidth: 1
            },
            yAxis: {
              title: "",
              gridLineWidth: 1,
              lineWidth: 1
            },
            series: [{
              name: 'Message Reviewed',
              data: [],
              pointWidth: 20,
              marker: {
                fillColor: '#FFFFFF',
                lineWidth: 2,
                lineColor: null,
                symbol: 'circle',
                radius: 6
              }
            }],
            legend: {
              align: 'right',
              verticalAlign: 'top',
              x: 0,
              y: 0,
              floating: true,
              borderWidth: 1,
              backgroundColor: '#FFFFFF',
              shadow: false
            },  
            tooltip: {
              formatter: function() {
                return `<b>${this.y}</b>`
              }
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
                plotOptions: {
                  series: {
                    dataLabels: {
                      enabled: true
                    }
                  }
                }
              },
              fallbackToExportServer: false
            }
          }}
        />
      </PaperCard>
    );
  }
}

@observer
class VTopReviewer extends Component {
  formatBarGraphDataForField = (_data = []) => {
    const obj = {
      categories: [],
      data: []
    };
    const innerObj = {
      Allowed: { name: 'Allowed', data: Array(_data.length).fill(0) },
      Denied: { name: 'Denied', data: Array(_data.length).fill(0) },
      Masked: { name: 'Masked', data: Array(_data.length).fill(0) }
    };
    _data.forEach((d, index) => {
      obj.categories.push(d.name);
      d.data.forEach(_d => {
        if (innerObj[_d.type]) {
          innerObj[_d.type].data[index] = _d.count;
        }
      });
    });
    obj.data = Object.values(innerObj);
    return obj;
  }
  render() {
    const { options } = this.props;
    const { cTopComplianceReviewer } = options;
    const data = f.models(cTopComplianceReviewer);
    const pointWidth = data.length < 5 ? 30 : (data.length < 10 ? 20 : 10);
    return (
      <PaperCard boxProps={{ p: 2 }}>
        <TitleItem
          label={REPORT_GRID_LABELS.TOP_REVIEWER_CONTENT_COMPLIANCE.LABEL}
          toolTipTitle={REPORT_GRID_LABELS.TOP_REVIEWER_CONTENT_COMPLIANCE.TOOLTIP}
        />
        <MultibarHighcharts
          ref={ref => this.topReviewerChart = ref}
          data={cTopComplianceReviewer}
          formatData={(data) => this.formatBarGraphDataForField(data)}
          xAxisText=""
          yAxisText=""
          chartOptions={{
            chart: {
              type: "column",
              spacing: [10, 25, 10, 25]
            },
            colors: ['#6FF17C', '#FD8A5B', '#69C9F9'],
            plotOptions: {
              column: {
                dataLabels: {
                  enabled: true,
                  formatter: function () {
                    if (typeof this.y === 'number' && this.y > 0) {
                      return this.y;
                    }
                  }                
                },
                pointWidth: pointWidth,
                groupPadding: 0.3
              }
            },
            xAxis: {
              title: "",
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
          }}
        />
      </PaperCard>
    );
  }
}

export {
  VMetricDataGrid,
  VComplianceReviewTrends,
  VTopReviewer
}