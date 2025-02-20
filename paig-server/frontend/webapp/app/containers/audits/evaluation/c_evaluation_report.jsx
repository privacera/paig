import React, { Component, Fragment } from 'react';
import { observable } from 'mobx';
import { observer, inject } from 'mobx-react';

import Box from '@material-ui/core/Box';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import BaseContainer from 'containers/base_container';
import VEvaluationOverview from 'components/audits/evaluation/v_evaluation_report';

const CATEGORIES = {
  Category: { multi: false, category: "Category", type: "text", key: 'category' },
  Prompt: { multi: false, category: "Prompt", type: "text", key: 'prompt' },
  Response: { multi: false, category: "Response", type: "text", key: 'response' }
}

@inject('evaluationStore')
@observer
export class CEvaluationReport extends Component {
  @observable _vState = {
    reportData: null,
    loading: true,
    searchFilterValue: []
  }
  // appNameColorMap = new ObservableMap();
  constructor(props) {
    super(props);

    // donut chart data
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
      // get report details
      this.getReportOverview(this.props.match.params.eval_id);
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
      color: "#D8DBDE",
    };

    const errorRateSeries = {
      name: "Error rate (%)",
      data: [],
      color: "#FF4D01",
    };

    const categories = [];
  
    apps.forEach((app) => {
      categories.push(app.application_name); 
      const total = app.passed + app.failed + app.error;
      passRateSeries.data.push(((app.passed / total) * 100));
      failRateSeries.data.push(((app.failed / total) * 100));
      errorRateSeries.data.push(((app.error / total) * 100));
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

  handleSearchByField = (filter, event) => {
    let params = {
      page: undefined
    };
    Object.values(CATEGORIES).forEach(obj => {
      params['includeQuery.' + obj.key] = undefined;
      params['excludeQuery.' + obj.key] = undefined;
    })

    filter.forEach((item) => {
      let obj = CATEGORIES[item.category];
      let prefix = item.operator == 'is' ? 'includeQuery' : 'excludeQuery';
      let value = item.value;
      if (obj.key) {    
        params[`${prefix}.${obj.key}`] = value;
      }        
    });
    Object.assign(this.cEvaluationDetailed.params, params);

    this._vState.searchFilterValue = filter;
    this.getReportDetails(this.props.match.params.eval_id);
  }

  render() {
    const {_vState, handleBackButton} = this;
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
        title={(
          <Fragment>
            {_vState.reportData && 
              <Box className='ellipsize' component="div">
                Evaluation Report - {_vState.reportData.report_name}
              </Box>
            } 
          </Fragment>
        )} 
      >
        <VEvaluationOverview 
          _vState={this._vState}
          cEvaluationOverview={this.cEvaluationOverview} 
          data={this.cEvaluationDetailed}
          handlePageChange={this.handlePageChange}
          handleSearchByField={this.handleSearchByField}
        />
      </BaseContainer>
    );
  }
}

export default CEvaluationReport;
