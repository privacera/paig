import React, { Component, Fragment, createRef } from 'react';
import { observable, reaction, action } from 'mobx';
import { inject } from 'mobx-react';
import { forEach, isEmpty } from 'lodash';

import { Grid } from '@material-ui/core';

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import { Utils } from 'common-ui/utils/utils';
import PDFUtil from 'components/reports/reports_pdfUtil';
import { replaceCurrentUrl } from 'containers/reports/c_reporting';
import { usersLookup, applicationLookup } from 'components/reports/fields_lookup';
import { DateRangePickerComponent, InputGroupSelect2 } from 'common-ui/components/filters';
import { REPORT_DETAILS, DATE_UNITS_GAP, MESSAGE_RESULT_TYPE, REPORT_GRID_LABELS } from 'utils/globals';
import { VMetricDataGrid, VComplianceReviewTrends, VTopReviewer } from 'components/reports/v_users_who_viewed_content_summary';
import { GenAIReportUtil, GenAIReportNameWithExportOptions, getUnitGap, cancelApiCall, getAxiosSourceToken } from 'components/reports/gen_ai_report_util';

@inject('adminAuditsStore')
export default class CUsersWhoViewedUserContentSummary extends Component {
  @observable _vState = {
    config: "",
    user: '',
    application: '',
    uploadDone: false,
    dateAs: 'relative',
    gap: DATE_UNITS_GAP.MONTH.VALUE,
    name: REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.LABEL,
    adminContentViewCount: 0,
    reviewedMessageCount: 0,
    uniqUserReviewCount: 0,
    downloading: false,
    loading: false,
    isDateEnable: true
  };

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

  moment = Utils.dateUtil.momentInstance();
  reportUtil = new GenAIReportUtil();
  cComplianceViewTrends = f.initCollection();
  cTopComplianceReviewer = f.initCollection();
  cancelTokenMap = new Map();

  constructor(props) {
    super(props);
    this.reportUtil.setDateRange(null, {
      startDate: this.dateRangeDetail.daterange[0],
      endDate: this.dateRangeDetail.daterange[1],
      chosenLabel: 'Last 3 Months'
    });
    this.reportUtil.setDefaultDateRanges(this.dateRangePickerRange());
    this.setCollectionParams();
    this.datePicker = createRef();
    this.disposeReaction = reaction(
      () => (!f.isLoading(this.cComplianceViewTrends) && !f.isLoading(this.cTopComplianceReviewer)),
      () => {
        if (!f.isLoading(this.cComplianceViewTrends) && !f.isLoading(this.cTopComplianceReviewer)) {
          this._vState.loading = false;
          this._vState.downloading = false;
        }
      }
    )
    this.checkForRestore(props)
  }
  componentDidMount() {
    let configId = null;
    if (this.props.match && this.props.match.params && this.props.match.params.configId) {
      configId = this.props.match.params.configId;
    }
    if (!configId && this.props.configId) {
      configId = this.props.configId;
    }
    this.loadConfig(configId);
  }
  componentWillUnmount() {
    if (this.props.configId || this.reportUtil.getConfigId()) {
      UiState.saveState(this.props._vName, undefined);
    } else {
      let { _vState, reportUtil, params } = this;
      let { _vName } = this.props;
      let data = { _vState, reportUtil, params };

      UiState.saveState(_vName, data);
    }
    if (this.disposeReaction) {
      this.disposeReaction();
    }
    delete this.disposeReaction;
    this.cancelTokenMap.clear();
  }
  @action
  async fetchConfig() {
    let configObj = await this.reportUtil.fetchConfig();
    if (configObj) {
      this.reportUtil.setConfig(configObj);
      this._vState.config = configObj;
    }
    return configObj;
  }

  @action
  loadConfig = async (configId) => {
    if (configId) {
      this.reportUtil.setConfigId(configId);
      let configObj = await this.fetchConfig();
      if (configObj && configObj.paramJson) {
        let paramJson = Utils.parseJSON(configObj.paramJson);
        let enableDate = Boolean(paramJson.to && paramJson.from);
        this.reportUtil.enableDate(enableDate)
        this._vState.isDateEnable = enableDate

        this.reportUtil.setDateAs(paramJson.dateAs);
        this._vState.dateAs = paramJson.dateAs || 'relative';
        this.reportUtil.setDateRangeFromParams(paramJson);

        this.reportUtil.setParam('application', this.reportUtil.addQuotesToCommaSeperatedString(paramJson.application));
				this._vState.application = paramJson.application;

				this.reportUtil.setParam('user', this.reportUtil.addQuotesToCommaSeperatedString(paramJson.user));
				this._vState.user = paramJson.user;

        if (this.datePicker.current && this.datePicker.current.setDate) {
          let dateRangeDetail = this.reportUtil.getDateRange();
          this.datePicker.current.setDate({
            chosenLabel: dateRangeDetail.chosenLabel,
            startDate: dateRangeDetail.daterange[0],
            endDate: dateRangeDetail.daterange[1]
          }, true);
        }
      }
    }
    this.handleFetch();
  }

  @action
  restoreState() {
    let data = UiState.getStateData(this.props._vName);
    if (!data) {
      return;
    }
    Object.assign(this, { ...data });
  }

  getConfigId = (props) => {
    let configId = null;
    if (props.match && props.match.params && props.match.params.configId) {
      configId = props.match.params.configId;
    }
    if (!configId && props.configId) {
      configId = props.configId;
    }
    return configId;
  }

  checkForRestore = (props) => {
    if (!this.getConfigId(props)) {
      this.restoreState();
    }
  }

  handleFetch = () => {
    this._vState.loading = true;
    this._vState.downloading = true;
    this.setUnitGaps();
    this.fetchTopReviewer();
    this.fetchReviewMessages();
    this.fetchComplianceTrends();
    this.fetchAdminContentCompliance();
    this.fetchUniqueUserContentReviews();
  }

  fetchCounts = (apiCallName, groupByField) => {
    const params = {
      groupBy: groupByField,
      'includeQuery.objectType': 'SHIELD_AUDIT',
      'includeQuery.action': 'REVIEW',
      ...this.getDateRange(),
      cardinality: true
    };
    this.setUserAndApplicationParams(params);
    cancelApiCall(this.cancelTokenMap, apiCallName);
    const source = getAxiosSourceToken(this.cancelTokenMap, apiCallName);
    return this.props.adminAuditsStore.fetchAdminContentComplianceCounts({ params, cancelToken: source.token })
      .catch(() => this.setLoadingAndDownloading());
  }

  fetchAdminContentCompliance = () => {
    this.fetchCounts('fetchAdminContentCompliance', 'actedByUsername')
      .then(resp => {
        const { actedByUsername = {} } = resp;
        this._vState.adminContentViewCount = actedByUsername.count || 0;
      });
  }

  fetchReviewMessages = () => {
    this.fetchCounts('fetchReviewMessages', 'action')
      .then(resp => {
        const { action = {} } = resp;
        this._vState.reviewedMessageCount = action.count || 0;
      });
  }
  
  fetchUniqueUserContentReviews = () => {
    this.fetchCounts('fetchUniqueUserContentReviews', 'objectName')
      .then(resp => {
        const { objectName = {} } = resp;
        this._vState.uniqUserReviewCount = objectName.count || 0;
      });
  }
  
  fetchComplianceTrends = () => {
    f.beforeCollectionFetch(this.cComplianceViewTrends);
    const models = [];
    const dateRange = this.getDateRange();
    const params = { groupBy: 'action', 'includeQuery.objectType': 'SHIELD_AUDIT', 'includeQuery.action': 'REVIEW', 'interval': this._vState.gap , ...dateRange};
    this.setUserAndApplicationParams(params);
    cancelApiCall(this.cancelTokenMap, 'fetchComplianceTrends');
    const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchComplianceTrends');
    this.props.adminAuditsStore.fetchAdminContentComplianceCounts({ params, cancelToken: source.token })
    .then((resp) => {
      if (!isEmpty(resp[this._vState.gap])) {
        forEach(resp[this._vState.gap], (obj, epoch) => {
          const o = { name: parseInt(epoch), count: 0 };
          const messages = Object.values(obj.action || {});
          o.count = messages.reduce((acc, curr) => acc + (curr?.count || 0), 0);
          models.push(o);
        });
      }
      f.resetCollection(this.cComplianceViewTrends, models);
    }, () => this.setLoadingAndDownloading());

  }

  fetchTopReviewer = () => {
    f.beforeCollectionFetch(this.cTopComplianceReviewer);
    const models = [];
    const params = { groupBy: 'actedByUsername,objectState.result', 'includeQuery.objectType': 'SHIELD_AUDIT', 'includeQuery.action': 'REVIEW', size: 20, ...this.getDateRange()};
    this.setUserAndApplicationParams(params);
    cancelApiCall(this.cancelTokenMap, 'fetchTopReviewer');
    const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchTopReviewer');
    this.props.adminAuditsStore.fetchAdminContentComplianceCounts({ params, cancelToken: source.token })
    .then((resp) => {
      if (!isEmpty(resp)) {
        forEach(resp.actedByUsername, (userObj, username) => {
          const o = { name: username, data: []};
          const result = userObj['objectState.result'];
          Object.keys(MESSAGE_RESULT_TYPE).forEach(key => {
            const message = MESSAGE_RESULT_TYPE[key];
            const d = { type: message.LABEL, count: 0};
            if (!isEmpty(result) && !isEmpty(result[message.NAME]) && [MESSAGE_RESULT_TYPE.ALLOWED.NAME, MESSAGE_RESULT_TYPE.DENIED.NAME, MESSAGE_RESULT_TYPE.MASKED.NAME].includes(message.NAME)) {
              Object.assign(d, { ...result[message.NAME], color: message.COLOR });
              o.data.push(d);
            }
          });
          models.push(o);
        });
      }
      f.resetCollection(this.cTopComplianceReviewer, models);
    }, () => this.setLoadingAndDownloading());
  }

  setUserAndApplicationParams = (params) => {
    const _params = {};
    const { _vState } = this;
    if (_vState.user) {
      _params['includeQuery.actedByUsername'] = _vState.user;
    }
    if (_vState.application) {
      _params['includeQuery.applicationName'] = _vState.application;
    }
    Object.assign(params, _params);
  }

  getDateRange = () => {
    const dateRangeDetail = this.reportUtil.getDateRange();
    const { daterange } = dateRangeDetail;
    const from = Utils.dateUtil.getValueOf(daterange[0]);
    const to = Utils.dateUtil.getValueOf(daterange[1]);
    return {
      fromTime: from,
      toTime: to
    }
  }

  handleRefresh = () => {
    this.handleFetch();
  }

  setCollectionParams = () => {
    this.cComplianceViewTrends.params = {};
    this.cTopComplianceReviewer.params = {};
  }

  setLoadingAndDownloading = () => {
    if (!f.isLoading(this.cComplianceViewTrends) && !f.isLoading(this.cTopComplianceReviewer)) {
      this._vState.loading = false;
      this._vState.downloading = false;
    }
  }

  setUnitGaps = () => {
    const dateRange = this.reportUtil.getDateRange();
    const label = dateRange.chosenLabel;
    const selectedGap = getUnitGap(label, dateRange);
    this._vState.gap = selectedGap;
  }

  handleDateChange = (event, picker) => {
    this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
    this.dateRangeDetail.chosenLabel = picker.chosenLabel;
    this.reportUtil.setDateRange(event, picker);
    this.handleFetch();
  }

  @action
  handleFilterChange = (paramName, val, addQuotes = false) => {
    if (addQuotes) {
      val = this.reportUtil.addQuotesToCommaSeperatedString(val);
    }
    this.reportUtil.setParam('page', undefined);
    this.reportUtil.setParam(paramName, val);
    this.handleFetch();
  }

  handleChange = (val, type) => {
    const value = val || '';
    this._vState[type] = value;
    this.reportUtil.setParam(type, value);
    this.handleFetch();
  }

  saveReportConfig = async (form, modal, saveAs) => {
    let config = this.reportUtil.collectReportDataFromForm(form, this._vState, this.props.reportType, saveAs);
    if (modal && modal.okBtnDisabled) {
      modal.okBtnDisabled(true);
    }
    try {
      config = await this.reportUtil.saveReportConfig(config);
      if (modal && modal.hide) {
        modal.hide();
      }
      f.notifySuccess('Report saved');
      this.reportUtil.setConfigId(config.id);
      this.fetchConfig();
      replaceCurrentUrl(this.props.reportType, config.id);
    } catch(e) {
      if (modal && modal.okBtnDisabled) {
        modal.okBtnDisabled(false);
      }
      f.handleError()(e);
    }
  }

  downloadReport = async () => {
    try {
      const pdfUtil = new PDFUtil();
      const { reportTypeObj } = this.props;
      pdfUtil.setHeader(reportTypeObj.label + " Report");
      pdfUtil.generateSchedulePdfName(this.reportUtil.getConfig());
      let doc = pdfUtil.getDocWithHeaderFooter();
      pdfUtil.setUploadPDf(this.props.uploadPdf);

      pdfUtil.addReportNameAndDesc(doc, this.reportUtil.getConfig());

      let columns = [];

      columns.push({
        margin: [3, 5, 0, 0],
        text: [{ text: 'Time: ', bold: true }, { text: `${this.reportUtil.fromToDateString()}` }]
      });

      doc.content.push({
        margin: [3, 5, 0, 0],
        columns
      });

      columns = [];

      columns.push({
        margin: [3, 5, 0, 0],
        text: [{ text: 'For: ', bold: true }, { text: `${this.reportUtil.replaceQuote(this.reportUtil.getDateRange().chosenLabel)}` }]
      });

      doc.content.push({
        margin: [3, 5, 0, 0],
        columns
      });

      columns = [];

      //users
      columns.push({
        margin: [3, 5, 0, 0],
        text: [{ text: 'Users: ', bold: true }, { text: `${this.reportUtil.replaceQuote(this._vState.user).split(',').join(', ') || 'All'}` }]
      });
      doc.content.push({
        margin: [3, 5, 0, 0],
        columns
      });

      columns = [];

      //applications
      columns.push({
        margin: [3, 5, 0, 0],
        text: [{ text: 'Applications: ', bold: true }, { text: `${this.reportUtil.replaceQuote(this._vState.application).split(',').join(', ') || 'All'}` }]
      });

      doc.content.push({
        margin: [3, 5, 0, 0],
        columns
      });

      doc.content.push({
        marginTop: 50,
        alignment: 'center',
        verticalAlign: 'center',
        table: {
          widths: ['33%', '33%', '33%'],
          verticalAlign: 'center',
          body: [
            [
              { text: [{ text: `${REPORT_GRID_LABELS.ADMIN_CONTENT_COMPLIANCE.LABEL} \n\n`, fontSize: 16 }, { text: this._vState.adminContentViewCount, fontSize: 18 }] },
              { text: [{ text: `${REPORT_GRID_LABELS.REVIEWED_MESSAGE.LABEL} \n\n`, fontSize: 16 }, { text: this._vState.reviewedMessageCount, fontSize: 18 }] },
              { text: [{ text: `${REPORT_GRID_LABELS.UNIQ_USERS.LABEL} \n\n`, fontSize: 16 }, { text: this._vState.uniqUserReviewCount, fontSize: 18 }] }
            ]
          ]
        },
        layout: pdfUtil.getMetricsLayout()
      });

      doc.content.push({
        margin: [3, 50, 0, 0],
        text: [{ text: REPORT_GRID_LABELS.COMPLIANCE_REVIEW_TRENDS.LABEL }]
      });

      columns = [];

      let img = await pdfUtil.getHighChartImageFor(this.complianceReviewTrendRef.complianceChart.chart.current);
      if (img) {
        columns.push({ image: img, "fit": [600, 300], pageBreak: 'after' });
      }

      doc.content.push({
        margin: [3, 10, 0, 0],
        columns
      });


      doc.content.push({
        margin: [3, 30, 0, 0],
        text: [{ text: REPORT_GRID_LABELS.TOP_REVIEWER_CONTENT_COMPLIANCE.LABEL }]
      });

      columns = [];

      img = await pdfUtil.getHighChartImageFor(this.topReviewerRef.topReviewerChart.chart.current);
      if (img) {
        columns.push({ image: img, "fit": [600, 300] });
      }

      doc.content.push({
        margin: [3, 10, 0, 0],
        columns
      });


      let pdfObj = pdfMake.createPdf(doc);
      // if (pdfUtil.shouldUploadPDF()) {
      //   pdfObj.getDataUrl(async (url) => {
      //     let res = await pdfUtil.uploadPdfFromURL(url, this.reportUtil.getConfigId());
      //     this._vState.uploadDone = true;
      //   })
      // } else {
      pdfObj.download(`${pdfUtil.getPDFName()}.pdf`);
      // }
      this._vState.downloading = false;

    } catch (e) {
      this._vState.downloading = false;
      console.log(e, "Error while downloading Report");
    }
  }

  render() {
    const { _vState, cComplianceViewTrends, cTopComplianceReviewer, downloadReport, saveReportConfig,
      handleDateChange, moment } = this;
    const { saveReportSupport, downloadSupport, supportScheduleReport, exportCSVSupport } = this.props;
    const dateRangeDetail = this.reportUtil.getDateRange();
    const params = this.reportUtil.getParams();
    const options = { _vState, cComplianceViewTrends, cTopComplianceReviewer, params, moment, dateRangeDetail };

    return (
      <Fragment>
        <GenAIReportNameWithExportOptions
          saveReportSupport={saveReportSupport}
          downloadSupport={downloadSupport}
          supportScheduleReport={supportScheduleReport}
          exportCSVSupport={exportCSVSupport}
          options={options}
          callbacks={{ saveReportConfig, downloadReport }}
          collAttr={{ sm: 12, md: 8, lg: 9 }}
          downloadCollAttr={{ sm: 10, md: 3, lg: 2, 'data-track-id': 'download-users-who-viewed-content-summary-report' }}
					saveCollAttr={{ sm: 2, md: 1, lg: 1, 'data-track-id': 'save-users-who-viewed-content-summary-report' }}
        />
        <Grid container spacing={3} className="align-items-center">
          <InputGroupSelect2
            colAttr={{ md: 4, sm: 6 }}
            fieldObj={_vState}
            fieldKey={'user'}
            labelKey={'label'}
            valueKey={'value'}
            multiple={true}
            placeholder="Select Users"
            allowCreate={false}
            loadOptions={(searchString, callback) => {
              usersLookup(searchString, callback, 'user');
            }}
            onChange={(value) => this.handleChange(value, 'user')}
          />
          <InputGroupSelect2
            colAttr={{ md: 4, sm: 6 }}
            fieldObj={_vState}
            fieldKey={'application'}
            labelKey={'label'}
            valueKey={'value'}
            multiple={true}
            placeholder="Select GenAI Applications"
            allowCreate={false}
            loadOptions={(searchString, callback) => {
              applicationLookup(searchString, callback, 'application');
            }}
            onChange={(value) => this.handleChange(value, 'application')}
          />
          <DateRangePickerComponent
            ref={this.datePicker}
            colAttr={{ md: 4, sm: 6 }}
            daterange={dateRangeDetail.daterange}
            chosenLabel={dateRangeDetail.chosenLabel}
            handleEvent={handleDateChange}
            showSwitchBox={false}
            showTimeFilter={false}
            ranges={this.dateRangePickerRange()}
            dateRangePickerAttr={{ maxDate: Utils.dateUtil.momentInstance()() }}
          />
        </Grid>
        <VMetricDataGrid options={options} />
        <Grid container spacing={3}>
          <Grid item md={12} sm={12}>
            <VComplianceReviewTrends ref={ref => this.complianceReviewTrendRef = ref} options={options} />
          </Grid>
          <Grid item md={12} sm={12}>
            <VTopReviewer ref={ref => this.topReviewerRef = ref} options={options} />
          </Grid>
        </Grid>
      </Fragment>
    )
  }
}
CUsersWhoViewedUserContentSummary.defaultProps = {
  _vName: 'CUsersWhoViewedUserContentSummary',
  reportType: REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.NAME,
  uploadPdf: false
}