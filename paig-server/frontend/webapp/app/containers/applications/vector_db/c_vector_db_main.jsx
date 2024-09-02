import React, { Component, Fragment } from 'react';
import { observable } from 'mobx';
import { observer, inject } from 'mobx-react';

import { Tabs, Tab, Grid, Box } from '@material-ui/core';
import GetAppIcon from '@material-ui/icons/GetApp';
import DeleteIcon from '@material-ui/icons/Delete';

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import { UI_CONSTANTS, FEATURE_PERMISSIONS } from 'utils/globals';
import BaseContainer from 'containers/base_container';
import CVectorDBDetail from 'containers/applications/vector_db/c_vector_db_detail';
import CVectorDBPermissions from 'containers/policies/vector_db/c_vector_db_permissions';
import { TabPanel } from 'common-ui/components/generic_components';
import { AddButtonWithPermission, AddButton, CanDelete } from 'common-ui/components/action_buttons';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';

@inject('vectorDBStore')
@observer
class CVectorDBMain extends Component {
    @observable _vState = {
        model: null,
        loading: true
    }

    @observable tabsState = {
        defaultState: 0
    }

    state = {
        views: []
    }

    views = [{
        title: "Overview",
        view: CVectorDBDetail,
        tab: `${UI_CONSTANTS.VECTOR_DB}.${UI_CONSTANTS.VECTOR_DB}`,
        index: 0,
        testId: 'vector-db-overview-tab'
    }, {
        title: "Permissions",
        view: CVectorDBPermissions,
        tab: `${UI_CONSTANTS.VECTOR_DB}.${UI_CONSTANTS.VECTOR_DB_PERMISSIONS}`,
        index: 1,
        testId: 'vector-db-permissions-tab'
    }]

    constructor(props) {
		super(props);
		this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.VECTOR_DB.PROPERTY);
	}

    componentDidMount() {
        this.filterTabs();
		if (this.props.match.params.id) {
			this.getVectorDBDetails(this.props.match.params.id);
		} else {
		    this._vState.model = {};
			this._vState.loading = false;
		}
    }

	getVectorDBDetails = (id) => {
	    this._vState.loading = true;
        this.props.vectorDBStore.getVectorDBById(id)
            .then((response) => {
                this._vState.model = response;
                this._vState.loading = false;
            }, f.handleError(null, () => {
                this._vState.loading = false;
                this._vState.model = null;
            }));
    }

    componentWillUnmount() {
        let { tabsState } = this;
        let data = JSON.stringify({ tabsState });

        UiState.saveState(this.props._vName, data);
    }

    filterTabs() {
        let { state } = this;
        state.views = this.views;
        if (state.views.length && !this.hasEventKey(state.views, this.tabsState.defaultState)) {
            this.tabsState.defaultState = state.views[0].index;
        }
        this.setState(state);
    }

    hasEventKey(views = [], defaultState = 1) {
        return !!views.find(view => view.index == defaultState);
    }

    handleTabSelect = (key, path) => {
        this.tabsState.defaultState = key;
    }
    
    handleRedirect = () => {
        this.props.history.push('/vector_db');
    }

    handleBackButton = () => {
        this.handleRedirect();
    }
    
    handlePostDelete = () => {
        this.handleRedirect();
    }

    handleDelete = () => {
        f._confirm.confirmDelete({
                children: <Fragment>Are you sure you want to delete <b>{this._vState.model.name}</b> vector DB?</Fragment>,
            }).then((confirm) => {
                this.props.vectorDBStore.deleteVectorDB(this._vState.model.id)
                    .then(() => {
                        f.notifySuccess(`The Vector DB ${this._vState.model.name} deleted successfully`);
                        confirm.hide();
                        this.handlePostDelete();
                    }, f.handleError(null, null, {confirm}));
            }, () => {});
    }

    render() {
        const {state, _vState, handleBackButton, handleTabSelect, getVectorDBDetails}  = this;
        let tabs = [];
        let tabsPane = [];

        if (state.views.length) {
            state.views.forEach((viewObj) => {
                tabs.push(
                    <Tab
                        label={viewObj.title}
                        key={viewObj.index}
                        onClick={(e) => this.handleTabSelect(viewObj.index)}
                        data-testid={viewObj.testId}
                    />
                )
                tabsPane.push(
                    <TabPanel key={viewObj.index} value={this.tabsState.defaultState} index={viewObj.index} p={0} mt="10px" renderAll={false}>
                        <viewObj.view _vState={_vState} handleTabSelect={handleTabSelect} handlePostUpdate={getVectorDBDetails}/>
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
                titleColAttr={{
                    sm: 10,
                    md: 10
                }}
                nameProps={{maxWidth: '100%'}}
                title={(
					<Fragment>
						{_vState.model && 
                            <Box className='ellipsize' component="div" >
                                VectorDB Details - {_vState.model.name}
                            </Box>
                        }
					</Fragment>
				)} 
                headerChildren={
                    this.tabsState.defaultState === 0 && _vState.model?.id
                    ?
                        (
                            <AddButtonWithPermission
                                colAttr={{
                                    xs: 12,
                                    sm: 2,
                                    md: 2
                                }}
                                size="small"
                                variant="outlined"
                                className="m-l-sm pull-right"
                                label={
                                    <Fragment>
                                        <DeleteIcon color="primary" fontSize="inherit" />
                                        &nbsp;Delete
                                    </Fragment>
                                }
                                permission={this.permission}
                                onClick={this.handleDelete}
                            />
                        )
                    : null
                }
            >   
                <div className='m-b-md'>
                    <Tabs indicatorColor="primary" textColor="primary" value={this.tabsState.defaultState} scrollButtons="auto" variant="scrollable" className="tabs-view">
                        {tabs}
                    </Tabs>
                </div>
                    {tabsPane}
            </BaseContainer>
        );
    }
}

CVectorDBMain.defaultProps = {
    view: UI_CONSTANTS.APPLICATIONS,
    _vName: 'c_vector_db_main'
};

export default CVectorDBMain;
