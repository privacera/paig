import React, {Component, createRef} from 'react';
import {inject, observer} from 'mobx-react';
import {action} from 'mobx';

import {Grid} from '@material-ui/core';
import {Button} from "@material-ui/core";

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import {Utils} from 'common-ui/utils/utils';
import FSModal from 'common-ui/lib/fs_modal';
import BaseContainer from 'containers/base_container';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {DateRangePickerComponent} from 'common-ui/components/filters';
import VRunReportForm from 'components/audits/evaluation/v_run_report_form';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';
import {evaluation_form_def} from 'components/audits/evaluation/v_evaluation_details_form';
import VEvaluationReportTable from 'components/audits/evaluation/v_evaluation_reports_list';
const CATEGORIES = {
  ReportName: { multi: false, category: "ReportName", type: "text", key: 'name' },
  Application: { multi: false, category: "Application", type: "text", key: 'application_names' },
  Status: { multi: false, category: "Status", type: "text", key: 'status', options: () => ['GENERATING', 'EVALUATING', 'COMPLETED', 'FAILED'] }
}

@inject('evaluationStore')
@observer
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
  }
  componentWillUnmount() {
    let {dateRangeDetail, _vState} = this;
    let {params} = this.cEvalReports;
    let {vName} = this.props;
    let data = JSON.stringify({params, dateRangeDetail, _vState});
    UiState.saveState(vName, data);
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
    }).then(res => {
      f.resetCollection(this.cEvalReports, res.models, res.pageState);            
    }, f.handleError(this.cEvalReports));
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
        if (obj.category && ['User', 'Application'].includes(obj.category)) {
          if (!value.startsWith('*')) {
            value = `*${value}`;
          }
          if (!value.endsWith('*')) {
            value = `${value}*`;
          }
        }    
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
      children: <div>Are you sure you want to delete report ?</div>,
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
    this.setState({
      showIframe: true,
      iframeUrl: model.report_url + "/report?evalId=" + model.report_id, // Assuming `viewUrl` contains the URL to be displayed
    });
    console.log("iframeUrl",  model.report_url + "/report?evalId=" + model.report_id);
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
    const data = {
      id: formData.id,
      purpose: formData.purpose,
      name: formData.name,
      categories: JSON.parse(formData.categories || "[]"),
      custom_prompts: [],
      application_ids: formData.application_ids,
      report_name: formData.report_name
    };

    try {
      this._vState.saving = true;
      let response = await this.props.evaluationStore.reRunReport(data);
      this._vState.saving = false;
      this.runReportModalRef.current.hide();
      f.notifySuccess('Report evaluation submitted');
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
        {!showIframe ? (
            <>
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
            </>
        ) : (
          <div>
            <Button
              variant="contained"
              color="primary"
              onClick={this.handleBack}
              style={{ marginBottom: '10px' }}
            >
              Back
            </Button>
            <iframe
              src={iframeUrl}
              style={{ width: '100%', height: '80vh', border: 'none' }}
              title="View Details"
            />
          </div>
        )}
        <FSModal ref={this.runReportModalRef} dataResolve={this.handleRunSave}>
          <VRunReportForm form={this.evalForm} />
        </FSModal>
      </BaseContainer>
    );
  }
}

CEvaluationReportsList.defaultProps = {
  vName: 'evaluationReports'
}

export default CEvaluationReportsList;