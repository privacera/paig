import React, { Component, createRef} from 'react';
import {observable} from 'mobx';
import {observer, inject} from 'mobx-react';

import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';

import { UI_CONSTANTS } from 'utils/globals';
import UiState from 'data/ui_state';
import BaseContainer from 'containers/base_container';
import CEvaluationReportOverview from 'containers/audits/evaluation/c_evaluation_report_overview';
import CEvaluationReportDetails from 'containers/audits/evaluation/c_evaluation_report_details';
import {TabPanel} from 'common-ui/components/generic_components';
import PaperTabsContainer from 'common-ui/components/paper_tabs_container';
import f from 'common-ui/utils/f';
import Box from '@material-ui/core/Box';
import CardContent from '@material-ui/core/CardContent';
import Card from '@material-ui/core/Card';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';
import {AddButton} from 'common-ui/components/action_buttons';
import VRunReportForm from 'components/audits/evaluation/v_run_report_form';
import {evaluation_form_def} from 'components/audits/evaluation/v_evaluation_details_form';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import FSModal from 'common-ui/lib/fs_modal';

@inject('evaluationStore')
@observer
class CEvaluationReportMain extends Component {
	@observable tabsState = {
		defaultState: 0,
		clearStateOnUnmount: false
	}
	@observable _vState = {
		reportData: null,
		loading: true,
		eval_id: null,
		searchFilterValue: []
	}
	runReportModalRef = createRef();
	state = {
		views: []
	}
	views = [{
		title: "OVERVIEW",
		view: CEvaluationReportOverview,
		index: 0,
		tab: `${UI_CONSTANTS.EVALUATION_REPORTS}.${UI_CONSTANTS.EVALUATION_REPORT_OVERVIEW}`,
		trackId: 'eval-report-overview-tab'
	}, {
		title: "DETAILS",
		view: CEvaluationReportDetails,
		index: 1,
		tab:  `${UI_CONSTANTS.EVALUATION_REPORTS}.${UI_CONSTANTS.EVALUATION_REPORT_DETAILS}`,
		trackId: 'eval-report-details-tab'
	}
    ]

	constructor(props) {
		super(props);
		this.evalForm = createFSForm(evaluation_form_def);
	}
	
	componentDidMount() {
		this.fetchAllApi();
		this.filterTabs();
	}
	
	componentWillUnmount() {
		const { tabsState } = this;
		tabsState.clearStateOnUnmount = true;
		const data = JSON.stringify({ tabsState });
		UiState.saveState(this.props._vName, data);
	}
	
	fetchAllApi = () => {
		if (this.props.match.params.eval_id) {
		  this._vState.eval_id = this.props.match.params.eval_id
		  // Get report details
		  this.getReportOverview(this.props.match.params.eval_id);
		  // Get table data
		  // this.getReportDetails(this.props.match.params.eval_id);
		} else {
		  this._vState.reportData = null;
		  this._vState.loading = false;
		}
	};
	
	getReportOverview = (id) => {
		this._vState.loading = true;
		this.props.evaluationStore.fetchEvaluationReportaInfo(id)
		  .then((response) => {
			this._vState.reportData = response;
			this._vState.loading = false;
		  }, f.handleError(null, () => {
			this._vState.loading = false;
			this._vState.reportData = null;
		  }));
	}

	handleRedirect = () => {
		this.props.history.push('/eval_reports');
	}
	
	handleBackButton = () => {
		this.handleRedirect();
	}
	

	filterTabs() {
		const { state } = this;
		state.views = UiState.filterTabs(this.props.view, this.views);
		this.setState(state);
	}
	
	handleTabSelect = (key) => {
		this.tabsState.defaultState = key;
	}
	
	handleRefresh = () => {
		const { state, tabsState } = this;
		const view = state.views[tabsState.defaultState];
		const viewRef = this[`${view.title}Ref`];
		if (viewRef && viewRef.handleRefresh) {
			viewRef.handleRefresh();
		}
	}

	renderTitle = () => {
		const { reportData } = this._vState;
		return reportData ? (
		  <Box className="ellipsize" component="div">
			Evaluation Reports
		  </Box>
		) : null;
	};
	
	handleReRun = () => {
		this.evalForm.clearForm();
		this.evalForm.refresh(this._vState.reportData);
		this.evalForm.model = this._vState.reportData;
		this.evalForm.refresh({name: this._vState.reportData.config_name}); // Set form.name with model.config_name
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
		  this.handleRedirect();
		} catch(e) {
		  this._vState.saving = false;
		  f.handleError()(e);
		}
	}
	
	
	render() {
		const {state, tabsState, handleTabSelect, handleBackButton, _vState} = this;
		const tabs = [];
		const tabsPanel = [];
		if (state.views.length) {
			state.views.forEach(viewObj => {
			  tabs.push(
				<Tab
				  label={viewObj.title}
				  key={viewObj.index}
				  data-track-id={viewObj.trackId}
				  onClick={(e) => handleTabSelect(viewObj.index)}
				  data-testid={viewObj.trackId}
				/>
			  )
			  tabsPanel.push(
				<TabPanel key={viewObj.index} value={tabsState.defaultState} index={viewObj.index} p={0} mt={"10px"} renderAll={false}>
				  <viewObj.view ref={ ref => this[`${viewObj.title}Ref`] = ref} handleTabSelect={handleTabSelect} tabsState={tabsState} history={this.props.history}
					parent_vState={_vState}/>
				</TabPanel>
			  )
			})
		}

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
				title={this.renderTitle()}
			>
			<Card className={`m-b-sm card-border-top-success `} >
				<CardContent style={{paddingBottom: '5px', paddingTop: '5px'}}>
					<Grid container className="align-items-center">
					<Grid item xs={10} sm={10} md={10} lg={10} >
						<Typography variant="button">{_vState.reportData?.name}</Typography>					
					</Grid>
					<AddButton
						onClick={this.handleReRun}
						label="Rerun"
						colAttr={{
						lg: 2,
						md: 2,
						sm: 2,
						xs: 2
						}}
						data-track-id="add-new-eval"
						size='small'
					/>
					</Grid>
				</CardContent>
			</Card>
			   <div>
				<Tabs className="tabs-view" aria-label="eval-security" value={tabsState.defaultState} >
					{tabs}
				</Tabs>
				{tabsPanel}
				</div>
			  <FSModal ref={this.runReportModalRef} dataResolve={this.handleRunSave}>
					<VRunReportForm form={this.evalForm} mode="rerun_report"/>
			 </FSModal>
			</BaseContainer>
		)	  
	}
}

CEvaluationReportMain.defaultProps = {
	view: UI_CONSTANTS.PAIG_LENS,
	_vName: "c_evaluation_report_main"
}

export default CEvaluationReportMain;