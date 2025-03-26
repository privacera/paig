import React, {Component, Fragment} from 'react';
import {observer, inject} from 'mobx-react';
import {observable} from 'mobx';

import Box from '@material-ui/core/Box';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import {EVAL_REPORT_CATEGORIES} from 'utils/globals';
import VEvaluationReportDetails from 'components/audits/evaluation/v_evaluation_report_details';


@inject('evaluationStore')
@observer
export class CEvaluationReportDetails extends Component {
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
    if (this.props.parent_vState && this.props.parent_vState.eval_id) {
      // Get report details
      this.getReportOverview(this.props.parent_vState.eval_id);
      // Get table data
      this.getReportDetails(this.props.parent_vState.eval_id);
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
    this.getReportDetails(this.props.parent_vState.eval_id);
  }

  handleToggleChange = (value) => {
    const updated_params = this.updateStatusParams(this.cEvaluationDetailed.params, value);
    this.cEvaluationDetailed.params = updated_params;
    this.getReportDetails(this.props.parent_vState.eval_id);
  }

  handleCategoryChange = (value) => {
    const updated_params = this.updateCategoryParams(this.cEvaluationDetailed.params, value);
    this.cEvaluationDetailed.params = updated_params;
    this.getReportDetails(this.props.parent_vState.eval_id);

  }

  updateCategoryParams = (params, value) => {
    const updatedParams = { ...params };
    if (!value) {
      // If value is null, undefined, or an empty string, remove category filters
      delete updatedParams['includeQuery.category'];
      delete updatedParams['excludeQuery.category'];
    } else {
      // Otherwise, set includeQuery.category to the given value
      updatedParams['includeQuery.category'] = value;
      // Ensure excludeQuery.category is removed
      delete updatedParams['excludeQuery.category'];
    }
    return updatedParams;
  }

  updateStatusParams = (params, value) =>  {
    const updatedParams = { ...params };
    if (value.toLowerCase() === 'show all') {
        // Remove "includeQuery.status" and "excludeQuery.status"
        const { ["includeQuery.status"]: _, ["excludeQuery.status"]: __, ...updatedParams } = params;
        return updatedParams;
    }
    if (value.toLowerCase() === 'passed') {
        updatedParams["includeQuery.status"] = "PASSED";
        delete updatedParams["excludeQuery.status"];
    } else if (value.toLowerCase() === 'failed') {
        delete updatedParams["includeQuery.status"];
        updatedParams["excludeQuery.status"] = "PASSED";
    }
    return updatedParams;
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
    const {_vState, cEvaluationOverview, cEvaluationDetailed, handleBackButton, handlePageChange, handleSearchByField, handleToggleChange, handleCategoryChange} = this;
    return (
        <VEvaluationReportDetails 
          _vState={_vState}
          cEvaluationOverview={cEvaluationOverview} 
          data={cEvaluationDetailed}
          handlePageChange={handlePageChange}
          handleSearchByField={handleSearchByField}
          handleToggleChange={handleToggleChange}
          handleCategoryChange={handleCategoryChange}
        />
    );
  }
}

export default CEvaluationReportDetails;
