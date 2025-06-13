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
		// Expose this component to child components
		window.parentEvaluationComponent = this;
		
		// Check for filter parameter in URL
		this.handleUrlFilter();
	}
	
	componentWillUnmount() {
		const { tabsState } = this;
		tabsState.clearStateOnUnmount = true;
		const data = JSON.stringify({ tabsState });
		UiState.saveState(this.props._vName, data);
		// Clean up the global reference
		if (window.parentEvaluationComponent === this) {
			delete window.parentEvaluationComponent;
		}
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
	
	handleUrlFilter = () => {
		// Handle both regular URL params and hash-based params
		let filterParam = null;
		let tabParam = null;
		
		// Try regular URL params first
		const urlParams = new URLSearchParams(window.location.search);
		filterParam = urlParams.get('filter');
		tabParam = urlParams.get('tab');
		
		// If not found, try hash-based params
		if ((!filterParam || !tabParam) && window.location.hash.includes('?')) {
			const hashParts = window.location.hash.split('?');
			if (hashParts.length > 1) {
				const hashParams = new URLSearchParams(hashParts[1]);
				if (!filterParam) filterParam = hashParams.get('filter');
				if (!tabParam) tabParam = hashParams.get('tab');
			}
		}
		
		if (filterParam) {
			try {
				// Parse the JSON filter (same pattern as eval reports)
				const filter = JSON.parse(decodeURIComponent(filterParam));
				this._vState.searchFilterValue = filter;
				
				// Check if we should switch to endpoints tab
				if (tabParam === 'endpoints') {
					// Switch to endpoints tab (index 1)
					this.handleTabSelect(1);
				} else {
					// Stay on config tab (index 0) to show the filtered results
					this.handleTabSelect(0);
				}
			} catch (e) {
				console.error('Error parsing filter parameter:', e);
			}
			// Clear the URL parameters after processing
			const newUrl = window.location.pathname + window.location.hash.split('?')[0];
			window.history.replaceState({}, '', newUrl);
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