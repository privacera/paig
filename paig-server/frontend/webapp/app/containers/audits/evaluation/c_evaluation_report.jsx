import React, { Component, Fragment } from 'react';
import { observable } from 'mobx';
import { observer, inject } from 'mobx-react';

import Box from '@material-ui/core/Box';

import f from 'common-ui/utils/f';
import BaseContainer from 'containers/base_container';
import VEvaluationOverview from 'components/audits/evaluation/v_evaluation_report';

@inject('evaluationStore')
@observer
export class CEvaluationReport extends Component {
  @observable _vState = {
    reportData: null,
    loading: true
  }
  // appNameColorMap = new ObservableMap();
  constructor(props) {
    super(props);

    // donut chart data
    this.cEvaluationOverview = f.initCollection();
  }

  componentDidMount() {
    this.fetchAllApi();
  }

  fetchAllApi = () => {
    if (this.props.match.params.eval_id) {
      // get report details
      this.getReportDetails(this.props.match.params.eval_id);
    } else {
      this._vState.reportData = null;
      this._vState.loading = false;
    }
  };

  getReportDetails = (id) => {
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
      name: "Pass rate",
      data: [],
      color: "#00CC77",
    };
  
    const failRateSeries = {
      name: "Fail rate",
      data: [],
      color: "#D8DBDE",
    };
  
    const categories = [];
  
    apps.forEach((app) => {
      categories.push(app.application_name); 
      passRateSeries.data.push(app.passed); 
      failRateSeries.data.push(app.failed);
    });
  
    const chartData = {
      categories,
      series: [passRateSeries, failRateSeries]
    };
  
    f.resetCollection(this.cEvaluationOverview, [chartData]);
  };
  
  

  handleRedirect = () => {
    this.props.history.push('/eval_reports');
  }

  handleBackButton = () => {
    this.handleRedirect();
  }

  render() {
    const {_vState, handleBackButton, handleDateChange} = this;
    return (
      <BaseContainer
        showRefresh={false}
        showBackButton={true}
        backButtonProps={{
          size: 'small',
          onClick: handleBackButton
        }}
        titleColAttr={{
          sm: 6,
          md: 6
        }}
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
        <VEvaluationOverview cEvaluationOverview={this.cEvaluationOverview} />
      </BaseContainer>
    );
  }
}

export default CEvaluationReport;
