import React, { Component, Fragment } from 'react';
import { inject } from 'mobx-react';
import { startCase } from 'lodash';

import HelpIcon from '@material-ui/icons/Help';
import Grid from '@material-ui/core/Grid';

import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import BaseContainer from 'containers/base_container';
import {MESSAGE_RESULT_TYPE, DATE_UNITS_GAP} from 'utils/globals';
import {findActiveGuideByName, clearGuideTimeout, PENDO_GUIDE_NAME} from 'components/pendo/pendo_initializer';
import {VUsage, VSensitiveDataAccess, VDataAccess} from 'components/dashboard/v_dashboard';
import DashboardUtils from "utils/dashboard_utils";
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';
import {DateRangePickerComponent} from 'common-ui/components/filters';
import {getUnitGap} from 'components/reports/gen_ai_report_util';

const moment = Utils.dateUtil.momentInstance();

@inject("dashboardStore")
export class CDashboard extends Component {
  state = {
    guide: null
  }
  dateRangeDetail = {
		daterange: Utils.dateUtil.getLastThreeMonthRange(),
		chosenLabel: 'Last 3 Months'
	}
  dateRangePickerRange = () => {
		let ranges = Object.assign(Utils.dateRangePickerRange(), {
			'Last 3 Months': Utils.dateUtil.getLastThreeMonthRange(),
			'Last 6 Months': Utils.dateUtil.getLastSixMonthRange()
		});
		Object.defineProperty(ranges, 'Last 3 Months', { get: function () { return Utils.dateUtil.getLastThreeMonthRange(); } });
		Object.defineProperty(ranges, 'Last 6 Months', { get: function () { return Utils.dateUtil.getLastSixMonthRange(); } });
		return ranges;
	}
  constructor(props) {
    super(props);

    // donut chart data
    this.cMessageUsage = f.initCollection();
    this.cSensitiveDataPromptUsage = f.initCollection();
    this.cSensitiveDataRepliesUsage = f.initCollection();

    this.cMessageUsage.params = {groupBy: 'result'};
    this.cSensitiveDataPromptUsage.params = {groupBy: 'result', 'includeQuery.requestType': 'prompt'};
    this.cSensitiveDataRepliesUsage.params = {groupBy: 'result', 'includeQuery.requestType': 'reply'};

    // bar chart data
    this.cSensitiveDataInApplication = f.initCollection();
    this.cSensitiveDataInApplication.params = {groupBy: 'traits,applicationName'};

    // column chart data
    this.cAccessData = f.initCollection();
    this.cAccessData.params = {groupBy: 'result'};
    
    this.assignDateToParams();
  }

  componentDidMount() {
    this.fetchAllApi();
    this.initGuide();
  }
  componentWillUnmount() {
    clearGuideTimeout(PENDO_GUIDE_NAME.DASHBOARD_TOUR);
  }
  initGuide = async() => {
    let guide = await findActiveGuideByName(PENDO_GUIDE_NAME.DASHBOARD_TOUR);
    this.setState({guide});
  }

  getDateRange = () => {
		const from = this.dateRangeDetail.daterange[0].valueOf();
		const to = this.dateRangeDetail.daterange[1].valueOf();
		return {
			fromTime: from,
			toTime: to
		}
	}

  assignDateToParams = () => {
    const dateRange = this.getDateRange();
    const interval = getUnitGap(this.dateRangeDetail.chosenLabel, this.dateRangeDetail);
    // donut chart params
    Object.assign(this.cMessageUsage.params, dateRange);
    Object.assign(this.cSensitiveDataPromptUsage.params, dateRange);
    Object.assign(this.cSensitiveDataRepliesUsage.params, dateRange);
  
    // bar chart params
    Object.assign(this.cSensitiveDataInApplication.params, dateRange);
  
    // column chart params
    Object.assign(this.cAccessData.params, dateRange, { interval });
  }

  handleDateChange = (event, picker) => {
		this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
		this.dateRangeDetail.chosenLabel = picker.chosenLabel;
    this.assignDateToParams();
		this.fetchAllApi();
	}

  handleRefresh = () => {
    this.fetchAllApi();
  };
  
  fetchAllApi = () => {
    this.fetchAndFormatData(this.cMessageUsage);
    this.fetchAndFormatData(this.cSensitiveDataPromptUsage);
    this.fetchAndFormatData(this.cSensitiveDataRepliesUsage);

    this.fetchSensitiveDataInApplications();

    this.fetchAccessData();
  };

  fetchAndFormatData = async (coll) => {
    f.beforeCollectionFetch(coll);
    try {
      let {result} = await this.props.dashboardStore.fetchUsageCounts({
        params: coll.params
      });

      Object.values(MESSAGE_RESULT_TYPE).forEach(obj => {
        if (!result.hasOwnProperty(obj.NAME)) {
          result[obj.NAME] = {
            count: 0,
            color: obj.COLOR
          };
        } else {
          result[obj.NAME].color = obj.COLOR
        }
      })

      let chartData = Object.keys(result).map(key => {
        return {
          name: startCase(key),
          y: parseInt(result[key].count),
          color: result[key].color
        }
      })

      let totalCount = chartData.reduce((sum, data) => sum + data.y, 0);
      let model = {totalCount, chartData}
      f.resetCollection(coll, [model]);
    } catch(e) {
      console.error("Failed to get count", e);
      f.resetCollection(coll, []);
    }
  }

  fetchSensitiveDataInApplications = async () => {
    f.beforeCollectionFetch(this.cSensitiveDataInApplication);
    try {
      let result = await this.props.dashboardStore.fetchTraitCounts({
        params: this.cSensitiveDataInApplication.params
      });
      let data = DashboardUtils.formatSensitiveDataInApplications(result);
      f.resetCollection(this.cSensitiveDataInApplication, data);
    } catch(e) {
      console.error("Failed to get sensitive data in application", e);
      f.resetCollection(this.cSensitiveDataInApplication, []);
    }
  }

  fetchAccessData = async () => {
    f.beforeCollectionFetch(this.cAccessData);
    const interval =  this.cAccessData.params.interval;
    try {
      let result = await this.props.dashboardStore.fetchAccessDataCounts({
        params: this.cAccessData.params
      });
      let data = {
        categories: [],
        series: []
      }
  
      if (result[interval]) {
        data.series = [
          {
            name: "Allowed Access",
            data: [],
            color: MESSAGE_RESULT_TYPE.ALLOWED.COLOR
          },
          {
            name: "Denied Access",
            data: [],
            color: MESSAGE_RESULT_TYPE.DENIED.COLOR
          },
          {
            name: "Masked Access",
            data: [],
            color: MESSAGE_RESULT_TYPE.MASKED.COLOR
          }
        ]
  
        // Sort result by interval
        const sortedTimestamp = Object.fromEntries(
          Object.entries(result[interval]).sort(([a], [b]) => a - b)
        );
  
        for (const timestamp in sortedTimestamp) {
          const date = moment(parseInt(timestamp));
          data.categories.push(date.format(DATE_UNITS_GAP[interval.toUpperCase()].format));
  
          const d = result[interval][timestamp]?.result;
          data.series[0].data.push(d?.allowed?.count || 0);
          data.series[1].data.push(d?.denied?.count || 0);
          data.series[2].data.push(d?.masked?.count || 0);
        }
      }
      f.resetCollection(this.cAccessData, [data]);
    } catch (e) {
      console.error("Failed to get access data", e);
      f.resetCollection(this.cAccessData, []);
    }
  };

  render() {
    const {dateRangeDetail, handleDateChange} = this;
    return (
      <BaseContainer
        className="page-title"
        handleRefresh={this.handleRefresh}
        titleColAttr={this.state.guide ? {md: null, xs: null} : {lg: 7, md: 5, xs: 12}}
        headerChildren={(
          <Fragment>
            {this.state.guide &&
              <Grid item className='flex-grow-2 p-l-0'>
                <CustomAnchorBtn
                  tooltipLabel="Dashboard Tour"
                  data-track-id="dashboard-tour"
                  icon={<HelpIcon />}
                  onClick={() => {
                    pendo.showGuideById(this.state.guide.id);
                  }}
                />
              </Grid>
            }
            <DateRangePickerComponent
              colAttr={{ lg: 5, md: 7, sm: 12, xs: 12, className: 'text-right pull-right'}}
              showSwitchBox={false}
              daterange={dateRangeDetail.daterange}
              chosenLabel={dateRangeDetail.chosenLabel}
              handleEvent={handleDateChange}
              ranges={this.dateRangePickerRange()}
              dateRangePickerAttr={{ maxDate: Utils.dateUtil.momentInstance()() }}
            />
          </Fragment>
        )}
      >
        <VUsage
          cMessageUsage={this.cMessageUsage}
          cSensitiveDataPromptUsage={this.cSensitiveDataPromptUsage}
          cSensitiveDataRepliesUsage={this.cSensitiveDataRepliesUsage}
        />
        <VSensitiveDataAccess data={this.cSensitiveDataInApplication} />
        <VDataAccess data={this.cAccessData} />
      </BaseContainer>
    );
  }
}

export default CDashboard;
