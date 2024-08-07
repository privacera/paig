import React, { Component, Fragment, createRef } from 'react';
import { observable, reaction, action, ObservableMap } from 'mobx';
import { inject } from 'mobx-react';
import { forEach, isEmpty, chunk } from 'lodash';

import { Grid } from '@material-ui/core';

import f from 'common-ui/utils/f';
import { Utils } from 'common-ui/utils/utils';
import { DateRangePickerComponent, InputGroupSelect2 } from 'common-ui/components/filters';
import DashboardUtils from 'utils/dashboard_utils';
import { REPORT_DETAILS, DATE_UNITS_GAP, MESSAGE_RESULT_TYPE, GRAPH_COLOR_PALLET } from 'utils/globals';
import UiState from 'data/ui_state';
import PDFUtil from 'components/reports/reports_pdfUtil';
import { usersLookup, applicationLookup } from 'components/reports/fields_lookup';
import {replaceCurrentUrl} from 'containers/reports/c_reporting';
import { GenAIReportUtil, GenAIReportNameWithExportOptions, getUnitGap, cancelApiCall, getAxiosSourceToken } from 'components/reports/gen_ai_report_util';
import { VMetricData, VSensitiveDataAccess, VUserPrompt, VRepliesPrompt, VSensitiveWordCould, VSensitiveTagsDistribution, VAccessTrendsOverTime } from 'components/reports/v_sensitive_data_report_summary';

@inject('dashboardStore')
export default class CSensitiveDataSummary extends Component {
	@observable _vState = {
		config: "",
		user: '',
		application: '',
		uploadDone: false,
		dateAs: 'relative',
		gap: DATE_UNITS_GAP.MONTH.VALUE,
		name: REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.LABEL,
		sensitiveAccessCount: 0,
		applicationAccessCount: 0,
		sensitiveTagsCount: 0,
		maxQueryCount: 0,
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
	cSensitiveDataAccess = f.initCollection();
	cUserPrompt = f.initCollection();
	cRepliesPrompt = f.initCollection();
	cSensitiveWorldCloud = f.initCollection();
	cSensitiveTagDistribution = f.initCollection();
	cancelTokenMap = new Map();
	appNameColorMap = new ObservableMap();

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
			() => (!f.isLoading(this.cSensitiveDataAccess) && !f.isLoading(this.cUserPrompt) && !f.isLoading(this.cRepliesPrompt) && !f.isLoading(this.cSensitiveWorldCloud) && !f.isLoading(this.cSensitiveTagDistribution)),
			() => {
				if (!f.isLoading(this.cSensitiveDataAccess) && !f.isLoading(this.cUserPrompt) && !f.isLoading(this.cRepliesPrompt) && !f.isLoading(this.cSensitiveWorldCloud) && !f.isLoading(this.cSensitiveTagDistribution)) {
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
		this.fetchUniqUsers();
		this.fetchSensitiveDataAccess();
		this.fetchUserPrompt();
		this.fetchRepliesPrompt();
		this.fetchSensitiveWorldCloud();
		this.fetchSensitiveTagDistribution();
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

	fetchUniqUsers = () => {
		const dateRange = this.getDateRange();
		const params = { groupBy: 'userId', ...dateRange, cardinality: true };
		this.setUserAndApplicationParams(params);
		cancelApiCall(this.cancelTokenMap, 'fetchUniqUsers');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchUniqUsers');
		this.props.dashboardStore.fetchUniqUserIdCounts({ params, cancelToken: source.token })
		.then((resp) => {
			const { userId={} } = resp;
			this._vState.sensitiveTagsCount = userId?.count || 0;
		}, () => this.setLoadingAndDownloading());
	}

	fetchSensitiveDataAccess = () => {
		f.beforeCollectionFetch(this.cSensitiveDataAccess);
		const { _vState } = this;
		const dateRange = this.getDateRange();
		const params = { groupBy: 'result', ...dateRange, interval: _vState.gap };
		this.setUserAndApplicationParams(params);
		cancelApiCall(this.cancelTokenMap, 'fetchSensitiveDataAccess');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchSensitiveDataAccess');
		this.props.dashboardStore.fetchAccessDataCounts({ params, cancelToken: source.token })
			.then((resp) => {
				let models = [];
				let sensitiveDataAccessCount = 0;
				if (!isEmpty(resp[_vState.gap])) {
					forEach(resp[_vState.gap], (obj, epoch) => {
						const o = { name: parseInt(epoch), data: [] };
						const result = obj.result;
						Object.keys(MESSAGE_RESULT_TYPE).forEach(key => {
							const message = MESSAGE_RESULT_TYPE[key];
							const d = { type: message.LABEL, color: message.COLOR, count: 0 }
							if (!isEmpty(result) && !isEmpty(result[message.NAME])) {
								Object.assign(d, { ...result[message.NAME] });
							}
							if ([MESSAGE_RESULT_TYPE.ALLOWED.LABEL, MESSAGE_RESULT_TYPE.MASKED.LABEL].includes(message.LABEL)) {
								sensitiveDataAccessCount += d.count;
							}
							o.data.push(d);
						});
						models.push(o);
					})
				}
				this._vState.sensitiveAccessCount = sensitiveDataAccessCount;
				f.resetCollection(this.cSensitiveDataAccess, models);
				this.setLoadingAndDownloading();
			}, f.handleError(this.cSensitiveDataAccess, this.setLoadingAndDownloading));
	}

	fetchUserPrompt = () => {
		f.beforeCollectionFetch(this.cUserPrompt);
		const dateRange = this.getDateRange();
		const params = { groupBy: 'result', 'includeQuery.requestType': 'prompt', ...dateRange };
		this.setUserAndApplicationParams(params);
		cancelApiCall(this.cancelTokenMap, 'fetchUserPrompt');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchUserPrompt');
		this.props.dashboardStore.fetchUsageCounts({ params, cancelToken: source.token })
			.then((result) => {
				const model = this.getDonutChartData(result);
				f.resetCollection(this.cUserPrompt, [model]);
				this.setLoadingAndDownloading();
			}, f.handleError(this.cUserPrompt, this.setLoadingAndDownloading, {}));
	}

	fetchRepliesPrompt = () => {
		f.beforeCollectionFetch(this.cRepliesPrompt);
		const dateRange = this.getDateRange();
		const params = { groupBy: 'result', 'includeQuery.requestType': 'reply', ...dateRange };
		this.setUserAndApplicationParams(params);
		cancelApiCall(this.cancelTokenMap, 'fetchRepliesPrompt');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchRepliesPrompt');
		this.props.dashboardStore.fetchUsageCounts({ params, cancelToken: source.token })
			.then((result) => {
				const model = this.getDonutChartData(result);
				f.resetCollection(this.cRepliesPrompt, [model]);
				this.setLoadingAndDownloading();
			}, f.handleError(this.cRepliesPrompt, this.setLoadingAndDownloading, {}));
	}

	getDonutChartData = ({ result }) => {
		let totalCount = 0;
		const chartData = [];

		if (result) {
			Object.values(MESSAGE_RESULT_TYPE).forEach(obj => {
				const o = { name: obj.LABEL, y: 0, color: obj.COLOR };
				if (result.hasOwnProperty(obj.NAME)) {
					Object.assign(o, { y: result[obj.NAME]?.count || 0 });
				}
				totalCount += o.y;
				chartData.push(o);
			});
		}

		return { totalCount, chartData };
	}

	setUserAndApplicationParams = (params) => {
		const _params = {};
		const { _vState } = this;
		if (_vState.user) {
			_params['includeQuery.userId'] = _vState.user;
		}
		if (_vState.application) {
			_params['includeQuery.applicationName'] = _vState.application;
		}
		Object.assign(params, _params);
	}

	fetchSensitiveWorldCloud = () => {
		f.beforeCollectionFetch(this.cSensitiveWorldCloud);
		const dateRange = this.getDateRange();
		const params = { groupBy: 'traits', ...dateRange };
		this.setUserAndApplicationParams(params);
		cancelApiCall(this.cancelTokenMap, 'fetchSensitiveWorldCloud');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchSensitiveWorldCloud');
		this.props.dashboardStore.fetchUniqTraitCounts({ params, cancelToken: source.token })
			.then((resp) => {
				let models = [];
				let totalCount = 0;
				if (!isEmpty(resp.traits)) {
					forEach(resp.traits, (obj, key) => {
						totalCount += obj?.count || 0;
						models.push({ name: key, value: obj?.count || 0 });
					})
				}
				f.resetCollection(this.cSensitiveWorldCloud, models);
				this.setLoadingAndDownloading();
			}, f.handleError(this.cSensitiveWorldCloud, this.setLoadingAndDownloading, {}));
	}

	fetchSensitiveTagDistribution = () => {
		f.beforeCollectionFetch(this.cSensitiveTagDistribution);
		const dateRange = this.getDateRange();
		const params = { groupBy: 'traits,applicationName', ...dateRange };
		this.setUserAndApplicationParams(params);
		cancelApiCall(this.cancelTokenMap, 'fetchSensitiveTagDistribution');
		const source = getAxiosSourceToken(this.cancelTokenMap, 'fetchSensitiveTagDistribution');
		this.props.dashboardStore.fetchTraitCounts({ params, cancelToken: source.token })
			.then((result) => {
				let models = DashboardUtils.formatSensitiveDataInApplications(result);
				this.appNameColorMap.clear();
				let countIndex = 0;
				this._vState.maxQueryCount = models.reduce((acc, curr) => {
					curr.graphData.forEach(d => {
						if (!this.appNameColorMap.has(d.name)) {
							let color = GRAPH_COLOR_PALLET[countIndex];
							if (!color) {
								color = GRAPH_COLOR_PALLET[0];
								countIndex = 0;
							}
							d.color = color;
							this.appNameColorMap.set(d.name, color);
							countIndex++;
						} else {
							d.color = this.appNameColorMap.get(d.name);
						}
					});
					if (acc <= curr.queries) {
						acc += curr.queries;
					}
					return acc;
				}, 0);
				this._vState.applicationAccessCount = this.appNameColorMap.size;
				f.resetCollection(this.cSensitiveTagDistribution, models);
				this.setLoadingAndDownloading();
			}, f.handleError(this.cSensitiveTagDistribution, this.setLoadingAndDownloading, {}));
	}

	handleRefresh = () => {
		this.handleFetch();
	}

	setCollectionParams = () => {
		this.cSensitiveDataAccess.params = {};
		this.cUserPrompt.params = {};
		this.cRepliesPrompt.params = {};
		this.cSensitiveWorldCloud.params = {};
		this.cSensitiveTagDistribution.params = {};
	}

	setLoadingAndDownloading = () => {
		if (!f.isLoading(this.cSensitiveDataAccess) && !f.isLoading(this.cUserPrompt) && !f.isLoading(this.cRepliesPrompt) && !f.isLoading(this.cSensitiveWorldCloud) && !f.isLoading(this.cSensitiveTagDistribution)) {
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

			columns = [];

			doc.content.push({
				marginTop: 50,
				alignment: 'center',
				verticalAlign: 'center',
				table: {
					widths: ['33%', '33%', '33%'],
					verticalAlign: 'center',
					body: [
						[
							{ text: [{ text: `Apps with Sensitive Data \n\n`, fontSize: 16 }, { text: this._vState.sensitiveAccessCount, fontSize: 18 }] },
							{ text: [{ text: `Sensitive Data Access Count \n\n`, fontSize: 16 }, { text: this._vState.applicationAccessCount, fontSize: 18 }] },
							{ text: [{ text: `Users Accessing Sensitive Data \n\n`, fontSize: 16 }, { text: this._vState.sensitiveTagsCount, fontSize: 18 }] }
						]
					]
				},
				layout: pdfUtil.getMetricsLayout()
			});

			doc.content.push({
				margin: [3, 50, 0, 0],
				text: [{ text: 'Access Types for Sensitive Data'}]
			});

			columns = [];

			let img = await pdfUtil.getHighChartImageFor(this.sensitiveDataRef.sensitiveDataChart.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [600, 300], pageBreak: 'after' });
			}

			doc.content.push({
				margin: [3, 0, 0, 0],
				columns
			});

			columns = [];

			columns.push({
				margin: [3, 5, 0, 0],
				text: [{ text: 'User Prompts' }]
			});

			columns.push({
				margin: [3, 5, 0, 0],
				text: [{ text: 'Replies To Users ' }]
			});

			doc.content.push({
				margin: [3, 50, 0, 0],
				columns
			});

			columns = [];

			img = await pdfUtil.getHighChartImageFor(this.userPromptRef.userPromptChart.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [250, 300] });
			}

			img = await pdfUtil.getHighChartImageFor(this.repliesUsersRef.repliesPromptChart.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [250, 300] });
			}

			doc.content.push({
				margin: [0, 50, 0, 0],
				columns
			});

			columns = [];
			doc.content.push({
				margin: [3, 60, 0, 0],
				text: [{ text: 'Sensitive Data Word Cloud ' }]
			});

			img = await pdfUtil.getHighChartImageFor(this.sensitiveWordCloudRef.wordCloudChart.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [700, 300], pageBreak: 'after' });
			}

			doc.content.push({
				margin: [0, 0, 0, 0],
				columns
			});

			const barsCollection = await this.getBarChartForPDF(pdfUtil);
			const barsData = chunk(barsCollection, 20);
			columns = [];
			doc.content.push({
				margin: [0, 40, 0, 0],
				text: [{ text: 'Sensitive Data Distribution By App', fontSize: 14 }]
			});
			// Set the Application for references
			const appNameColors = Array.from(this.appNameColorMap.entries());
			const appNames = chunk(appNameColors, 5);
			const legendTable = {
				marginTop: 10,
				marginBottom: 20,
				alignment: 'left',
				verticalAlign: 'center',
				table: {
					widths: ['20%', '20%', '20%', '20%', '20%'],
					verticalAlign: 'center',
					body: appNames.length ? [] : [[]]
				},
				layout: 'noBorders'
			};

			appNames.forEach((appArr) => {
				const [col1, col2, col3, col4, col5] = appArr;
				const arr = [];
				arr.push(...[
					{
						type: "square",
						markerColor: col1?.[1],
						fontSize: 14,
						ul: [
							{text: col1?.[0], fontSize: 12}
						]
					},
					{
						type: "square",
						markerColor: col2?.[1],
						fontSize: 14,
						ul: [
							{text: col2?.[0], fontSize: 12}
						]
					},
					{
						type: "square",
						markerColor: col3?.[1],
						fontSize: 14,
						ul: [
							{text: col3?.[0], fontSize: 12}
						]
					},
					{
						type: "square",
						markerColor: col4?.[1],
						fontSize: 14,
						ul: [
							{text: col4?.[0], fontSize: 12}
						]
					},
					{
						type: "square",
						markerColor: col5?.[1],
						fontSize: 14,
						ul: [
							{text: col5?.[0], fontSize: 12}
						]
					}
				]);
				legendTable.table.body.push(arr);
			});

			doc.content.push(legendTable);

			// Set the tag queries distributions header
			const tableHeaders = [
				{ text: `Tags`, fontSize: 14 },
				{ text: `Queries`, fontSize: 14 },
				{ text: `Distribution`, fontSize: 14 }
			];
			barsData.forEach((barArr, i) => {
				const obj = {
					marginTop: i === 0 ? 10 : 0,
					alignment: 'left',
					verticalAlign: 'center',
					table: {
						widths: ['20%', '12%', '68%'],
						verticalAlign: 'center',
						body: []
					},
					layout: 'noBorders'
				}
				if (i === 0) {
					obj.table.body.push(tableHeaders)
				}
				const rows = this.pushImageToDoc(barArr);
				obj.table.body.push(...rows);
				if (barsData.length - 1 !== i) {
					obj.pageBreak = 'after';
				}
				doc.content.push(obj);
			});

			columns = [];
			columns.push({ text: '\n', pageBreak: 'after', pageOrientation: 'portrait' });

			doc.content.push({
				margin: [3, 0, 0, 0],
				columns
			});

			columns = [];
			doc.content.push({
				margin: [3, 20, 0, 0],
				text: [{ text: 'Access Trend Over Time' }]
			});

			img = await pdfUtil.getHighChartImageFor(this.accessTrendOverTimeRef.accessTrendsChart.chart.current);
			if (img) {
				columns.push({ image: img, "fit": [700, 300] });
			}

			doc.content.push({
				margin: [0, 0, 0, 0],
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

	pushImageToDoc = bars => {
		return bars.map(bar => {
			const [img, obj] = bar;
			return [
				{ text: obj.tag, fontSize: 10 },
				{ text: obj.queries, fontSize: 10 },
				{ image: img, "fit": [400, 30] }
			]
		});
	}

	getBarChartForPDF = async (pdfUtil) => {
		const data = [];
		const models = f.models(this.cSensitiveTagDistribution);
		for (const model of models) {
			const img = await pdfUtil.getHighChartImageFor(this.sensitiveTagDistRef[model.tag + 'ChartRef']);
			if (img) {
				data.push([img, model]);
			}
		}
		return data;
	}

	render() {
		const { _vState, downloadReport, saveReportConfig,
			handleDateChange, cSensitiveDataAccess, cUserPrompt, cRepliesPrompt, cSensitiveWorldCloud, cSensitiveTagDistribution, moment, appNameColorMap } = this;
		const { saveReportSupport, downloadSupport, supportScheduleReport, exportCSVSupport } = this.props;
		const dateRangeDetail = this.reportUtil.getDateRange();
		const params = this.reportUtil.getParams();
		const options = { _vState, params, dateRangeDetail, cSensitiveDataAccess, cUserPrompt, cRepliesPrompt, cSensitiveWorldCloud, cSensitiveTagDistribution, moment, appNameColorMap };

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
					downloadCollAttr={{ sm: 12, md: 4, lg: 3, 'data-track-id': 'download-sensitive-data-summary-report' }} // TODO: [PAIG-2025] Download button move right
					// downloadCollAttr={{ sm: 10, md: 3, lg: 2, 'data-track-id': 'download-sensitive-data-summary-report' }}
					saveCollAttr={{ sm: 2, md: 1, lg: 1, 'data-track-id': 'save-sensitive-data-summary-report' }}
				/>
				<Grid container spacing={3} className="align-items-center">
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
				<VMetricData options={options} />
				<Grid container spacing={3}>
					<Grid item md={12} sm={12}>
						<VSensitiveDataAccess
							ref={ref => this.sensitiveDataRef = ref}
							title="Access Types For Sensitive Data"
							options={options}
						/>
					</Grid>
					<Grid item md={5} sm={12}>
						<Grid container spacing={3}>
							<Grid item md={12} sm={12} data-track-id="sensitive-data-in-prompts">
								<VUserPrompt ref={ref => this.userPromptRef = ref} title="Sensitive Data In Prompts" cUserPrompt={cUserPrompt} />
							</Grid>
							<Grid item md={12} sm={12} data-track-id="sensitive-data-in-replies">
								<VRepliesPrompt ref={ref => this.repliesUsersRef = ref} title="Sensitive Data In Replies" options={options} />
							</Grid>
						</Grid>
					</Grid>
					<Grid item md={7} sm={12}>
						<VSensitiveWordCould ref={ref => this.sensitiveWordCloudRef = ref} title="Sensitive Data Word Cloud" options={options} />
					</Grid>
					<Grid item md={12} sm={12}>
						<VSensitiveTagsDistribution ref={ref => this.sensitiveTagDistRef = ref} title="Sensitive Data Distribution By App" options={options} />
					</Grid>
					<Grid item md={12} sm={12}>
						<VAccessTrendsOverTime	ref={ref => this.accessTrendOverTimeRef = ref} title="Access Trend Over Time"	options={options}	/>
					</Grid>
				</Grid>
			</Fragment>
		)
	}
}
CSensitiveDataSummary.defaultProps = {
  _vName: 'CSensitiveDataSummary',
  reportType: REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.NAME,
  uploadPdf: false
}