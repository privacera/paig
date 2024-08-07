import React, { Component } from 'react';
import {observable} from 'mobx';
import {observer} from 'mobx-react';

import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';

import { UI_CONSTANTS } from 'utils/globals';
import UiState from 'data/ui_state';
import BaseContainer from 'containers/base_container';
import CUsers from 'containers/user_management/c_user_management';
import CGroups from 'containers/user_management/c_groups';
import {TabPanel} from 'common-ui/components/generic_components';
import PaperTabsContainer from 'common-ui/components/paper_tabs_container';

@observer
class CUserManagementMain extends Component {
	@observable tabsState = {
		defaultState: 0,
		clearStateOnUnmount: false
	}
	state = {
		views: []
	}
	views = [{
		title: "Users",
		view: CUsers,
		index: 0,
		tab: `${UI_CONSTANTS.USER_MANAGEMENT}.${UI_CONSTANTS.PORTAL_USERS}`,
		trackId: 'users-tab'
	}, {
		title: "Groups",
		view: CGroups,
		index: 1,
		tab: `${UI_CONSTANTS.USER_MANAGEMENT}.${UI_CONSTANTS.PORTAL_GROUPS}`,
		trackId: 'groups-tab'
	}]
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
	
	handleRefresh = () => {
		const { state, tabsState } = this;
		const view = state.views[tabsState.defaultState];
		const viewRef = this[`${view.title}Ref`];
		if (viewRef && viewRef.handleRefresh) {
			viewRef.handleRefresh();
		}
	}
	
	render() {
		const {state, tabsState, handleTabSelect, handleRefresh} = this;
		const callbacks = { handleTabSelect };
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
				  <viewObj.view ref={ ref => this[`${viewObj.title}Ref`] = ref} callbacks={callbacks} tabsState={tabsState}/>
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
				<Tabs className="tabs-view" aria-label="user-management" value={tabsState.defaultState} >
					{tabs}
				</Tabs>
				{tabsPanel}
			  </PaperTabsContainer>
			</BaseContainer>
		)	  
	}
}

CUserManagementMain.defaultProps = {
	view: UI_CONSTANTS.ACCOUNT,
	_vName: "c_user_management_main"
}

export default CUserManagementMain;