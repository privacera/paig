import React, {Component, createRef, Fragment} from 'react';
import {inject} from 'mobx-react';
import {action} from 'mobx';

import {Grid} from '@material-ui/core';

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import {Utils} from 'common-ui/utils/utils';
import FSModal from 'common-ui/lib/fs_modal';
import hashHistory from 'common-ui/routers/history';
import BaseContainer from 'containers/base_container';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {DateRangePickerComponent} from 'common-ui/components/filters';
import VRunReportForm from 'components/audits/evaluation/v_run_report_form';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';
import {evaluation_form_def} from 'components/audits/evaluation/v_evaluation_details_form';
import VEvaluationReportTable from 'components/audits/evaluation/v_evaluation_reports_list';

const CATEGORIES = {
  "Report Name": { multi: false, category: "Report Name", type: "text", key: 'name' },
  Application: { multi: false, category: "Application", type: "text", key: 'application_names' },
  Status: { multi: false, category: "Status", type: "text", key: 'status', options: () => ['GENERATING', 'EVALUATING', 'COMPLETED', 'FAILED'] }
}

@inject('evaluationStore')
class CEvaluationReportsList extends Component {
  runReportModalRef = createRef();
  state = {
    showIframe: false,
    iframeUrl: null, // URL for iframe content
  };

  _vState = {
    searchFilterValue: [],
    showNextPage: null,
    prevNextValueList:[''],
    pageNumber: 0,
  }
  constructor(props) {
    super(props);

    this.evalForm = createFSForm(evaluation_form_def);
    this.dateRangeDetail = {
      daterange: Utils.dateUtil.getLast7DaysRange(),
      chosenLabel: 'Last 7 Days'
    }

    this.cEvalReports = f.initCollection();
    this.cEvalReports.params = {
      size: 15,
      sort: 'create_time,desc',
      fromTime: this.dateRangeDetail.daterange[0].valueOf(),
      toTime: this.dateRangeDetail.daterange[1].valueOf()
    }

    this.applicationKeyMap = {};

    this.restoreState();
  }
  componentDidMount() {
    this.handleRefresh();
    // Auto-refresh every 30 secs
    this.refreshInterval = setInterval(() => {
      this.handleRefresh();
    }, 30000);
  }
  componentWillUnmount() {
    let {dateRangeDetail, _vState} = this;
    let {params} = this.cEvalReports;
    let {vName} = this.props;
    let data = JSON.stringify({params, dateRangeDetail, _vState});
    UiState.saveState(vName, data);
    // Clear the interval when the component is unmounted
    clearInterval(this.refreshInterval);
  }
  @action
  restoreState() {
    let data = UiState.getStateData(this.props.vName)
    if (!data) {
      return;
    }
    if (data.dateRangeDetail.daterange.length) {
      data.dateRangeDetail.daterange[0] = Utils.dateUtil.getMomentObject(data.dateRangeDetail.daterange[0]);
      data.dateRangeDetail.daterange[1] = Utils.dateUtil.getMomentObject(data.dateRangeDetail.daterange[1]);
    }
    Object.assign(this, {
      dateRangeDetail: data.dateRangeDetail,
      _vState: data._vState
    });
    this.cEvalReports.params = data.params;
  }
  handleRefresh = () => {
    this.fetchEvaluationReports();
  }
  fetchEvaluationReports = () => {
    f.beforeCollectionFetch(this.cEvalReports);
    this.props.evaluationStore.fetchEvaluationReports({
      params: this.cEvalReports.params
    }).then(f.handleSuccess(this.cEvalReports), f.handleError(this.cEvalReports));
  }

  handlePageChange = () => {
    this.fetchEvaluationReports();
  }

  handleDateChange = (event, picker) => {
    this._vState.prevNextValueList = [''];
    this._vState.pageNumber = 0;
    delete this.cEvalReports.params.page;
    if (picker.startDate) {
      this.cEvalReports.params.fromTime = picker.startDate.valueOf();
      this.cEvalReports.params.toTime = picker.endDate.valueOf();

      this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
    } else {
      delete this.cEvalReports.params.fromTime;
      delete this.cEvalReports.params.toTime;
      this.dateRangeDetail.daterange = [];
    }
    this.dateRangeDetail.chosenLabel = picker.chosenLabel;

    this.fetchEvaluationReports();
  }

  handleSearchByField = (filter, event) => {
    this._vState.prevNextValueList = [''];
    this._vState.pageNumber = 0;
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
      if (obj) {
        params[`${prefix}.${obj.key}`] = value;
      }        
    });
    Object.assign(this.cEvalReports.params, params);

    this._vState.searchFilterValue = filter;
    this.fetchEvaluationReports();
  }

  handleDelete = (model) => {
    f._confirm.show({
      title: `Delete Report`,
      children: <Fragment>Are you sure you want to delete the report <b>{model.name}</b>?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
    .then((confirm) => {
      this.props.evaluationStore.deleteReport(model.id,{
        models: this.cEvalReports
      })
      .then(() => {
        confirm.hide();
        f.notifySuccess('Report Deleted');
        this.fetchEvaluationReports();
      }, f.handleError(null, null, {confirm}));
    }, () => {});
  }

  handleView = (model) => {
    hashHistory.push(`/eval_report/${model.eval_id}`);
  }

  handleBack = () => {
    this.setState({
      showIframe: false,
      iframeUrl: null,
    });
  }

  handleReRun = (model) => {
    this.evalForm.clearForm();
    this.evalForm.refresh(model);
    this.evalForm.model = model;
    this.evalForm.refresh({name: model.config_name}); // Set form.name with model.config_name
    if (this.runReportModalRef.current) {
      this.runReportModalRef.current.show({
        title: 'Rerun Report Evaluation',
        btnOkText: 'ReRun',
        btnCancelText: 'Cancel'
      })
    }
  }

  handleRunSave = async () => {
    const form = this.evalForm;
    const formData = form.toJSON();
    formData.categories = JSON.parse(formData.categories || "[]"),
    formData.custom_prompts = [];

    try {
      this._vState.saving = true;
      let response = await this.props.evaluationStore.reRunReport(formData);
      this._vState.saving = false;
      this.runReportModalRef.current.hide();
      f.notifySuccess('Report evaluation submitted');
      this.fetchEvaluationReports();
      // this.handlePostCreate(response);
      this._vState.saving = false;
    } catch(e) {
      this._vState.saving = false;
      f.handleError()(e);
    }
}


  render() {
    const {_vState, dateRangeDetail, handleDateChange} = this;
    const { showIframe, iframeUrl } = this.state;
      

    return (
      <BaseContainer
        handleRefresh={this.handleRefresh}
        titleColAttr={{ lg: 12, md: 12 }}
      >
        <Fragment>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={12} md={6} lg={7}>
              <IncludeExcludeComponent
                _vState={_vState}
                categoriesOptions={Object.values(CATEGORIES)}
                onChange={this.handleSearchByField}
              />
            </Grid>
            <DateRangePickerComponent
              colAttr={{ lg: 5, md: 6, sm: 12, xs: 12, className: 'text-right' }}
              daterange={dateRangeDetail.daterange}
              chosenLabel={dateRangeDetail.chosenLabel}
              handleEvent={handleDateChange}
            />
          </Grid>
          <VEvaluationReportTable
            data={this.cEvalReports}
            pageChange={this.handlePageChange}
            _vState={_vState}
            applicationKeyMap={this.applicationKeyMap}
            handleDelete={this.handleDelete}
            handleView={this.handleView}
            handleReRun={this.handleReRun}
          />
        </Fragment>
        <FSModal ref={this.runReportModalRef} dataResolve={this.handleRunSave}>
          <VRunReportForm form={this.evalForm} mode="rerun_report"/>
        </FSModal>
      </BaseContainer>
    );
  }
}

CEvaluationReportsList.defaultProps = {
  vName: 'evaluationReports'
}

export default CEvaluationReportsList;