import React, { Component } from 'react';
import {observable} from 'mobx';
import {observer} from 'mobx-react';

import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';

import { UI_CONSTANTS } from 'utils/globals';
import UiState from 'data/ui_state';
import BaseContainer from 'containers/base_container';
import CEvaluationConfigList from 'containers/audits/evaluation/c_evaluation_config_list';
import CEvaluationAppsList from 'containers/audits/evaluation/c_evaluation_list_applications';
import {TabPanel} from 'common-ui/components/generic_components';
import PaperTabsContainer from 'common-ui/components/paper_tabs_container';



@observer
class CEvaluationConfigMain extends Component {
	@observable tabsState = {
		defaultState: 0,
		clearStateOnUnmount: false
	}
	@observable _vState = {
		searchFilterValue: []
	}
	
	state = {
		views: []
	}
	views = [{
		title: "CONFIGURATION",
		view: CEvaluationConfigList,
		index: 0,
		tab: `${UI_CONSTANTS.EVALUATION_SECURITY}.${UI_CONSTANTS.EVALUATION_CONFIG}`,
		trackId: 'eval-config-tab'
	}, {
		title: "ENDPOINTS",
		view: CEvaluationAppsList,
		index: 1,
		tab:  `${UI_CONSTANTS.EVALUATION_SECURITY}.${UI_CONSTANTS.EVALUATION_ENDPOINT}`,
		trackId: 'eval-endpoint-tab'
	}
    ]
	constructor(props) {
		super(props);
	}
	
	componentDidMount() {
		this.filterTabs();
	}
	
	componentWillUnmount() {
		const { tabsState } = this;
		tabsState.clearStateOnUnmount = true;
		const data = JSON.stringify({ tabsState });
		UiState.saveState(this.props._vName, data);
	}
	
	filterTabs() {
		const { state } = this;
		state.views = UiState.filterTabs(this.props.view, this.views);
		this.setState(state);
	}
	
	handleTabSelect = (key) => {
		this.tabsState.defaultState = key;
	}
	
	handleManualTabSelect = (key) => {
		// Clear filter when manually switching tabs (this is the key difference from eval reports)
		this._vState.searchFilterValue = [];
		this.handleTabSelect(key);
	}
	
	handleApplicationClick = (applicationName, filter) => {
		// Use the exact same pattern as eval report severity filtering
		this._vState.searchFilterValue = filter;
		// Switch to endpoints tab
		this.handleTabSelect(1);
	}
	
	handleRefresh = () => {
		const { state, tabsState } = this;
		const view = state.views[tabsState.defaultState];
		const viewRef = this[`${view.title}Ref`];
		if (viewRef && viewRef.handleRefresh) {
			viewRef.handleRefresh();
		}
	}
		
	render() {
		const {state, tabsState, handleRefresh, handleTabSelect, _vState} = this;
		const tabs = [];
		const tabsPanel = [];
		
		if (state.views.length) {
			state.views.forEach(viewObj => {
			  tabs.push(
				<Tab
				  label={viewObj.title}
				  key={viewObj.index}
				  data-track-id={viewObj.trackId}
				  onClick={(e) => this.handleManualTabSelect(viewObj.index)}
				  data-testid={viewObj.trackId}
				/>
			  )
			  
			  tabsPanel.push(
				<TabPanel key={viewObj.index} value={tabsState.defaultState} index={viewObj.index} p={0} mt={"10px"} renderAll={false}>
				  <viewObj.view 
				    ref={ ref => this[`${viewObj.title}Ref`] = ref}  
				    tabsState={tabsState} 
				    history={this.props.history} 
				    parent={this}
				    parent_vState={_vState}
				  />
				</TabPanel>
			  )
			})
		}

		return (
			<BaseContainer
				handleRefresh={handleRefresh}
				titleColAttr={{sm: 8, md: 10}}
			>
			  <PaperTabsContainer>
				<Tabs className="tabs-view" aria-label="eval-security" value={tabsState.defaultState} >
					{tabs}
				</Tabs>
				{tabsPanel}
			  </PaperTabsContainer>
			</BaseContainer>
		)	  
	}
}

CEvaluationConfigMain.defaultProps = {
	view: UI_CONSTANTS.PAIG_LENS,
	_vName: "c_evaluation_main"
}

export default CEvaluationConfigMain;