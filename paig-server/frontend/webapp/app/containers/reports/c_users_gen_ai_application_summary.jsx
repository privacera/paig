import React, { Component, Fragment, createRef } from 'react';
import { observable, reaction, action } from 'mobx';
import { inject } from 'mobx-react';
import { forEach, isEmpty } from 'lodash';

import { Grid } from '@material-ui/core';

import { REPORT_DETAILS, DATE_UNITS_GAP } from 'utils/globals';
import UiState from 'data/ui_state';
import f from 'common-ui/utils/f';
import { Utils } from 'common-ui/utils/utils';
import PDFUtil from 'components/reports/reports_pdfUtil';
import { usersLookup, applicationLookup } from 'components/reports/fields_lookup';
import { DateRangePickerComponent, InputGroupSelect2 } from 'common-ui/components/filters';
import {replaceCurrentUrl} from 'containers/reports/c_reporting';
import { GenAIReportUtil, GenAIReportNameWithExportOptions, getUnitGap, cancelApiCall, getAxiosSourceToken } from 'components/reports/gen_ai_report_util';
import { UserByApplicationChart, TopUsersChart, ActivityTrends } from 'components/reports/v_users_gen_ai_application_summary';

@inject('dashboardStore')
export default class CUsersGenAIApplicationSummary extends Component {
	@observable _vState = {
		config: "",
		searchValue: '',
		user: '',
		application: '',
		uploadDone: false,
		dateAs: 'relative',
		gap: DATE_UNITS_GAP.MONTH.VALUE,
		name: REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.LABEL,
		downloading: false,
		loading: false,
		isDateEnable: true
	};

	moment = Utils.dateUtil.momentInstance();
	reportUtil = new GenAIReportUtil();
	cUserByApplication = f.initCollection();
	cTopUsers = f.initCollection();
	cActivityTrends = f.initCollection();
	cancelTokenMap = new Map();
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
		this.reportUtil.setDateRange(null, {
			startDate: this.dateRangeDetail.daterange[0],
			endDate: this.dateRangeDetail.daterange[1],
			chosenLabel: 'Last 3 Months'
		});
		this.reportUtil.setDefaultDateRanges(this.dateRangePickerRange());
		this.setCollectionParams();
		this.datePicker = createRef();
		this.disposeReaction = reaction(
			() => (!f.isLoading(this.cUserByApplication) && !f.isLoading(this.cTopUsers) && !f.isLoading(this.cActivityTrends)),
			() => {
				if (!f.isLoading(this.cUserByApplication) && !f.isLoading(this.cTopUsers) && !f.isLoading(this.cActivityTrends)) {
					this._vState.loading = false;
					this._vState.downloading = false;
				}
			}
		)
		this.checkForRestore(props)
	}

	setCollectionParams = () => {
		this.cUserByApplication.params = {};
		this.cTopUsers.params = {};
		this.cActivityTrends.params = {};
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

	handleRefresh = () => {
		this.handleFetch();
	}

	handleFetch = () => {
		this._vState.loading = true;
		this._vState.downloading = true;
		this.setUnitGaps();
		this.fetchUserByApplication();
		this.fetchTopUsers();
		this.fetchActivityTrends();
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

	fetchUserByApplication = async () => {
		const { _vState } = this;
		const dateRange = this.getDateRange();
		const params = { groupBy: "applicationName,userId", cardinality: true, ...dateRange };
		if (_vState.user) {
			params["includeQuery.userId"] = _vState.user;
		}
		if (_vState.application) {
			params["includeQuery.applicationName"] = _vState.application;
		}
		f.beforeCollectionFetch(this.cUserByApplication);
		cancelApiCall(this.cancelTokenMap, 'fetchUserByApplication');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchUserByApplication');
		try {
			const data = await this.props.dashboardStore.fetchAppNameByUserIdCounts({ params, cancelToken: source.token });
			this.setUserByAppData(data);
		} catch (e) {
			console.error("Failed to get users by application.", e);
			f.handleError(this.cUserByApplication)(e);
			this.setLoadingAndDownloading();
		}
	}

	setUserByAppData = (res = {}) => {
		let models = [];
		if (!isEmpty(res.applicationName)) {
			forEach(res.applicationName, (obj, name) => {
				const o = { name, count: 0 };
				if (obj.userId) {
					const counts = Object.values(obj.userId);
					Object.assign(o, { count: counts.reduce((acc, curr) => { return acc += (curr?.count || curr) }, 0) });
				}
				models.push(o);
			})
		}
		f.resetCollection(this.cUserByApplication, models);
		this.setLoadingAndDownloading();
	}

	fetchTopUsers = async () => {
		const { _vState } = this;
		const dateRange = this.getDateRange();
		const params = { groupBy: "userId", size: 10, ...dateRange };
		if (_vState.user) {
			params["includeQuery.userId"] = _vState.user;
		}
		f.beforeCollectionFetch(this.cTopUsers);
		cancelApiCall(this.cancelTokenMap, 'fetchTopUsers');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchTopUsers');
		try {
			const data = await this.props.dashboardStore.fetchTopUserIdCounts({ params, cancelToken: source.token });
			this.setTopUserData(data);
		} catch (e) {
			console.error("Failed to get top users", e);
			f.handleError(this.cTopUsers)(e);
			this.setLoadingAndDownloading();
		}
	}

	setTopUserData = (res = {}) => {
		let models = [];
		if (!isEmpty(res.userId)) {
			forEach(res.userId, (obj, name) => {
				models.push({ name, ...obj });
			});
		}
		f.resetCollection(this.cTopUsers, models);
		this.setLoadingAndDownloading();
	}

	fetchActivityTrends = async () => {
		const { _vState } = this;
		const dateRange = this.getDateRange();
		f.beforeCollectionFetch(this.cActivityTrends);
		const params = { groupBy: "tenantId", ...dateRange, interval: this._vState.gap };
		if (_vState.user) {
			params["includeQuery.userId"] = _vState.user;
		}
		if (_vState.application) {
			params["includeQuery.applicationName"] = _vState.application;
		}
		try {
			cancelApiCall(this.cancelTokenMap, 'fetchActivityTrends');
			const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchActivityTrends');
			const data = await this.props.dashboardStore.fetchActivityTrendCounts({ params, cancelToken: source.token });
			this.setActivityTrendsData(data);
		} catch (e) {
			console.error("Failed to get activity trends", e);
			f.handleError(this.cActivityTrends)(e);
			this.setLoadingAndDownloading();
		}
	}

	setUnitGaps = () => {
		const dateRange = this.reportUtil.getDateRange();
		const label = dateRange.chosenLabel;
		const selectedGap = getUnitGap(label, dateRange);
		this._vState.gap = selectedGap;
	}

	setActivityTrendsData = (res = {}) => {
		const { gap } = this._vState;
		const models = [];
		if (!isEmpty(res[gap])) {
			forEach(res[gap], (obj, epoch) => {
				const name = parseInt(epoch);
				const o = { name, count: 0 };
				if (!isEmpty(obj.tenantId)) {
					const counts = Object.values(obj.tenantId);
					Object.assign(o, { count: counts.reduce((acc, curr) => { return acc += (curr?.count || curr) }, 0) });
				}
				models.push(o);
			})
		}
		f.resetCollection(this.cActivityTrends, models);
		this.setLoadingAndDownloading();
	}

	setLoadingAndDownloading = () => {
		if (!f.isLoading(this.cUserByApplication) && !f.isLoading(this.cTopUsers) && !f.isLoading(this.cActivityTrends)) {
			this._vState.loading = false;
			this._vState.downloading = false;
		}
	}

	handleDateChange = (event, picker) => {
		this.dateRangeDetail.daterange = [picker.startDate, picker.endDate];
		this.dateRangeDetail.chosenLabel = picker.chosenLabel;
		this.reportUtil.setDateRange(event, picker);
		this.setUnitGaps();
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

	handleInputChange = (e) => {
		let value = e.target.value;
		this._vState.searchValue = value || "";
		this.handleFilterChange('searchValue', value, false);
	}

	handleEnterPress = (value, e) => {
		if (value) {
			this._vState.searchValue = value;
		}
		this.handleFilterChange('searchValue', value, false);
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
			let params = this.reportUtil.getParams() || {};

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

			//application
			columns.push({
				margin: [3, 5, 0, 0],
				text: [{ text: 'User: ', bold: true }, { text: `${this.reportUtil.replaceQuote(this._vState.user).split(',').join(', ') || 'All'}` }]
			});
			if (columns.length) {
				doc.content.push({
					margin: [3, 5, 0, 0],
					columns
				});
			}

			columns = [];

			//application
			columns.push({
				margin: [3, 5, 0, 0],
				text: [{ text: 'Application: ', bold: true }, { text: `${this.reportUtil.replaceQuote(this._vState.application).split(',').join(', ') || 'All'}` }]
			});
			if (columns.length) {
				doc.content.push({
					margin: [3, 5, 0, 0],
					columns
				});
			}

			columns = [];

			let img = await pdfUtil.getHighChartImageFor(this.userByAppChartRef.userByAppChart.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [600, 300], pageBreak: 'after' });
			}

			doc.content.push({
				margin: [3, 50, 0, 0],
				columns
			});

			columns = [];

			img = await pdfUtil.getHighChartImageFor(this.topUserChartRef.topUsersChartRef.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [600, 300] });
			}

			doc.content.push({
				margin: [3, 50, 0, 0],
				columns
			});

			columns = [];

			img = await pdfUtil.getHighChartImageFor(this.activityTrendsChatRef.activityTrendsChartRef.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [600, 300] });
			}

			doc.content.push({
				margin: [3, 50, 0, 0],
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
		const { _vState, downloadReport, saveReportConfig, handleInputChange, handleEnterPress, handleRefresh,
			handleDateChange, cUserByApplication, cTopUsers, cActivityTrends, moment } = this;
		const { saveReportSupport, downloadSupport, supportScheduleReport, exportCSVSupport } = this.props;
		const dateRangeDetail = this.reportUtil.getDateRange();
		const params = this.reportUtil.getParams();
		const options = { _vState, params, dateRangeDetail, cUserByApplication, cTopUsers, cActivityTrends, moment };
		const callbacks = {};

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
					downloadCollAttr={{ sm: 12, md: 4, lg: 3, 'data-track-id': 'download-user-app-summary-report' }} // TODO: [PAIG-2025] Download button move right
					// downloadCollAttr={{ sm: 10, md: 3, lg: 2, 'data-track-id': 'download-user-app-summary-report' }}
					saveCollAttr={{ sm: 2, md: 1, lg: 1, 'data-track-id': 'save-user-app-summary-report' }}
				/>
				<Grid container spacing={3} className="align-items-center">
					{/* <Grid item md={4} sm={12}>
						<Grid container spacing={0} className="align-items-center">
							<RefreshButton colAttr={{ md: 'auto' }} pullLeft={true} onClick={handleRefresh} />
							<SearchField 
								colAttr={{md: 'auto', className: "flex-grow-2"}}
								ref={ref => this.searchField = ref} 
								initialValue={_vState.searchValue} 
								placeholder="Search"
								onChange={handleInputChange}
								onEnter={handleEnterPress}
								showSearchFilter = {false}
								showSearchInfo = {false}
								showSearchIcon={true}
							/>
							
						</Grid>
					</Grid> */}
					<InputGroupSelect2
						colAttr={{ md: 4, sm: 6 }}
						fieldObj={_vState}
						fieldKey="user"
						labelKey="label"
						valueKey="value"
						multiple={true}
						placeholder="Select Users"
						allowCreate={false}
						loadOptions={(searchString, callback) => {
							usersLookup(searchString, callback, 'user');
						}}
						onChange={(value) => this.handleChange(value, 'user')}
						data-track-id="select-users"
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
						data-track-id="select-application"
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
				<Grid container spacing={3}>
					<Grid item md={5} sm={12}>
						<UserByApplicationChart ref={ref => this.userByAppChartRef = ref} title="Users By Applications" options={options} />
					</Grid>
					<Grid item md={7} sm={12}>
						<TopUsersChart ref={ref => this.topUserChartRef = ref} title="Top 10 Users" options={options} callbacks={callbacks} />
						<ActivityTrends ref={ref => this.activityTrendsChatRef = ref} title="Activity Trends" options={options} callbacks={callbacks} />
					</Grid>
				</Grid>
			</Fragment>
		)
	}
}
CUsersGenAIApplicationSummary.defaultProps = {
  _vName: 'UserGenAIApplicationSummary',
  reportType: REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME,
  uploadPdf: false
}