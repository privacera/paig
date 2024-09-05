import React, { Component, Fragment } from 'react';
import { observable } from 'mobx';
import { observer, inject } from 'mobx-react';

import { Tabs, Tab, Grid, Box } from '@material-ui/core';
import GetAppIcon from '@material-ui/icons/GetApp';
import DeleteIcon from '@material-ui/icons/Delete';
import HelpIcon from '@material-ui/icons/Help';
import FeedbackIcon from '@material-ui/icons/Feedback';

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import { UI_CONSTANTS, FEATURE_PERMISSIONS } from 'utils/globals';
import BaseContainer from 'containers/base_container';
import CAIApplicationDetail from 'containers/applications/ai_applications/c_ai_application_detail';
import CAIPermissions from 'containers/policies/ai_policies/c_ai_permissions';
import {findActiveGuideByName, clearGuideTimeout, PENDO_GUIDE_NAME} from 'components/pendo/pendo_initializer';
import { TabPanel } from 'common-ui/components/generic_components';
import { AddButtonWithPermission, AddButton, CanDelete, CustomAnchorBtn } from 'common-ui/components/action_buttons';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';

@inject('aiApplicationStore')
@observer
class CAIApplicationMain extends Component {
    @observable _vState = {
        application: null,
        loading: true
    }

    @observable tabsState = {
        defaultState: 0
    }

    state = {
        views: [],
        guide: null,
        feedbackGuide: null
    }

    views = [{
        title: "Overview",
        view: CAIApplicationDetail,
        tab: `${UI_CONSTANTS.AI_APPLICATIONS}.${UI_CONSTANTS.AI_APPLICATIONS}`,
        index: 0,
        ref: null,
        trackId: 'application-overview-tab'
    }, {
        title: "Permissions",
        view: CAIPermissions,
        tab: `${UI_CONSTANTS.AI_APPLICATIONS}.${UI_CONSTANTS.AI_APPLICATIONS_PERMISSIONS}`,
        index: 1,
        ref: null,
        trackId: 'application-permissions-tab'
    }]

    constructor(props) {
		super(props);
		this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.AI_APPLICATIONS.PROPERTY);
	}

    componentDidMount() {
        this.filterTabs();
        if (this.props.match.params.id) {
			// get application details
			this.getApplicationDetails(this.props.match.params.id);
		} else {
		    this._vState.application = null;
			this._vState.loading = false;
		}
        this.initGuide();
    }
    initGuide = () => {
        findActiveGuideByName(PENDO_GUIDE_NAME.APPLICATION_DETAIL_TOUR).then(guide => {
            this.setState({guide})
        });
        findActiveGuideByName(PENDO_GUIDE_NAME.POLICY_PAGE_FEEDBACK).then(feedbackGuide => {
            this.setState({feedbackGuide});
        });
    }

    getApplicationDetails = (id) => {
	    this._vState.loading = true;
        this.props.aiApplicationStore.getAIApplicationById(id)
            .then((response) => {
                this._vState.application = response;
                this._vState.loading = false;
            }, f.handleError(null, () => {
                this._vState.loading = false;
                this._vState.application = null;
            }));
    }

    componentWillUnmount() {
        clearGuideTimeout(PENDO_GUIDE_NAME.APPLICATION_DETAIL_TOUR);
        clearGuideTimeout(PENDO_GUIDE_NAME.POLICY_PAGE_FEEDBACK);

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
        const obj = this.state.views[key];
        if (path === 'permission' && obj?.ref) {
            window.scrollTo({ top: obj.ref.offsetTop, behavior: 'smooth' })
        }
        this.tabsState.defaultState = key;
    }
    
    handleRedirect = () => {
        this.props.history.push('/ai_applications');
    }

    handleBackButton = () => {
        this.handleRedirect();
    }

    handleDownloadAppConfig = () => {
        let url = this.props.aiApplicationStore.getAIApplicationConfigUrl(this._vState.application.id)
        window.open(url, '_blank');
    }
    
    handlePostDelete = () => {
        this.handleRedirect();
    }

    handleDelete = () => {
        f._confirm.confirmDelete({
                children: <Fragment>Are you sure you want to delete <b>{this._vState.application.name}</b> application?</Fragment>,
            }).then((confirm) => {
                this.props.aiApplicationStore.deleteAIApplication(this._vState.application.id)
                    .then((response) => {
                        f.notifySuccess(`The AI Application ${this._vState.application.name} deleted successfully`);
                        confirm.hide();
                            this.handlePostDelete();
                    }, f.handleError());
            }, () => {});
    }

    render() {
        const {state, _vState, handleBackButton, handleTabSelect, getApplicationDetails}  = this;
        let tabs = [];
        let tabsPane = [];

        if (state.views.length) {
            state.views.forEach((viewObj) => {
                tabs.push(
                    <Tab
                        label={viewObj.title}
                        key={viewObj.index}
                        data-track-id={viewObj.trackId}
                        ref={ref => viewObj.ref = ref}
                        onClick={(e) => this.handleTabSelect(viewObj.index)}
                        data-testid={viewObj.trackId}
                    />
                )
                tabsPane.push(
                    <TabPanel key={viewObj.index} value={this.tabsState.defaultState} index={viewObj.index} p={0} mt="10px" renderAll={false}>
                        <viewObj.view _vState={_vState} handleTabSelect={handleTabSelect} handlePostUpdate={getApplicationDetails}/>
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
                    sm: 6,
                    md: 6
                }}
                nameProps={{maxWidth: '100%'}}
                title={(
					<Fragment>
						{_vState.application && 
                            <Box className='ellipsize' component="div">
                                AI Application Details - {_vState.application.name}
                            </Box>
                        }
					</Fragment>
				)} 
                headerChildren={
                    this.props.match.params.id && this.tabsState.defaultState === 0 && _vState.application? 
                        (
                            <Grid item xs={12} sm={6} md={6}>
                                <div className="pull-right">
                                    {
                                        this.state.guide &&
                                        <CustomAnchorBtn
                                            className="m-r-sm"
                                            tooltipLabel="Application Detail Tour"
                                            data-track-id="application-detail-tour"
                                            icon={<HelpIcon />}
                                            onClick={() => {
                                                pendo.showGuideById(this.state.guide.id);
                                            }}
                                        />
                                    }
                                    <AddButtonWithPermission
                                        size="small"
                                        variant="outlined"
                                        className=""
                                        addCol={false}
                                        permission={this.permission}
                                        label={
                                            <Fragment>
                                                <GetAppIcon fontSize="small" className='m-r-xs'/>
                                                    DOWNLOAD APP CONFIG
                                            </Fragment>
                                        }
                                        data-track-id="download-app-config"
                                        onClick={this.handleDownloadAppConfig}
                                    />
                                    <CanDelete permission={this.permission}>
                                        <AddButton
                                            size="small"
                                            variant="outlined"
                                            className="m-l-sm"
                                            addCol={false}
                                            label={
                                                <Fragment>
                                                    <DeleteIcon color="primary" fontSize="inherit" className='m-r-xs'/>
                                                        Delete
                                                </Fragment>
                                            }
                                            data-track-id="delete-app"
                                            onClick={this.handleDelete}
                                        />
                                    </CanDelete>
                                </div>
                            </Grid>
                        )
                    : null
                }
            >   
                <div className='m-b-md'>
                    <Tabs indicatorColor="primary" textColor="primary" value={this.tabsState.defaultState} scrollButtons="auto" variant="scrollable" className="tabs-view">
                        {tabs}
                        {
                            this.tabsState.defaultState == 1 && this.state.feedbackGuide &&
                            <CustomAnchorBtn
                                size="medium"
                                tooltipLabel="Policy Page Feedback"
                                data-track-id="policy-page-feedback"
                                icon={<FeedbackIcon />}
                                onClick={() => {
                                    pendo.showGuideById(this.state.feedbackGuide.id);
                                }}
                            />
                        }
                    </Tabs>
                </div>
                {/* <Loader isLoading={_vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')} > */}
                    <Fragment>
                        {tabsPane}
                    </Fragment>
                {/* </Loader> */}
            </BaseContainer>
        );
    }
}

CAIApplicationMain.defaultProps = {
    view: UI_CONSTANTS.APPLICATIONS,
    _vName: 'c_ai_applications_main'
};

export default CAIApplicationMain;
