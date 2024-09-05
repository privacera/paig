/* library imports */
import React, { Component, Fragment } from 'react';
import { observer } from 'mobx-react';
import {observable, reaction, action } from 'mobx';
import {clone} from 'lodash';
import isObject from 'lodash/isObject'
import clsx from 'clsx';

import Grid from '@material-ui/core/Grid';
import MenuItem from '@material-ui/core/MenuItem';
import Typography from '@material-ui/core/Typography';
import CardContent from '@material-ui/core/CardContent';
import CircularProgress from '@material-ui/core/CircularProgress';
import Button from '@material-ui/core/Button';
import ArrowDropDownIcon from '@material-ui/icons/ArrowDropDown';
import PublishRoundedIcon from '@material-ui/icons/PublishRounded';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import withStyles from '@material-ui/core/styles/withStyles';
import TextareaAutosize from '@material-ui/core/TextareaAutosize';
import Tooltip from '@material-ui/core/Tooltip';
import FormLabel from '@material-ui/core/FormLabel';
import Card from '@material-ui/core/Card';
import Box from '@material-ui/core/Box';
import FolderIcon from '@material-ui/icons/Folder';
import Link from '@material-ui/core/Link';
import HomeRoundedIcon from '@material-ui/icons/HomeRounded';
import Breadcrumbs from '@material-ui/core/Breadcrumbs';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import Alert from '@material-ui/lab/Alert';

/* other project imports */
import { SCAN_SUMMARY_SOLR_FIELDS, SCAN_TYPE, NA} from 'utils/globals';
import UISidebarTabsUtil from 'utils/ui_sidebar_tabs_util';
import { Loader, PopperMenu, getSkeleton } from 'common-ui/components/generic_components'
import { IBoxMetrics } from 'common-ui/components/widgets';
import { DATE_TIME_FORMATS, FIELDS_STR } from 'common-ui/utils/globals';
import { ICheckRadio, Checkbox, Toggle as ToggleButton } from 'common-ui/components/filters';
import VScheduleReportForm, { schedule_report_form_def } from 'common-ui/components/reports/v_schedule_report_form';
import { FormHorizontal, FormGroupInput, FormGroupSelect2 } from 'common-ui/components/form_fields';
import f from 'common-ui/utils/f';
import { Utils } from 'common-ui/utils/utils';
import { createFSForm } from 'common-ui/lib/form/fs_form';
import FSModal,{Confirm} from 'common-ui/lib/fs_modal';
import {CommandDisplay, CustomAnchorBtn} from 'common-ui/components/action_buttons';

class MetricsCount extends Component {
	//data as list of label value -> [{label: DISCOVERY_METRICS.UNIQUETAGS.label, value: 0}]
	state = {
		data: []
	}
	constructor(props) {
		super(props);
		reaction(
			() => !f.isLoading(this.props.data),
			() => {
				if (!f.isLoading(this.props.data)) {
					this.setData(f.models(this.props.data));
				}
			}
		);
	}
	setData(data = []) {
		const { state } = this
		state.data = data;
		this.setState(state);
	}
	getPdfContent = () => {
		return this.state.data.map(m => ({
			text: [{
				text: `${m.value}\n`,
				fontSize: 20
			}, {
				text:isObject(m.label) ? m.pdfLabel : m.label, fontSize: 10
			}]
		})
		);
	}
	render() {
		const {className, data, colAttr} = this.props;
		return (
			<Loader promiseData={data} loaderContent={getSkeleton('TWO_SLIM_LOADER2')} >
				<Grid container spacing={3} className={className}>
				{
					this.state.data.map((m, i) => {
						return(
							<IBoxMetrics colAttr={colAttr} label={m.label} count={m.value}
							key={typeof m.label == 'object' ? i : m.label} loading={f.isLoading(data)}
							/>
							)
						})
					}
				</Grid>
			</Loader>
		)
	}
}

@observer
class ReportNameWithExportOptions extends Component {
	state = {
		downloadSupport: true,
		saveReportSupport: true,
		exportCSVSupport: false,
		exportAuditCSVSupport: false,
		exportScanSummaryCSVSupport: false,
		exportDataInventoryCSVSupport: false,
		exportComplianceAuditCSV: false,
		exportDataAlertCSV: false,
		exportDataZoneCSV: false
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
		if (this.props.exportAuditCSVSupport != undefined) {
			state.exportAuditCSVSupport = this.props.exportAuditCSVSupport;
		}
		if (this.props.exportScanSummaryCSVSupport != undefined) {
			state.exportScanSummaryCSVSupport = this.props.exportScanSummaryCSVSupport;
		}
		if (this.props.exportDataInventoryCSVSupport != undefined) {
			state.exportDataInventoryCSVSupport = this.props.exportDataInventoryCSVSupport;
		}
		if (this.props.exportComplianceAuditCSV != undefined) {
			state.exportComplianceAuditCSV = this.props.exportComplianceAuditCSV
		}
		if (this.props.exportDataAlertCSV != undefined) {
			state.exportDataAlertCSV = this.props.exportDataAlertCSV;
		}
		if (this.props.exportDataZoneCSV != undefined) {
			state.exportDataZoneCSV = this.props.exportDataZoneCSV;
		}
		this.setState(this.state);
	}

	setExcludeDescription(val) {
		this.savereport && this.savereport.setExcludeDescription(val);
	}
	render() {
		const { scheduleSupport, collAttr, offSetAttr, downloadCollAttr, exportCollAttr, saveCollAttr, showExportDropdown} = this.props;
		const { _vState, params, dateRangeDetail, data } = this.props.options;
		const { resetFilters, downloadReport, saveReportConfig, exportCSV } = this.props.callbacks;
		return (
			<IBOX _vState={_vState}>
				<Grid container spacing={3} className="align-items-center">
					<ReportName collAttr={collAttr} _vState={_vState} onRemoveClick={resetFilters} />
					{this.state.downloadSupport && <DownloadButton collAttr={downloadCollAttr} _vState={_vState} onClick={downloadReport} buttonText={"Download Report"} />}
					{(this.state.exportCSVSupport || this.state.exportDataInventoryCSVSupport) && <ExportCSV collAttr={exportCollAttr} exportDataInventoryCSVSupport={this.state.exportDataInventoryCSVSupport} _vState={_vState} data={data} onExportClick={exportCSV} buttonText={"Export to CSV"} />}
					{this.state.exportScanSummaryCSVSupport && <ExportScanSummaryCSV collAttr={exportCollAttr} _vState={_vState} data={data} onExportClick={exportCSV} buttonText={"Export to CSV"} />}
					{this.state.exportAuditCSVSupport && <ExportAuditCSV collAttr={exportCollAttr} _vState={_vState} data={data} onExportClick={exportCSV} buttonText={"Export to CSV"} />}
					{this.state.exportComplianceAuditCSV && <ExportComplianceAuditCSV _vState={_vState} data={data} onExportClick={exportCSV} buttonText={"Export"} showExportDropdown={false} showButton={false} />}
					{this.state.exportDataAlertCSV && <ExportDataAlertCSV _vState={_vState} data={data} onExportClick={exportCSV} buttonText={"Export to CSV"} showExportDropdown={true} showButton={false}/>}
					{this.state.exportDataZoneCSV && <ExportDataZoneCSV collAttr={exportCollAttr} _vState={_vState} data={data} onExportClick={exportCSV} buttonText={"Export to CSV"} showButton={true} showNoOfResources={false}/>}
					{this.state.saveReportSupport && <SaveReport collAttr={saveCollAttr} ref={ref => this.savereport = ref} options={{ _vState, scheduleSupport, params, dateRangeDetail, offSetAttr }} callbacks={{ saveReportConfig }} />}
				</Grid>
			</IBOX>
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
	const realTimeScanId = {scanId: NA};
	let filters = [];
	if (_vState.filterType == 'advance') {
		addFilterField({ label: 'Resource:', attr: 'resource', fields: _vState, filters });
		addFilterField({ label: 'Advanced Search Query:', attr: 'searchQueryForUI', fields: _vState, filters });
	} else {
		addFilterField({ label: 'Users:', attr: 'user', fields: _vState, filters });
		addFilterField({ label: 'Application:', attr: FIELDS_STR.APP_NAME, fields: _vState, filters });
		addFilterField({ label: 'Tags:', attr: FIELDS_STR.ALL_TAGS_STR, fields: _vState, filters });
		addFilterField({ label: 'Level:', attr: 'level', fields: _vState, filters });
		addFilterField({ label: 'Datazones:', attr: FIELDS_STR.DATAZONE_STR, fields: _vState, filters });
		addFilterField({ label: 'Resource:', attr: 'resource', fields: _vState, filters });
		addFilterField({ label: 'Policy:', attr: 'policyName', fields: _vState, filters });
		addFilterField({ label: 'Alerts For:', attr: 'alertKey', fields: _vState, filters });
		addFilterField({ label: 'Resource Type:', attr: 'resourceListSelected', fields: getResourceTypeLabels(_vState, 'resourceListSelected'), filters });
		addFilterField({ label: 'Exclude Service Users:', attr: 'excludeServiceUsers', fields: _vState, filters });
		addFilterField({ label: 'Access Type:', attr: 'accessType', fields: _vState, filters });
		addFilterField({ label: 'Access Result:', attr: 'result', fields: _vState, filters });
		addFilterField({ label: 'Workspace ID:', attr: 'workspaceId', fields: _vState, filters });
		addFilterField({ label: 'Cluster:', attr: 'cluster', fields: _vState, filters });
		addFilterField({ label: 'Account ID:', attr: 'accountId', fields: _vState, filters });
		//DataZone Report
		addFilterField({ label: 'Tag Attributes:', attr: 'tagAttributes', fields: _vState, filters });
		if(_vState.topTag == 'Select your tags') {
			addFilterField({ label: 'Tags:', attr: 'tags', fields: _vState, filters });
		} else {
			addFilterField({ label: 'Tags:', attr: 'topTag', fields: _vState, filters });
		}
		if(_vState.scanType != undefined && _vState.scanType == "REALTIME"){
			addFilterField({ label: 'Scan ID:', attr: 'scanId', fields: realTimeScanId, filters });
		} else {
			addFilterField({ label: 'Scan ID:', attr: 'scanId', fields: _vState, filters });
		}
		if(_vState.scanType != undefined) {
			addFilterField({ label: 'Scan Type:', attr: 'label', fields: SCAN_TYPE[_vState.scanType] || {label: ''}, filters });
		}
		if(_vState.showLogs != undefined) {
			addFilterField({ label: 'Show Logs:', attr: 'showLogs', fields: _vState, filters });
		}
	}
	if (_vState.searchQuery) {
		addFilterField({ label: 'Search Query:', attr: 'searchQuery', fields: _vState, filters });
	}
	return (
		<Grid container spacing={3} component={Box} padding="0 10px">
			<Grid item sm={12}>
				<Typography variant="body2">Filter Parameter</Typography>
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
		this.form = createFSForm(schedule_report_form_def);
	}
	state ={
		excludeDescription: this.props.options._vState.excludeDescription || ''
	}
	saveAs = '';
	excludeDescription='';
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
		if(_vState.hasOwnProperty('excludeDescription')) {
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
				reportName: _vState.config.reportName,
				description: _vState.config.description,
				emailTo: _vState.config.emailTo,
				emailMessage: _vState.config.emailMessage,
				paramJson: _vState.config.paramJson,
				status: _vState.config.status
			});
		}
		this.modal.show({
			//showSaveAs: !!_vState.config.id
		});
	}

	setExcludeDescription(val) {
		this.excludeDescription = val;
	}

	getExcludeDescription() {
		return this.excludeDescription;
	}
	
	render() {
		const { _vState, params, dateRangeDetail, scheduleSupport } = this.props.options;
		const {classes} = this.props;
		return (
			<Grid item sm={2} md={1} className='text-right save-caret'>
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
					<VScheduleReportForm scheduleSupport={scheduleSupport} form={this.form} />
					<RelativeAbsoluteDateFilter _vState={_vState} dateRangeDetail={dateRangeDetail} />
					{ _vState.hasOwnProperty('excludeResources') &&
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
					}
					<FiltersToBeSaved _vState={_vState} params={params} />
				</FSModal>
			</Grid>
		);
	}
}

const SaveReport = withStyles(saveReportStyles)(SaveReportInstance);

const CSV_COLUMNS = {
	SOURCE: {value: 'source', label: 'source'},
	APPLICATION: {value: 'application', label: 'application'},
	DATAZONE: {value: 'datazone', label: 'datazone'},
	DB: {value: 'db', label: 'db'},
	TABLE: {value: 'table', label: 'table'},
	COLUMN: {value: 'column', label: 'column'},
	NON_NULL_COUNT: {value: 'nonNullCount', label: 'nonNullCount'},
	SCORE: {value: 'score', label: 'score'},
	TAGS: {value: 'tags', label: 'tags'},
	TAG_ATTRIBUTE: {value: 'tagAttributes', label: 'tagAttributes'},
	TAG_REASON: {value: 'tagReason', label: 'tagReason'},
	TAG_STATUS: {value: 'tagStatus', label: 'tagStatus'},
	TAG_STATUS_REASON: {value: 'tagStatusReason', label: 'tagStatusReason'},
	OWNER: {value: 'owner', label: 'owner'},
	LOCATION: {value: 'location', label: 'location'},
	ENCRYPTED: {value: 'encrypted', label: 'encrypted'},
	CRYPTOGRAPHY: {value: 'cryptography', label: 'cryptography'},
	CREATE_DATE: {value: 'createDate', label: 'createDate(mm/dd/yy)'},
	UPDATE_DATE : {value: 'updateDate', label: 'updateDate(mm/dd/yy)'},
	ASPR: {value: 'aspr', label: 'aspr'},
	SIZE: {value: 'size', label: 'size'},
	REVIEWED_BY: {value: 'reviewedBy', label: 'reviewedBy'},
	REVIEWED_ON: {value: 'reviewedOn', label: 'reviewedOn'},
	TIME: {value: 'time', label: 'time(hh:mm:ss)'},
	STATUS: {value: 'status', label: 'status'},
	SCAN_ID: {value: 'scanId', label: 'scanId'},
	RESOURCE: {value: 'resource', label: 'resource'},
	GLOBAL_ID: {value: 'global_id', label: 'scanId'},
	POLICY_ID: {value: 'policyId', label: 'policyId'},
	POLICY_VERSION: {value: 'policyVersion', label: 'policyVersion'},
	POLICY_NAME: {value: 'policyName', label: 'policyName'},
	EVENT_TIME: {value: 'event_time', label: 'eventTime'},
	APPLICATION: {value: 'application', label: 'application'},
	USER: {value: 'user', label: 'user'},
	SERVICE: {value: 'service', label: 'service'},
	SERVICE_TYPE: {value: 'serviceType', label: 'serviceType'},
	RESOURCE: {value: 'resource', label: 'resource'},
	EVENT_TIME: {value: 'eventTime', label: 'eventTime'},
	ACCESS_TYPE: {value: 'accessType', label: 'accessType'},
	ACTION: {value: 'action', label: 'action'},
	RESULT: {value: 'result', label: 'result'},
	ACCESS_ENFORCER: {value: 'accessEnforcer', label: 'accessEnforcer'},
	CLUSTER_NAME: {value: 'clusterName', label: 'clusterName'},
	EVENT_COUNT: {value: 'eventCount', label: 'eventCount'},
	TAGS: {value: 'tags', label: 'tags'},
	CLIENT_IP: {value: 'clientIp', label: 'clientIp'},
	AGENT_HOST_NAME: {value: 'agentHostName', label: 'agentHostName'},
	RESOURCE_TYPE: {value: 'resourceType', label: 'resourceType'},
	ZONE_NAME: {value: 'zoneName', label: 'zoneName'},
	DATA_TYPE: {value: 'dataType', label: 'dataType'},
	ALERT_TIME: {value: 'alertTime', label: 'alertTime'},
	ALERT_LEVEL: {value: 'alertLevel', label: 'alertLevel'},
	ALERT_POLICY: {value: 'policy', label: 'policy'},
	ALERT_FOR: {value: 'alertFor', label: 'alertFor'},
	REASON:{value: 'reason', label: 'reason'},
	ACCOUNT_NAME:{value: 'accountName', label: 'accountName'},
	ACCOUNT_ID:{value: 'accountId',label:'accountId'},
	WORKSPACE:{value:'workspaceName', label:'workspaceName'},
	WORKSPACE_ID: {value: 'workspaceId', label: 'workspaceId' },
	TAG: {value: 'tag', label: 'tag'},
	// TAG_APPLIED_ON: {value: 'tagAppliedOn', label: 'tagAppliedOn'},
	TAG_REVIEWED_ON: {value:'tagReviewedOn', label: 'tagReviewedOn'},
	EXCLUDED_RESOURCE_REASON: {value: 'scanReason', label: 'scanReason'}
}

const EXPORT_COLUMNS = {
	SOURCE: CSV_COLUMNS.SOURCE,
	APPLICATION: CSV_COLUMNS.APPLICATION,
	DATAZONE: CSV_COLUMNS.DATAZONE,
	DB: CSV_COLUMNS.DB,
	TABLE: CSV_COLUMNS.TABLE,
	COLUMN: CSV_COLUMNS.COLUMN,
	NON_NULL_COUNT: CSV_COLUMNS.NON_NULL_COUNT,
	SCORE: CSV_COLUMNS.SCORE,
	TAGS: CSV_COLUMNS.TAGS,
	TAG_ATTRIBUTE: CSV_COLUMNS.TAG_ATTRIBUTE,
	TAG_REASON: CSV_COLUMNS.TAG_REASON,
	TAG_STATUS: CSV_COLUMNS.TAG_STATUS,
	TAG_STATUS_REASON: CSV_COLUMNS.TAG_STATUS_REASON,
	OWNER: CSV_COLUMNS.OWNER,
	LOCATION: CSV_COLUMNS.LOCATION,
	ENCRYPTED: CSV_COLUMNS.ENCRYPTED,
	CRYPTOGRAPHY: CSV_COLUMNS.CRYPTOGRAPHY,
	CREATE_DATE: CSV_COLUMNS.CREATE_DATE,
	UPDATE_DATE: CSV_COLUMNS.UPDATE_DATE,
	ASPR: CSV_COLUMNS.ASPR,
	SIZE: CSV_COLUMNS.SIZE
}

const EXPORT_AUDITS_COLUMNS = {
	REVIEWED_BY: CSV_COLUMNS.REVIEWED_BY,
	APPLICATION: CSV_COLUMNS.APPLICATION,
	DATAZONE: CSV_COLUMNS.DATAZONE,
	DB: CSV_COLUMNS.DB,
	TABLE: CSV_COLUMNS.TABLE,
	COLUMN: CSV_COLUMNS.COLUMN,
	SCORE: CSV_COLUMNS.SCORE,
	TAGS: CSV_COLUMNS.TAGS,
	TAG_ATTRIBUTE: CSV_COLUMNS.TAG_ATTRIBUTE,
	TAG_REASON: CSV_COLUMNS.TAG_REASON,
	TAG_STATUS: CSV_COLUMNS.TAG_STATUS,
	TAG_STATUS_REASON: CSV_COLUMNS.TAG_STATUS_REASON,
	OWNER: CSV_COLUMNS.OWNER,
	LOCATION: CSV_COLUMNS.LOCATION,
	SIZE: CSV_COLUMNS.SIZE,
	REVIEWED_ON: CSV_COLUMNS.REVIEWED_ON
}

const EXPORT_SCAN_SUMMARY_COLUMNS = {
	APPLICATION: CSV_COLUMNS.APPLICATION,
	TIME: CSV_COLUMNS.TIME,
	SCAN_ID: CSV_COLUMNS.SCAN_ID,
	RESOURCE: CSV_COLUMNS.RESOURCE,
	STATUS: CSV_COLUMNS.STATUS,
	EXCLUDED_RESOURCE_REASON: CSV_COLUMNS.EXCLUDED_RESOURCE_REASON
}

const EXPORT_DATA_ALERT_COLUMNS = {
	ALERT_TIME: CSV_COLUMNS.ALERT_TIME,
	ALERT_LEVEL: CSV_COLUMNS.ALERT_LEVEL,
	ALERT_POLICY: CSV_COLUMNS.ALERT_POLICY,
	ALERT_FOR: CSV_COLUMNS.ALERT_FOR,
	APPLICATION: CSV_COLUMNS.APPLICATION,
	USER: CSV_COLUMNS.USER,
	REASON: CSV_COLUMNS.REASON
}

const EXPORT_DATA_DONZE_COLUMNS = {
	DATAZONE: CSV_COLUMNS.DATAZONE,
	APPLICATION: CSV_COLUMNS.APPLICATION,
	CREATE_DATE: CSV_COLUMNS.CREATE_DATE,
	TAG: CSV_COLUMNS.TAG,
	// TAG_APPLIED_ON: CSV_COLUMNS.TAG_APPLIED_ON,
	TAG_STATUS: CSV_COLUMNS.TAG_STATUS,
	TAG_REVIEWED_ON: CSV_COLUMNS.TAG_REVIEWED_ON
}

const EXPORT_DATA_INVENTORY_COLUMNS = {
	SOURCE: CSV_COLUMNS.SOURCE,
	APPLICATION: CSV_COLUMNS.APPLICATION,
	DATAZONE: CSV_COLUMNS.DATAZONE,
	DB: CSV_COLUMNS.DB,
	TABLE: CSV_COLUMNS.TABLE,
	COLUMN: CSV_COLUMNS.COLUMN,
	NON_NULL_COUNT: CSV_COLUMNS.NON_NULL_COUNT,
	SCORE: CSV_COLUMNS.SCORE,
	TAGS: CSV_COLUMNS.TAGS,
	TAG_ATTRIBUTE: CSV_COLUMNS.TAG_ATTRIBUTE,
	TAG_REASON: CSV_COLUMNS.TAG_REASON,
	TAG_STATUS: CSV_COLUMNS.TAG_STATUS,
	TAG_STATUS_REASON: CSV_COLUMNS.TAG_STATUS_REASON,
	OWNER: CSV_COLUMNS.OWNER,
	LOCATION: CSV_COLUMNS.LOCATION,
	ENCRYPTED: CSV_COLUMNS.ENCRYPTED,
	CRYPTOGRAPHY: CSV_COLUMNS.CRYPTOGRAPHY,
	CREATE_DATE: CSV_COLUMNS.CREATE_DATE,
	UPDATE_DATE: CSV_COLUMNS.UPDATE_DATE,
	ASPR: CSV_COLUMNS.ASPR,
	SIZE: CSV_COLUMNS.SIZE,
	SCAN_ID: CSV_COLUMNS.GLOBAL_ID,
	DATA_TYPE: CSV_COLUMNS.DATA_TYPE
}

const EXPORT_COMPLIANCE_AUDITS_COLUMNS = {
	POLICY_ID: CSV_COLUMNS.POLICY_ID,
	POLICY_VERSION: CSV_COLUMNS.POLICY_VERSION,
	RESULT: CSV_COLUMNS.RESULT,
	APPLICATION: CSV_COLUMNS.APPLICATION,
	EVENT_TIME: CSV_COLUMNS.EVENT_TIME,
	USER: CSV_COLUMNS.USER,
	SERVICE: CSV_COLUMNS.SERVICE,
	SERVICE_TYPE: CSV_COLUMNS.SERVICE_TYPE,
	RESOURCE: CSV_COLUMNS.RESOURCE,
	ACCESS_TYPE: CSV_COLUMNS.ACCESS_TYPE,
	ACTION: CSV_COLUMNS.ACTION,
	ACCESS_ENFORCER: CSV_COLUMNS.ACCESS_ENFORCER,
	CLUSTER_NAME: CSV_COLUMNS.CLUSTER_NAME,
	EVENT_COUNT: CSV_COLUMNS.EVENT_COUNT,
	TAGS: CSV_COLUMNS.TAGS,
	CLIENT_IP: CSV_COLUMNS.CLIENT_IP,
	AGENT_HOST_NAME: CSV_COLUMNS.AGENT_HOST_NAME,
	RESOURCE_TYPE: CSV_COLUMNS.RESOURCE_TYPE,
	ZONE_NAME: CSV_COLUMNS.ZONE_NAME,
	ACCOUNT_NAME:CSV_COLUMNS.ACCOUNT_NAME,
	ACCOUNT_ID:CSV_COLUMNS.ACCOUNT_ID,
	WORKSPACE:CSV_COLUMNS.WORKSPACE,
	WORKSPACE_ID: CSV_COLUMNS.WORKSPACE_ID
}

@observer
class ExportCSVBase extends Component {
	defaultRowSize = UISidebarTabsUtil.exportCSVDefaultRow?.();
	defaultShowEmptyMetaNameTaggedColumns = false;
	defaultIncludeEmptyTable = false;
	defaultShowOnlyColumnTagsOnColumn = true;
	state = {
		rows: '',
		errMsg: '',
		columns: '',
		errMsgColumn: '',
		isAllColumns: true,
		showOwner: true,
		owner: '',
		allResource: true,
		showEmptyMetaNameTaggedColumns: this.defaultShowEmptyMetaNameTaggedColumns,
		includeEmptyTable: this.defaultIncludeEmptyTable,
		showOnlyColumnTagsOnColumn: this.defaultShowOnlyColumnTagsOnColumn,
		skipExternalTableLocation: false,
		excludeReviewedTags: false,
		fileType: ''
	}
	exportColums = [];
		
	constructor(props) {
		super(props);
	}
	getExportColumns() {
		return this.exportColums;
	}

	validate = () => {
		this.validateRow();
		if (this.state.columns.trim() == '') {
			this.state.errMsgColumn = 'Required';
		}
		return (!this.state.errMsg && !this.state.errMsgColumn)
	}
	resolve = () => {
		if (this.validate()) {
			const {onExportClick} = this.props;
			const obj = {
				size: this.state.allResource ? this.defaultRowSize : this.state.rows,
				columns: this.state.columns,
				showEmptyMetaNameTaggedColumns: this.state.showEmptyMetaNameTaggedColumns,
				includeEmptyTable: this.state.includeEmptyTable,
				showOnlyColumnTagsOnColumn: this.state.showOnlyColumnTagsOnColumn,
				fileType: this.state.fileType
			};
			if (this.props.exportDataInventoryCSVSupport) {
				obj.skipExternalTableLocation = this.state.skipExternalTableLocation;
				obj.excludeReviewedTags = this.state.excludeReviewedTags;
			}
			onExportClick && onExportClick(obj);
			this.modal.hide();
		} else {
			this.setState(this.state);
		}
	}
	validateRow(rows = this.state.rows) {
		if (this.state.allResource) {
			this.state.errMsg = '';
		} else if (rows == '') {
			this.state.errMsg = 'Required';
		} else if (parseInt(rows) < 1) {
			this.state.errMsg = 'Row should be greater then 0';
		}
	}
	handleChange = (e) => {
		let rows = e.currentTarget.value.replace(/[^0-9]/g, "");
		this.state.errMsg = '';
		this.state.rows = rows;
		this.validateRow(rows);
		this.setState(this.state);
	}
	handleOwnerChange = (e) => {
		this.state.owner = e.currentTarget.value;
		this.setState(this.state);
	}
	handleColumnChange = (val = '') => {
		this.state.errMsgColumn = '';
		this.state.columns = val;
		if (val.trim() == '') {
			this.state.isAllColumns = false;
			this.state.errMsgColumn = 'Required';
		} else if (this.getExportColumns().length == this.state.columns.split(',').length) {
			this.state.isAllColumns = true;
		} else {
			this.state.isAllColumns = false;
		}
		this.state.showOwner = this.state.columns.split(',').includes('owner');
		this.setState(this.state);
	}
	
	handleExport = (fileType, modalTitle) => {
		this.state.rows = '';
		this.state.errMsg = '';
		this.state.errMsgColumn = '';
		this.state.columns = this.getDefaultExportColumns();
		this.state.isAllColumns = this.getExportColumns().length == this.state.columns.split(',').length;
		this.state.showEmptyMetaNameTaggedColumns = this.defaultShowEmptyMetaNameTaggedColumns;
		this.state.includeEmptyTable = this.defaultIncludeEmptyTable;
		this.state.showOnlyColumnTagsOnColumn = this.defaultShowOnlyColumnTagsOnColumn;
		this.state.includeResource = [];
		this.state.excludeResources = [];
		// this.state.showOwner = '';
		// this.state.owner = '';
		this.state.allResource = true;
		this.state.fileType = fileType;
		this.setState(this.state, () => {
			let opts = {
				btnOkText: 'Export',
				btnCancelText: 'Cancel'
			}
			if (modalTitle) {
				opts.title = modalTitle;
			}
			this.modal.show(opts);
		})
	}
	getDefaultExportColumns = () => {
		const {props = {}} = this;
		// const defaultExportColumns = [];
		let defaultUnselectColumn = [EXPORT_COLUMNS.TAG_ATTRIBUTE.value, EXPORT_COLUMNS.SOURCE.value];
		let defaultExportColumns = this.getExportColumns().filter(c => {
			let showColumn = true
			if (props.allColumns) {
				const found = props.allColumns.find(column=> column.csvColumnName === c.value);
				showColumn = found ? found.isSelected : false;
			}
			return !defaultUnselectColumn.includes(c.value) && showColumn
		}).map(c => c.value);
		return	defaultExportColumns.join(',');
	}
	getAllExportColumns = () => {
		return this.getExportColumns().map(c => c.value).join(',');
	}
}
ExportCSVBase.defaultProps = {
	showButton: true
}
@observer
class ExportCSV extends ExportCSVBase {
	constructor(props) {
		super(props);
		this.decideExportColumns();
	}
	
	getCSVColumns() {
		
	}

	decideExportColumns() {
		let isNullCountEnable = UISidebarTabsUtil.isClassificationNonNullCountEnable?.();
		const Export_Col = this.props.exportDataInventoryCSVSupport ? EXPORT_DATA_INVENTORY_COLUMNS : EXPORT_COLUMNS;
		this.exportColums = Object.values(Export_Col).filter(c => {
			if (c.value != 'nonNullCount' || isNullCountEnable) {
				return true;
			}
			return false;
		})
	}

	getFsModal = () => {
		const { buttonText, _vState } = this.props;
		return(
			<FSModal ref={ref => this.modal = ref} dataTitle={buttonText} dataResolve={this.resolve} >
				<FormHorizontal>
					<Grid item sm={12}>
						<Grid container spacing={1} alignItems="center">
								<FormGroupInput
								inputColAttr={{ md: 10, sm: 9}}
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
								<Checkbox labelText="Show only column tags on column" checked={this.state.showOnlyColumnTagsOnColumn} onChange={e => this.setState({showOnlyColumnTagsOnColumn: e.target.checked})} />
								<Tooltip className='bg-white valign-middle' arrow placement="top" title={'Select this checkbox when you want to show only the metatags done at the column level and skip the metatags tags at the table level.'}>
									<InfoOutlinedIcon fontSize="small" />
								</Tooltip>
							</Grid>
							{this.props.exportDataInventoryCSVSupport && 
								<Grid item sm={12} md={12}>
									<Checkbox labelText="Exclude external table location" checked={this.state.skipExternalTableLocation} onChange={e => this.setState({skipExternalTableLocation: e.target.checked})} />
									<Tooltip className='bg-white valign-middle' arrow placement="top" title={'Select this checkbox when you want to exclude the table for HDFS resource.'}>
										<InfoOutlinedIcon fontSize="small" />
									</Tooltip>
								</Grid>
							}
							{this.props.exportDataInventoryCSVSupport && 
								<Grid item sm={12} md={12}>
									<Checkbox labelText="Exclude Reviewed Tags" checked={this.state.excludeReviewedTags} onChange={e => this.setState({excludeReviewedTags: e.target.checked})} />
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

class ExportCSVByScanId extends ExportCSV {
	showNoResultModal = () => {
		this.noResultModal.show({title: "There are no scan results for this request.",btnOkText:'Ok', showCloseButton: false}).then(confirm => {
			confirm.hide();
		});
	}
	render() {
		const {hasResult = true} = this.props;

		return (
			<div className="inline-block">
				<CustomAnchorBtn
					tooltipLabel="Export CSV"
					color="primary"
					className="m-l-xs"
					icon={<PublishRoundedIcon fontSize="inherit"/>}
					onClick={hasResult ? this.handleExport: this.showNoResultModal}
				/>
				{this.getFsModal()}
				<Confirm ref={ref => this.noResultModal = ref} />
			</div>
		)
	}
}

ExportCSVByScanId.defaultProps = {
	buttonText: "Export to CSV"
}

@observer
class ExportAuditCSV extends ExportCSVBase {
	constructor(props) {
		super(props);
		this.decideExportColumns();
	}
	decideExportColumns() {
		this.exportColums = Object.values(EXPORT_AUDITS_COLUMNS)
	}
	render() {
		const { buttonText, _vState, collAttr={}, columnDropListComponent, showExportDropdown, showNoOfResources = true } = this.props;
		return (
			<Grid item md={2} sm={4} {...collAttr}>
				{
					this.props.showButton &&
					<Button disabled={_vState.downloading} variant={'contained'} color="primary" size={'small'} className="pull-right"
						onClick={() => this.handleExport.call(this, null, buttonText)}
					>
						<PublishRoundedIcon />{buttonText}
					</Button>
				}
				{
					showExportDropdown &&
					<PopperMenu
						buttonType="Button"
						buttonProps={{disabled: _vState.downloading}}
						label={buttonText}
						renderCustomMenus={(handleClose) => {
							return([
								<MenuItem key="1" variant={'primary'} onClick={() => {
									this.handleExport.call(this, 'csv');
									handleClose();
								}}>Export as CSV</MenuItem>,
								<MenuItem key="2" variant={'primary'} onClick={() => {
									this.handleExport.call(this, 'json');
									handleClose();
								}}>Export as JSON</MenuItem>
							])
						}}
					/>
				}
				{columnDropListComponent}
				<FSModal ref={ref => this.modal = ref} dataTitle={'Export'} dataResolve={this.resolve} >
					<Box>
						<FormHorizontal alignItems="center">
							{showNoOfResources && <React.Fragment><FormGroupInput
								// inputColAttr={{ sm: 6, md: 7 }}
								inputColAttr={{ sm: 9, md: 10 }}
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
								<Grid item sm={3} md={2} className="nomargin-top-check">
								<Checkbox checked={this.state.allResource} labelText='All' onChange={e => {
									this.setState({
										allResource: e.target.checked
									});
								}} />
							</Grid></React.Fragment> 
							}
							{this.state.fileType !== 'json' &&  <React.Fragment><FormGroupSelect2
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
							<Grid item sm={3} md={2} className="nomargin-top-check">
									<Checkbox checked={this.state.isAllColumns} labelText='All' onChange={e => {
										let isChecked = e.target.checked;
										this.setState({
											isAllColumns: isChecked
										}, () => {
											this.handleColumnChange(isChecked ? this.getAllExportColumns() : '');
										});
									}} />
								</Grid>
							</React.Fragment> }
						</FormHorizontal>
					</Box>
				</FSModal>
			</Grid>
		)
	}
}

class ExportScanSummaryCSV extends ExportAuditCSV {
	constructor(props) {
		super(props);
		this.decideExportColumns();
	}
	decideExportColumns() {
		this.exportColums = Object.values(EXPORT_SCAN_SUMMARY_COLUMNS);
	}
}

class ExportComplianceAuditCSV extends ExportAuditCSV {
	constructor(props) {
		super(props);
		this.decideExportColumns();
	}
	decideExportColumns() {
		this.exportColums = Object.values(EXPORT_COMPLIANCE_AUDITS_COLUMNS);
		if(UISidebarTabsUtil.isRangerEnable?.()) {
			this.exportColums.splice(1, 0, CSV_COLUMNS.POLICY_NAME);
		};
	}
}

class ExportDataAlertCSV extends ExportAuditCSV {
	constructor(props) {
		super(props);
		this.decideExportColumns();
	}
	decideExportColumns() {
		this.exportColums = Object.values(EXPORT_DATA_ALERT_COLUMNS);
	}
}

class ExportDataZoneCSV extends ExportAuditCSV {
	constructor(props) {
		super(props);
		this.decideExportColumns();
	}
	decideExportColumns() {
		this.exportColums = Object.values(EXPORT_DATA_DONZE_COLUMNS);
	}
}

const ReportSaveButton = observer(({ _vState, onSaveClick, onSaveAsClick }) => {
	let returnVal = null;
	if (_vState.config) {
		returnVal =  (
			<PopperMenu
				buttonType="Button"
				buttonProps={{disabled: _vState.downloading}}
				label={<Fragment>Save<ArrowDropDownIcon /></Fragment>}
				menuOptions={[{label: 'Save', onClick: onSaveClick}, {label: 'Save As', onClick: onSaveAsClick}]}
			/>
		);
	} else {
			returnVal = <Button disabled={_vState.downloading} variant="contained" color={'primary'} size={'small'} onClick={onSaveClick}>Save</Button>
	}
	return returnVal;
});

const IBOX = observer(({ _vState, children }) => {
	return (
		<Card className={`m-b-md ${(_vState.config.reportName) ? 'card-border-top-primary' : 'card-border-top-warning'}`}>
			<CardContent style={{paddingBottom: '10px', paddingTop: '10px'}}>
				{children}
			</CardContent>
		</Card>
	)
});

const ReportName = observer(({ collAttr = { sm: 6, md: 9 }, _vState = {}, onRemoveClick = null }) => {
	let header = <Typography component="div" variant="h5" className="scheduled-report-title">{_vState.name}</Typography>;
	if (_vState.config && _vState.config.reportName) {
		header = (
			<Typography component="div" variant="h5" className="break-all scheduled-report-title">
			{_vState.name} - {_vState.config.reportName}
			</Typography>
		)
	}
	return (
		<Grid item {...collAttr}>
			{header}
		</Grid>
	)
});

const getResourceTypeLabels = (_vState, attr) => {
	if (!_vState[attr]) {
		return _vState;
	}
	return {
		[attr]: getResourceTypeValueByAttr({resource: _vState[attr], label: 'LABEL'})
	};
}

const getResourceTypeValueByAttr = ({resource='', label='FIELD_NAME', returnString=true}) => {
	const resources = resource.split(',');
	const resourceTypes = [];
	resources.forEach(val => {
		const value = val.trim();
		const resource = SCAN_SUMMARY_RESOURCE_STATUS_LIST.find(r => (r.FIELD_NAME == value || r.LABEL == value));
		if (resource) {
			resourceTypes.push(resource[label]);
		}
	});
	return returnString ? resourceTypes.join(', ') : resourceTypes;
}

@observer
class DownloadButton extends Component{
	@observable _vState = {
    downloadInProgress: false
  };
	constructor(props){
		super(props);
		this.disposeReaction = reaction(
			() => (props && props._vState.downloading),
			() => {
				if (!props._vState.downloading && this._vState.downloadInProgress) {
					this._vState.downloadInProgress=false
				}
			}
		);
	}

	componentWillUnmount() {
		// dispose the reaction method
		if (this.disposeReaction) {
				this.disposeReaction();
		}
		delete this.disposeReaction;
	}

	render(){
		const {_vState = {}, collAttr = { sm: 4, md: 2 }, pullRight = true, className = '', buttonProps = {}, buttonText, onClick = null} = this.props;
		return (
			<Grid item {...collAttr}>
				<Button id="download" variant="contained" color={'primary'} size={'small'} className={`${pullRight ? 'pull-right' : ''} ${className}`} onClick={(e) => {
					_vState.downloading = true;
					this._vState.downloadInProgress=true;
					setTimeout(function () {
						onClick && onClick(e);
					}, 0)
				}} disabled={_vState.downloading} {...buttonProps}>
					{this._vState.downloadInProgress &&
						<CircularProgress size={14} thickness={4} value={100} variant="indeterminate" style={{ color: '#ffffff', className: 'm-r-xxs' }}/>
					}
					{buttonText}
				</Button>
			</Grid>
		);
	}
}


const ReportCardView = withStyles({
	reportCard: {
		height: "100%"
	}
})(({ report, onSelect, classes }) => {
	return (
		<Grid item md={6} xs={12}>
			<Card classes={{root: classes.reportCard}}>
				<CardContent>
					<Typography gutterBottom variant="h6" color="textSecondary">
						{report.label}
					</Typography>
					<Typography gutterBottom variant="body2" color="textSecondary" component="p">
						{report.description}
					</Typography>
					<a onClick={e => onSelect && onSelect(report.type)}>View or Edit Report</a>
				</CardContent>
			</Card>
		</Grid>
	)
})

const getCustomSelection = (dateRangeDetail) => {
    const from = dateRangeDetail.daterange[0];
    const to = dateRangeDetail.daterange[1];
    const days = to.diff(from, 'days');
    if (days < 7) {
      return ["+1DAY"];
    } else if (days < 30 && days > 7) {
      return ["+1DAY", "+7DAY"];
    } else if (days < 60 && days > 30) {
      return ["+7DAY", "+1MONTH"];
    } else if (days < 90 && days > 60) {
      return ["+1MONTH", "+3MONTH"];
    } else if (days > 90) {
      return ["+1MONTH", "+3MONTH", "+6MONTH"];
    } else {
      return ["+1MONTH", "+3MONTH"];
    }
  }

const getSelections = (label, dateRangeDetail) => {
	let selections = [];
	switch(label) {
	  case "Today": selections = ["+12HOURS", "+1DAY"];
	    break;
	  case "Yesterday":  selections = ["+12HOURS", "+1DAY"];
	    break;
	  case "Last 7 Days":  selections = ["+1DAY"];
	    break;
	  case "Last 30 Days": selections = ["+7DAY"];
	    break;
	  case "This Month": selections = ["+7DAY"];
	    break;
	  case "Last Month": selections = ["+7DAY"];
	    break;
	  case "Last 3 Months" : selections = ["+1MONTH"];
	    break;
	  case "Last 6 Months": selections = ["+1MONTH", "+3MONTH"];
	    break;
	  case "Custom Range": selections = getCustomSelection(dateRangeDetail);
	    break;
	  default: selections = ["+1MONTH", "+3MONTH"];
	    break;
	}
	return selections;
}

const ToggleView = observer(({ _vState, children }) => {
	let view = null;
	if (_vState) {
		if (_vState.filterType == 'basic') {
			view = children[0] || null;
		} else if (_vState.filterType == 'advance') {
			view = children[1] || null;
		}
	}
	return view;
});

const InputCheckbox = observer(function InputCheckbox({ _vState, onChange }) {
	const handleChange = action(() => {
		_vState.filterType = _vState.filterType == 'advance' ? 'basic' : 'advance';
	})
	return (
		<div className="checkbox-container m-t-sm m-b-sm pull-right">
			<input type="checkbox" name="checkbox1" data-test="advanceSearch" className="checkbox-custom" checked={_vState.filterType == 'advance' ? "checked" : ""}
				onChange={onChange || handleChange}
			/>
			<label htmlFor="checkbox1" className="checkbox-custom-label"></label>Switch to Advanced Search
		</div>
	)
})

const Toggle = observer(function Toggle({ label='Query Filters', _vState, onChange }) {
	const handleChange = action(() => {
		_vState.filterType = _vState.filterType == 'advance' ? 'basic' : 'advance';
	});
	return (
		<div className="m-t-xxs m-b-sm inline-block">
			<ToggleButton containerClassName="noClass" label={label} fields={_vState} attr={'groupPartFiles'} onChange={onChange || handleChange} checked={_vState.filterType == 'advance' ? 'checked' : ''} />
		</div>
	)
});

const BreadCrumb = observer(function BreadCrumb({options, callbacks, colAttr={}}) {
    const {_vState} = options;
    const {getUserInput} = callbacks;
    let paths = [];
    _vState.currentPath.map((path, i) => {
        let p = path;
        if(i == 0) {
            p = <FolderIcon fontSize="small" color="action" />;
        }
        return paths.push(<Link className="file-breadcrumb" key={i} onClick={() => _vState.handleBreadCrumbPathClick(i, path)}>{p}</Link>)
    });

    return (
        <div className="breadcrumb-buttons">
            <div className="breadcrumb-copy-button inline-block">
                <CommandDisplay id={_vState.appCode} command={getUserInput()} commandDisplayProps={{}} showCommand={false}
                    anchorClass='MuiSvgIcon-root MuiSvgIcon-colorPrimary MuiSvgIcon-fontSizeInherit'
                />
            </div>
            <div>
                {paths}
            </div>
        </div>
    )
})

class FileView extends Component {
    constructor(props) {
        super(props);
        this.state = {
            fileName: '',
            fileTxt: '',
            loading: true,
            isDataTrim: false
        }
        reaction(
            () => props.file && f.isLoading(props.file),
            () => {
                if (props.file && !f.isLoading(props.file)) {
                    const model = f.models(props.file)[0];
                    let name = '';
                    let isDataTrim = false;
                    if (model && model.file) {
                        name = model.file.name;
                        isDataTrim =  model.isDataTrim;
                    }
                    this.setState({ fileName: name, fileTxt: (model && model.file) || null, loading: false, isDataTrim });
                }
            }
          )
    }
    handleChange = e => {
        this.setState({fileTxt: e.target.value});
    }
    getInfoMsg = () => {
        return (
            <Alert severity="info">
                <strong>Note:</strong> Please download the file to see the whole content of the file.
            </Alert>
        );
    }
    render() {
        const {fileTxt, loading, isDataTrim} = this.state;
        const {editable} = this.props;
        const txt = fileTxt && (typeof fileTxt === "string" ? fileTxt : JSON.stringify(fileTxt, null, 4));
        return (
            <Loader isLoading={loading}  loaderContent={getSkeleton('TEXT_LOADER')} >
                <div className="file-view">
                    <Box mb={2}>{isDataTrim && this.getInfoMsg()}</Box>
                    {   editable 
                        ?   <textarea className={'full-wh-textarea'} value={txt} onChange={this.handleChange} />
                        :   <pre>{txt || "No Data"}</pre>
                    }
                </div>
            </Loader>
        )
    }
}
FileView.defaultProps = {
    editable: false
}

const FIELDS_CONSTANT = {
	APPLICATION: { NAME: 'Application', LABEL: 'Application' },
	TAGS: { NAME: 'Tags', LABEL: 'Tags' },
	DATAZONE: { NAME: 'Datazone', LABEL: 'Datazone' },
	DATAZONE_OWNER: { NAME: 'Datazone Owner', LABEL: 'Datazone Owner' },
	DEST_DATAZONE: { NAME: 'Datazone', LABEL: 'Datazone' },
	LEVEL: { NAME: 'Level', LABEL: 'Level' },
	ALERT_FOR: { NAME: 'Alert For', LABEL: 'Alert For' },
	POLICY: { NAME: 'Policy', LABEL: 'Policy' },
	TAG_ATTRIBUTE: { NAME: 'Tag Attribute', LABEL: 'Tag Attribute' },
	SCAN_ID: { NAME: 'Scan Id', LABEL: 'Scan Id' },
	EXCLUDE_RESOURCE: {NAME: 'Exclude Resource', LABEL: 'Exclude Resource'},
	SCAN_TYPE: {NAME: 'Scan Type', LABEL: 'Scan Type'},
	ACCESS: {NAME: 'Access Type', LABEL: 'Access Type'},
	RESULT: {NAME: 'Access Result', LABEL: 'Access Result'},
	WORKSPACE_ID: {NAME: 'Workspace ID', LABEL: 'Workspace ID'},
	CLUSTER: {NAME: 'Cluster', LABEL: 'Cluster'},
	ACCOUNT_ID: {NAME: 'Account ID', LABEL: 'Account ID'}
}

  const RelativeAbsoluteDateFilter = observer(function RelativeAbsoluteDateFilter({ _vState, dateRangeDetail }) {
	if (!dateRangeDetail || !dateRangeDetail.daterange || !dateRangeDetail.chosenLabel) {
		return null;
	}
	const isDateEnabled = !_vState.isDateEnable ? _vState.isDateEnable : true;
	let showRelaticeFilter = dateRangeDetail.chosenLabel != 'Custom Range';
	let label = '';//`(${dateRangeDetail.chosenLabel})`
	let date = (<div>{Utils.dateUtil.getTimeZone(dateRangeDetail.daterange[0], DATE_TIME_FORMATS.DATE_FORMAT)} <b>TO</b> {Utils.dateUtil.getTimeZone(dateRangeDetail.daterange[1], DATE_TIME_FORMATS.DATE_FORMAT)} {showRelaticeFilter ? '' : label}</div>);
	return (
		<Grid container spacing={3} style={{padding: '0px 10px'}}>
			<Grid item sm={12} md={12}>
				<Typography variant="body2">Time</Typography>
				<Box>
					<Box>
						{
							showRelaticeFilter && isDateEnabled &&
							<ICheckRadio label={dateRangeDetail.chosenLabel} value={'relative'} checked={_vState.dateAs == 'relative' ? 'checked' : ''}
								onChange={(e) => _vState.dateAs = e.target.value}
							/>
						}
					</Box>
					<Box>
						{ 
							isDateEnabled &&
							<ICheckRadio label={date} value={'absolute'} checked={_vState.dateAs == 'absolute' ? 'checked' : ''}
								onChange={(e) => _vState.dateAs = e.target.value}
							/>
						}
					</Box>
					<Box>
						{
							!isDateEnabled &&
							<div className="m-t-2 m-b-sm">Date Filter Not Applied</div>
						}
					</Box>
				</Box>
			</Grid>
		</Grid>
	)
})

const BreadCrumbCloud = observer(function BreadCrumbCloud({options, callbacks, labelOptions=null, colAttr={}}) {
    const {_vState} = options;
    const {getUserInput} = callbacks;
    let paths = [];
    _vState.currentPath.map((path, i) => {
        let p = path;
        if(i == 0) {
            p = <HomeRoundedIcon color="action" fontSize="small" />;
        }
        return paths.push(<Link key={i} onClick={() => _vState.handleBreadCrumbPathClick(i, path)}>{p}</Link>)
    });
    return (
            <Grid item {...colAttr}>
                <Box display={'flex'} justifyContent='space-between' className="breadcrumbs-small p-w-15">
                    <Breadcrumbs separator={<NavigateNextIcon fontSize="small" className="m-t-xs" />} aria-label="breadcrumb">
                        {paths}
                    </Breadcrumbs>
                    {
                        labelOptions && <Box mt={1}>{labelOptions}</Box>
                    }
                </Box>
            </Grid>
    )
})

const SCAN_SUMMARY_RESOURCE_STATUS_LIST = [SCAN_SUMMARY_SOLR_FIELDS.TAGGED_RESOURCE, SCAN_SUMMARY_SOLR_FIELDS.UN_TAGGED_RESOURCE, SCAN_SUMMARY_SOLR_FIELDS.FAILED_RESOURCE, SCAN_SUMMARY_SOLR_FIELDS.EXCLUDED_RESOURCE, SCAN_SUMMARY_SOLR_FIELDS.DELETED_RESOURCE, SCAN_SUMMARY_SOLR_FIELDS.LISTING_FAILED_RESOURCE];

export {
	MetricsCount,
	ReportNameWithExportOptions,
	ReportCardView, 
    ToggleView, 
    InputCheckbox, 
    Toggle, 
    ExportCSV,
    DownloadButton, 
    ExportScanSummaryCSV,
	ExportAuditCSV, 
    ExportComplianceAuditCSV, 
    ExportDataAlertCSV, 
    getSelections, 
    ExportCSVByScanId, 
    ExportDataZoneCSV,
	BreadCrumb,
	FileView,
	FIELDS_CONSTANT,
	RelativeAbsoluteDateFilter,
	getResourceTypeValueByAttr,
	BreadCrumbCloud,
	ReportSaveButton,
	ExportCSVBase
}