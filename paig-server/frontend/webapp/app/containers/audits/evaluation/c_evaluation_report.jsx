import React, {Component, Fragment} from 'react';
import {observer, inject} from 'mobx-react';
import {observable} from 'mobx';

import Box from '@material-ui/core/Box';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import {EVAL_REPORT_CATEGORIES} from 'utils/globals';
import BaseContainer from 'containers/base_container';
import VEvaluationOverview from 'components/audits/evaluation/v_evaluation_report';

@inject('evaluationStore')
@observer
export class CEvaluationReport extends Component {
  @observable _vState = {
    reportData: null,
    loading: true,
    searchFilterValue: []
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
    if (this.props.match.params.eval_id) {
      // Get report details
      this.getReportOverview(this.props.match.params.eval_id);
      // Get table data
      this.getReportDetails(this.props.match.params.eval_id);
    } else {
      this._vState.reportData = null;
      this._vState.loading = false;
    }
  };

  getReportOverview = (id) => {
    this._vState.loading = true;
    this.props.evaluationStore.fetchReportCumulative(id)
      .then((response) => {
        this._vState.reportData = response;
        this.formatReportData(response);
        this._vState.loading = false;
      }, f.handleError(null, () => {
        this._vState.loading = false;
        this._vState.reportData = null;
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

  getReportDetails = (id) => {
    f.beforeCollectionFetch(this.cEvaluationDetailed);
    this.props.evaluationStore.fetchReportDetailed(id, {
      params: this.cEvaluationDetailed.params
    })
    .then(f.handleSuccess(this.cEvaluationDetailed), f.handleError(this.cEvaluationDetailed));
  }

  handleRedirect = () => {
    this.props.history.push('/eval_reports');
  }

  handleBackButton = () => {
    this.handleRedirect();
  }

  handlePageChange = () => {
    this.fetchAllApi();
  }

  handleSearchByField = (filter) => {
    const newParams = { page: undefined };
    Object.values(EVAL_REPORT_CATEGORIES).forEach(obj => {
      newParams[`includeQuery.${obj.key}`] = undefined;
      newParams[`excludeQuery.${obj.key}`] = undefined;
    })

    filter.forEach(({ category, operator, value }) => {
      const obj = Object.values(EVAL_REPORT_CATEGORIES).find(item => item.category === category);
      if (obj) {
        const prefix = operator === 'is' ? 'includeQuery' : 'excludeQuery';
        newParams[`${prefix}.${obj.key}`] = value;
      }
    });
    Object.assign(this.cEvaluationDetailed.params, newParams);
    this._vState.searchFilterValue = filter;
    this.getReportDetails(this.props.match.params.eval_id);
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
    const {_vState, cEvaluationOverview, cEvaluationDetailed, handleBackButton, handlePageChange, handleSearchByField} = this;
    return (
      <BaseContainer
        showRefresh={false}
        showBackButton={true}
        backButtonProps={{
          size: 'small',
          onClick: handleBackButton
        }}
        titleColAttr={{sm: 12, md: 12}}
        nameProps={{maxWidth: '100%'}}
        title={this.renderTitle()}
      >
        <VEvaluationOverview 
          _vState={_vState}
          cEvaluationOverview={cEvaluationOverview} 
          data={cEvaluationDetailed}
          handlePageChange={handlePageChange}
          handleSearchByField={handleSearchByField}
        />
      </BaseContainer>
    );
  }
}

export default CEvaluationReport;
