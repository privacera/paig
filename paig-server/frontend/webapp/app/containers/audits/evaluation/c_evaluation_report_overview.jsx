import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import {observable} from 'mobx';

import Box from '@material-ui/core/Box';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import VEvaluationReportOverview from 'components/audits/evaluation/v_evaluation_report_overview';

@inject('evaluationStore')
export class CEvaluationReportOverview extends Component {
  @observable _vState = {
    reportData: null,
    loading: true,
    searchFilterValue: [],
    reportSeverity: null,
    reportStats: null
  }
  constructor(props) {
    super(props);

    // Donut chart data
    this.cEvaluationOverview = f.initCollection();

    // Table data
    this.cEvaluationDetailed = f.initCollection();
    this.cEvaluationDetailed.params = {
      page: 0,
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
    }
  }

  componentDidMount() {
    this.fetchAllApi();
  }

  fetchAllApi = () => {
    if (this.props.parent_vState && this.props.parent_vState.eval_id) {
      // Get report details
      this.getReportOverview(this.props.parent_vState.eval_id);
      this.getReportCategoryStats(this.props.parent_vState.eval_id);
      this.getReportSeverity(this.props.parent_vState.eval_id);
    } else {
      this._vState.reportData = null;
      this._vState.loading = false;
    }
  };

  getReportOverview = (id) => {
    this.props.evaluationStore.fetchReportCumulative(id)
      .then((response) => {
        this._vState.reportData = response;
        this.formatReportData(response);
      }, f.handleError(null, () => {
        this._vState.reportData = null;
      }));
  }

  getReportSeverity = (id) => {
    this.props.evaluationStore.fetchReportSeverity(id)
      .then((response) => {
        this._vState.reportSeverity = response;
        this._vState.loading = false;
      }, f.handleError(null, () => {
        this._vState.loading = false;
        this._vState.reportSeverity = null;
      }));
  }

  getReportCategoryStats = (id) => {
    this.props.evaluationStore.fetchReportCategoryStats(id)
      .then((response) => {
        this._vState.reportStats = response;
      }, f.handleError(null, () => {
        this._vState.reportStats = null;
      }));
  }

  formatReportData = (reportData) => {
    const apps = reportData.result;

    // Categories for series
    const passRateSeries = {
      name: "Pass rate (%)",
      data: [],
      color: "#00CC77",
    };

    const failRateSeries = {
      name: "Fail rate (%)",
      data: [],
      color: "#ff4d01",
    };

    const errorRateSeries = {
      name: "Error rate (%)",
      data: [],
      color: "#FFC107",
    };

    const categories = [];
  
    apps.forEach((app) => {
      categories.push(app.application_name); 
      const total = app.passed + app.failed + app.error || 0;
      passRateSeries.data.push(((app.passed / total || 0) * 100));
      failRateSeries.data.push(((app.failed / total || 0) * 100));
      errorRateSeries.data.push(((app.error / total || 0) * 100));
    });
  
    const chartData = {
      categories,
      series: [passRateSeries, failRateSeries, errorRateSeries]
    };
  
    f.resetCollection(this.cEvaluationOverview, [chartData]);
  };


  handleRedirect = () => {
    this.props.history.push('/eval_reports');
  }

  handleBackButton = () => {
    this.handleRedirect();
  }

  handlePageChange = () => {
    this.fetchAllApi();
  }

  handleTabSelect = (key, filter) => {
    this.props.parent_vState.searchFilterValue  = filter;
    this.props.handleTabSelect(key);
  }

  renderTitle = () => {
    const { reportData } = this._vState;
    return reportData ? (
      <Box className="ellipsize" component="div">
        Evaluation Report - {reportData.report_name}
      </Box>
    ) : null;
  };

  render() {
    const {_vState, parent_vState, cEvaluationOverview, cEvaluationDetailed, handleBackButton, handlePageChange, handleSearchByField, handleTabSelect} = this;
    return (
        <VEvaluationReportOverview 
          _vState={_vState}
          parent_vState={parent_vState}
          cEvaluationOverview={cEvaluationOverview} 
          data={cEvaluationDetailed}
          handlePageChange={handlePageChange}
          handleSearchByField={handleSearchByField}
          handleTabSelect={handleTabSelect}
        />
    );
  }
}

export default CEvaluationReportOverview;
