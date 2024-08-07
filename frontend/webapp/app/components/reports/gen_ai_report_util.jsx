import React, { Component, Fragment } from 'react';
import { observer } from 'mobx-react';
import { clone } from 'lodash';
import axios from 'axios';

import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import PublishRoundedIcon from '@material-ui/icons/PublishRounded';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import withStyles from '@material-ui/core/styles/withStyles';
import Tooltip from '@material-ui/core/Tooltip';
import Box from '@material-ui/core/Box';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent'
import FormLabel from '@material-ui/core/FormLabel';

import stores from 'data/stores/all_stores';
import { Checkbox } from 'common-ui/components/filters';
import { FormHorizontal, FormGroupInput, FormGroupSelect2 } from 'common-ui/components/form_fields';
import { SCHEDULE_FOR, DATE_UNITS_GAP } from 'utils/globals';
import { SCHEDULE_TYP } from 'common-ui/utils/globals';
import MScanSchedule from 'common-ui/data/models/m_scan_schedule';
import MReportConfig from 'common-ui/data/models/m_report_config';
import { CommonUtil } from 'common-ui/components/report_util';
import FSModal from 'common-ui/lib/fs_modal';
import { createFSForm } from 'common-ui/lib/form/fs_form';
import VAIScheduleReportForm, { report_form_def } from 'components/reports/v_report_form';
import { DownloadButton, ReportSaveButton, ExportCSVBase, RelativeAbsoluteDateFilter } from 'common-ui/components/v_reporting';

class GenAIReportUtil extends CommonUtil {
	configId = null;
	configObj = null;

	setConfigId = (configId) => {
		this.configId = configId;
	}
	getConfigId() {
		return this.configId;
	}
	getConfig() {
		return this.configObj;
	}
	setConfig = (config) => {
		this.configObj = config;
	}
	collectReportDataFromForm = (form, _vState, reportType = '', saveAs, advancedFilter, includeExcludeQuery) => {
		let data = form.toJSON();
		if (saveAs == 'new') {
			data.id = undefined;
			data.scheduleId = undefined;
		}
		if (!data.id) {
			data.id = undefined;
		}

		// data.scheduledFor = SCHEDULE_FOR.DASHBOARD_REPORT.label;
		// data.lastScheduled = null;
		// data.isAll = !!data.isAll;
		// switch (data.scheduleType) {
		// 	case SCHEDULE_TYPE.ONCE.value:
		// 	case SCHEDULE_TYPE.DAILY.value:
		// 		data.day = undefined;
		// 		data.month = undefined;
		// 		break;
		// 	case SCHEDULE_TYPE.WEEKLY.value:
		// 		data.month = undefined;
		// 		if (data.isAll) {
		// 			data.day = undefined;
		// 		}
		// 		break;
		// 	case SCHEDULE_TYPE.MONTHLY.value:
		// 		if (data.isAll) {
		// 			data.month = undefined;
		// 		}
		// 		break;
		// }
		// let scheduleId = data.scheduleId || undefined;
		let { id, schedulerName, name, description, emailTo, emailMessage, scheduleReport } = data;
		data.id = undefined;
		// data.schedulerName = undefined
		data.name = undefined;
		data.description = undefined;
		// data.emailTo = undefined;
		// data.emailMessage = undefined;
		// data.scheduleId = undefined;
		// data.scheduleReport = undefined;
		data.paramJson = undefined;

		// let scheduleInfo = new MScanSchedule({
		// 	...data, id: scheduleId, name: schedulerName
		// })
		let paramJson = {
			reportType,
			dateAs: this.enableDateRange ? _vState.dateAs : '',
			from: this.params.from,
			to: this.params.to,
			chosenLabel: this.enableDateRange ? this.dateRangeDetail.chosenLabel : '',
			quickDateFilter: _vState.quickDateFilter || '',
			application: _vState.application || ''
		}
		this.addParamsIfHasOwnProperty(paramJson, 'user', _vState);
		this.addParamsIfHasOwnProperty(paramJson, 'application', _vState);
		this.addParamsIfHasOwnProperty(paramJson, 'searchValue', _vState);
		this.addParamsIfHasOwnProperty(paramJson, 'gap', _vState);


		paramJson = JSON.stringify(paramJson);

		let config = new MReportConfig({
			id: id || undefined,
			name,
			description,
			paramJson,
			// emailTo,
			// emailMessage,
			status: data.status,
			// scheduleInfo: scheduleReport ? scheduleInfo : undefined
		});

		return config;
	}

	addParamsIfHasOwnProperty(addToObj = {}, storeFieldName = '', fields = {}, attr = '') {
		if (!attr && storeFieldName) {
			attr = storeFieldName;
		}
		if (fields.hasOwnProperty(attr)) {
			addToObj[storeFieldName] = fields[attr];
		}
		return addToObj;
	}

	fetchConfig() {
		let configId = this.getConfigId();
		if (configId) {
			return stores.shieldAuditsReportsStore.getReport(configId, {
				noCache: true
			});
		}
		return null;
	}

	saveReportConfig(config) {
		if (!config) {
			return;
		}
		if (config.id) {
			return stores.shieldAuditsReportsStore.updateReport(config);
		}

		return stores.shieldAuditsReportsStore.createReport(config);
	}

	resetData() {
		this.resetParams();
		this.resetDateRange();
		this.setConfigId(null);
		this.setConfig(null);
	}

	reloadFilter(refInstance) {
		refInstance = ((refInstance && refInstance.wrappedInstance) || (refInstance))
		if (refInstance) {
			refInstance.reload && refInstance.reload();
		}
	}
	getStringFromSet(data) {
		if (!data instanceof Set) {
			return '';
		}
		return Array.from(data).join(',');
	}

	mergeString = (existing = '', newString = '') => {
		let set = new Set();
		existing && existing.split(',').forEach(e => set.add(e));
		newString && set.add(newString);
		return this.getStringFromSet(set);
	}
}

@observer
class GenAIReportNameWithExportOptions extends Component {
	state = {
		downloadSupport: true,
		saveReportSupport: true,
		exportCSVSupport: false
	}
	componentDidMount() {
		this.checkActionButtonState();
	}

	checkActionButtonState() {
		const { state } = this;
		if (this.props.saveReportSupport != undefined) {
			state.saveReportSupport = this.props.saveReportSupport;
		}
		if (this.props.downloadSupport != undefined) {
			state.downloadSupport = this.props.downloadSupport;
		}
		if (this.props.exportCSVSupport != undefined) {
			state.exportCSVSupport = this.props.exportCSVSupport;
		}
		this.setState(this.state);
	}

	setExcludeDescription(val) {
		this.saveReport && this.saveReport.setExcludeDescription(val);
	}
	render() {
		const { scheduleSupport, collAttr, offSetAttr, downloadCollAttr, exportCollAttr, saveCollAttr, showExportDropdown } = this.props;
		const { _vState, params, dateRangeDetail, data } = this.props.options;
		const { resetFilters, downloadReport, saveReportConfig, exportCSV } = this.props.callbacks;
		return (
			<Card className={`m-b-md ${(_vState.config.name) ? 'card-border-top-primary' : 'card-border-top-warning'}`}>
				<CardContent style={{paddingBottom: '10px', paddingTop: '10px'}}>
					<Grid container spacing={1} className="align-items-center">
						<ReportName collAttr={collAttr} _vState={_vState} onRemoveClick={resetFilters} />
						{this.state.downloadSupport && <DownloadButton collAttr={downloadCollAttr} _vState={_vState} onClick={downloadReport} buttonText={"Download Report"} />}
						{(this.state.exportCSVSupport || this.state.exportDataInventoryCSVSupport) && <ExportCSV collAttr={exportCollAttr} exportDataInventoryCSVSupport={this.state.exportDataInventoryCSVSupport} _vState={_vState} data={data} onExportClick={exportCSV} buttonText={"Export to CSV"} />}
						{this.state.saveReportSupport && <SaveReport collAttr={saveCollAttr} ref={ref => this.saveReport = ref} options={{ _vState, scheduleSupport, params, dateRangeDetail, offSetAttr }} callbacks={{ saveReportConfig }} />}
					</Grid>
				</CardContent>
			</Card>
		)
	}
}

const saveReportStyles = {
	textArea: {
		width: "100%"
	}
}

const addFilterField = ({ fields = {}, attr = '', label = '', filters = [], defaultValue = 'All' }) => {
	if (fields.hasOwnProperty(attr)) {
		let val = (typeof fields[attr] == 'boolean') ? '' + fields[attr] : fields[attr];
		filters.push(
			<div className="m-b-sm" key={attr}>
				<span>{label} </span><span>{val || defaultValue}</span>
			</div>
		)
	}
	return filters;
}

const FiltersToBeSaved = ({ _vState, params = {} }) => {
	let filters = [];
	addFilterField({ label: 'Users:', attr: 'user', fields: _vState, filters });
	addFilterField({ label: 'Application:', attr: 'application', fields: _vState, filters });

	return (
		<Grid container spacing={3} component={Box} padding="0 10px">
			<Grid item sm={12}>
				<FormLabel>Filter Parameter</FormLabel>
				<pre>
					{filters}
				</pre>
			</Grid>
		</Grid>
	)
}
class SaveReportInstance extends Component {
	constructor(props) {
		super(props);
		this.form = createFSForm(report_form_def);
	}
	state = {
		excludeDescription: this.props.options._vState.excludeDescription || ''
	}
	saveAs = '';
	excludeDescription = '';
	resolveForm = () => {
		const { saveReportConfig } = this.props.callbacks;
		this.form.validate().then(() => {
			if (this.form.valid) {
				saveReportConfig(this.form, this.modal, this.saveAs, this.state.excludeDescription);
			}
		})
	}
	export = () => {
		const { dateRangeDetail, _vState } = this.props.options;
		if (dateRangeDetail) {
			_vState.dateAs = dateRangeDetail.chosenLabel == 'Custom Range' ? 'absolute' : _vState.dateAs;
		}
		if (_vState.hasOwnProperty('excludeDescription')) {
			this.setState({ excludeDescription: this.getExcludeDescription() });
		}
		this.form.clearForm();
		if (_vState.config) {
			let scheduleInfo = {};
			if (_vState.config.scheduleInfo) {
				scheduleInfo = clone(_vState.config.scheduleInfo);
				scheduleInfo.schedulerName = scheduleInfo.name;
				scheduleInfo.name = undefined;
				scheduleInfo.scheduleId = scheduleInfo.id;
				scheduleInfo.id = undefined;
			}
			this.form.refresh({
				schedulerName: scheduleInfo.schedulerName,
				scheduleType: scheduleInfo.scheduleType,
				startTime: scheduleInfo.startTime,
				day: scheduleInfo.day,
				month: scheduleInfo.month,
				isAll: scheduleInfo.isAll,
				objectId: scheduleInfo.objectId,
				objectClassType: scheduleInfo.objectClassType,
				scheduleId: scheduleInfo.scheduleId,
				scheduleReport: !!scheduleInfo.scheduleId,
				id: _vState.config.id,
				name: _vState.config.name,
				description: _vState.config.description,
				emailTo: _vState.config.emailTo,
				emailMessage: _vState.config.emailMessage,
				paramJson: _vState.config.paramJson,
				status: _vState.config.status
			});
		}
		this.modal.show();
	}

	setExcludeDescription(val) {
		this.excludeDescription = val;
	}

	getExcludeDescription() {
		return this.excludeDescription;
	}

	render() {
		const { _vState, params, dateRangeDetail, scheduleSupport } = this.props.options;
		const { classes, collAttr } = this.props;
		return (
			<Grid item sm={2} md={1} className='text-right save-caret' {...collAttr}>
				<ReportSaveButton _vState={_vState}
					onSaveClick={() => {
						this.saveAs = '';
						this.export();
					}}
					onSaveAsClick={() => {
						this.saveAs = 'new';
						this.export();
					}}
				/>
				<FSModal ref={ref => this.modal = ref} dataTitle={'Save Report'} dataResolve={this.resolveForm} >
					<VAIScheduleReportForm scheduleSupport={scheduleSupport} form={this.form} />
					<RelativeAbsoluteDateFilter _vState={_vState} dateRangeDetail={dateRangeDetail} />
					{/* _vState.hasOwnProperty('excludeResources') &&
						<FormHorizontal>
							<FormGroupSelect2
								inputColAttr={{ sm: 12, md: 12 }}
								value={_vState.excludeResources}
								label={"Exclude Resource"}
								multiple={true}
								disabled={true}
							/>
							<Grid item component={FormLabel} sm={12} className="m-b-sm">
								<Typography variant="body2">Exclude Description</Typography>
								<TextareaAutosize 
									className={clsx(classes.textArea)}
									placeholder="Exclude Description"
									rowsMin={4}
									value={this.state.excludeDescription}
									onChange={(e) => {
										this.setExcludeDescription(e.target.value);
										this.setState({excludeDescription: e.target.value})
									}}
								/>
							</Grid>
						</FormHorizontal>
					*/}
					<FiltersToBeSaved _vState={_vState} params={params} />
				</FSModal>
			</Grid>
		);
	}
}

const SaveReport = withStyles(saveReportStyles)(SaveReportInstance);

const ReportName = observer(({ collAttr = { sm: 12, md: 9 }, _vState = {}, onRemoveClick = null }) => {
	let header = <Typography component="div" variant="h6" className="break-all scheduled-report-title">{_vState.name}</Typography>;
	if (_vState.config?.name) {
		header = (
			<Fragment>
				<Typography component="div" variant="h6" className="break-all scheduled-report-title">
					{_vState.config.name}
				</Typography>
				<Typography component="div" variant="body2" className="break-all scheduled-report-title">
					{_vState.name}
				</Typography>
			</Fragment>
		)
	}

	return (
		<Grid item {...collAttr}>
			{header}
		</Grid>
	)
});

@observer
class ExportCSV extends ExportCSVBase {
	constructor(props) {
		super(props);
		this.decideExportColumns();
	}

	getCSVColumns() {

	}

	decideExportColumns() {
		const Export_Col = EXPORT_COLUMNS;
		this.exportColums = Object.values(Export_Col).filter(c => {
			if (c.value != 'nonNullCount') {
				return true;
			}
			return false;
		})
	}

	getFsModal = () => {
		const { buttonText, _vState } = this.props;
		return (
			<FSModal ref={ref => this.modal = ref} dataTitle={buttonText} dataResolve={this.resolve} >
				<FormHorizontal>
					<Grid item sm={12}>
						<Grid container spacing={1} alignItems="center">
							<FormGroupInput
								inputColAttr={{ md: 10, sm: 9 }}
								required={true}
								maxLength={12}
								value={this.state.rows}
								label={"No. of Resource"}
								disabled={this.state.allResource}
								data-test="no-of-rows"
								onChange={this.handleChange}
								errMsg={this.state.errMsg}
							>
							</FormGroupInput>
							<Grid item sm={3} md={2}>
								<Checkbox checked={this.state.allResource} labelText='All' onChange={e => {
									this.setState({
										allResource: e.target.checked
									});
								}} />
							</Grid>
							<FormGroupSelect2
								required={true}
								inputColAttr={{ sm: 9, md: 10 }}
								label={"Columns"}
								data={this.getExportColumns()}
								value={this.state.columns}
								labelKey={'label'}
								valueKey={'value'}
								multiple={true}
								onChange={this.handleColumnChange}
								inputProps={{ 'data-test': 'columns' }}
								errMsg={this.state.errMsgColumn}
							>
							</FormGroupSelect2>
							<Grid item sm={3} md={2}>
								<Checkbox checked={this.state.isAllColumns} labelText='All' onChange={e => {
									let isChecked = e.target.checked;
									this.setState({
										isAllColumns: isChecked
									}, () => {
										this.handleColumnChange(isChecked ? this.getAllExportColumns() : '');
									});
								}} />
							</Grid>
						</Grid>
					</Grid>
					<Grid item sm={12}>
						<Grid container spacing={1}>
							<Grid item sm={12} md={12}>
								<Checkbox labelText="Include empty metaname tagged columns" checked={this.state.showEmptyMetaNameTaggedColumns} onChange={e => {
									this.setState({
										showEmptyMetaNameTaggedColumns: e.target.checked
									});
								}} />
								<Tooltip className='bg-white valign-middle' arrow placement="top" title={'Select this checkbox if you want to include those columns which are empty (no data)  but have been metatagged at the column level.'}>
									<InfoOutlinedIcon fontSize="small" />
								</Tooltip>
							</Grid>
							<Grid item sm={12} md={12}>
								<Checkbox labelText="Include empty table" checked={this.state.includeEmptyTable}
									onChange={e => {
										this.setState({
											includeEmptyTable: e.target.checked,
											showEmptyMetaNameTaggedColumns: e.target.checked
										})
									}} />
								<Tooltip className='bg-white valign-middle' arrow placement="top" title={
									<Fragment>
										Select this checkbox if you want to include tables which are empty (no data) but have been metatagged at the table and column level.
										<div className="m-t-xs">
											<b>Note:</b> Selecting this will automatically select empty columns checkbox
										</div>
									</Fragment>
								}
								>
									<InfoOutlinedIcon fontSize="small" />
								</Tooltip>
							</Grid>
							<Grid item sm={12} md={12}>
								<Checkbox labelText="Show only column tags on column" checked={this.state.showOnlyColumnTagsOnColumn} onChange={e => this.setState({ showOnlyColumnTagsOnColumn: e.target.checked })} />
								<Tooltip className='bg-white valign-middle' arrow placement="top" title={'Select this checkbox when you want to show only the metatags done at the column level and skip the metatags tags at the table level.'}>
									<InfoOutlinedIcon fontSize="small" />
								</Tooltip>
							</Grid>
							{this.props.exportDataInventoryCSVSupport &&
								<Grid item sm={12} md={12}>
									<Checkbox labelText="Exclude external table location" checked={this.state.skipExternalTableLocation} onChange={e => this.setState({ skipExternalTableLocation: e.target.checked })} />
									<Tooltip className='bg-white valign-middle' arrow placement="top" title={'Select this checkbox when you want to exclude the table for HDFS resource.'}>
										<InfoOutlinedIcon fontSize="small" />
									</Tooltip>
								</Grid>
							}
							{this.props.exportDataInventoryCSVSupport &&
								<Grid item sm={12} md={12}>
									<Checkbox labelText="Exclude Reviewed Tags" checked={this.state.excludeReviewedTags} onChange={e => this.setState({ excludeReviewedTags: e.target.checked })} />
									<Tooltip className='bg-white valign-middle' arrow placement="top" title={'Select this checkbox to exclude the tags with status Accepted/Rejected.'}>
										<InfoOutlinedIcon fontSize="small" />
									</Tooltip>
								</Grid>
							}
						</Grid>
					</Grid>
				</FormHorizontal>
			</FSModal>
		)
	}
	render() {
		const { buttonText, _vState } = this.props;

		return (
			<Grid item sm={4} md={3}>
				{
					this.props.showButton &&
					<Button
						disabled={_vState.downloading}
						variant={'contained'}
						color={'primary'}
						size={'small'}
						className="pull-right"
						onClick={this.handleExport}>
						<PublishRoundedIcon />{buttonText}
					</Button>
				}
				{this.getFsModal()}
			</Grid>
		)
	}
}

const CSV_COLUMNS = {
	SOURCE: { value: 'source', label: 'source' },
	APPLICATION: { value: 'application', label: 'application' },
	NON_NULL_COUNT: { value: 'nonNullCount', label: 'nonNullCount' },
	CREATE_DATE: { value: 'createDate', label: 'createDate(mm/dd/yy)' },
	UPDATE_DATE: { value: 'updateDate', label: 'updateDate(mm/dd/yy)' },
	SIZE: { value: 'size', label: 'size' },
	TIME: { value: 'time', label: 'time(hh:mm:ss)' },
	EVENT_TIME: { value: 'event_time', label: 'eventTime' },
	USER: { value: 'user', label: 'user' },
	SERVICE: { value: 'service', label: 'service' },
	SERVICE_TYPE: { value: 'serviceType', label: 'serviceType' },
	RESOURCE: { value: 'resource', label: 'resource' },
	ACTION: { value: 'action', label: 'action' },
	RESULT: { value: 'result', label: 'result' },
	ACCOUNT_NAME: { value: 'accountName', label: 'accountName' },
	ACCOUNT_ID: { value: 'accountId', label: 'accountId' },
	TAG: { value: 'tag', label: 'tag' }
}

const EXPORT_COLUMNS = {
	USER: CSV_COLUMNS.USER,
	APPLICATION: CSV_COLUMNS.APPLICATION,
	NON_NULL_COUNT: CSV_COLUMNS.NON_NULL_COUNT,
	CREATE_DATE: CSV_COLUMNS.CREATE_DATE,
	UPDATE_DATE: CSV_COLUMNS.UPDATE_DATE,
	SIZE: CSV_COLUMNS.SIZE
}

const getCustomGap = (dateRangeDetail) => {
	const from = dateRangeDetail.daterange[0];
	const to = dateRangeDetail.daterange[1];
	const days = to.diff(from, 'days');
	if (days <= 2) {
		return DATE_UNITS_GAP.HOUR.VALUE;
	} else if (days > 2 && days < 7) {
		return DATE_UNITS_GAP.DAY.VALUE;
	} else if (days < 30 && days > 7) {
		return DATE_UNITS_GAP.DAY.VALUE;
	} else if (days < 60 && days > 30) {
		return DATE_UNITS_GAP.WEEK.VALUE;
	} else if (days < 365 && days > 60) {
		return DATE_UNITS_GAP.MONTH.VALUE
	} else if (days > 365) {
		return DATE_UNITS_GAP.QUARTER.VALUE;
	} else {
		return DATE_UNITS_GAP.MONTH.VALUE;
	}
}

const getUnitGap = (label, dateRangeDetail) => {
	let gap = DATE_UNITS_GAP.MONTH.VALUE;
	switch (label) {
		case "Today":
		case "Yesterday": gap = DATE_UNITS_GAP.HOUR.VALUE;
			break;
		case "Last 7 Days": gap = DATE_UNITS_GAP.DAY.VALUE;
			break;
		case "This Month":
		case "Last 30 Days":
		case "Last Month": gap = DATE_UNITS_GAP.WEEK.VALUE;
			break;
		case "Last 3 Months":
		case "Last 6 Months": gap = DATE_UNITS_GAP.MONTH.VALUE;
			break;
		case "Custom Range": gap = getCustomGap(dateRangeDetail);
			break;
		default: gap = DATE_UNITS_GAP.MONTH.VALUE;
			break;
	}
	return gap;
}

const cancelApiCall = (cancelTokenMap, uniqKey) => {
	if (cancelTokenMap.has(uniqKey)) {
		const cancelTokens = cancelTokenMap.get(uniqKey);
		cancelTokens.cancel();
	}
}

const getAxiosSourceToken = (cancelTokenMap, uniqKey) => {
	const CancelToken = axios.CancelToken;
	const source = CancelToken.source();
	cancelTokenMap.set(uniqKey, source);
	return source;
}

export {
	GenAIReportUtil,
	GenAIReportNameWithExportOptions,
	ExportCSV,
	getUnitGap,
	cancelApiCall,
	getAxiosSourceToken
}

