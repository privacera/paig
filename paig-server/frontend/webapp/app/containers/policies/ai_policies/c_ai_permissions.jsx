import React, {Component, Fragment} from 'react';
import {action, observable} from 'mobx';
import {inject, observer} from 'mobx-react';
import {withRouter} from 'react-router';

import { Grid, Paper, Box }  from "@material-ui/core";

import BaseContainer from 'containers/base_container';
import UiState from 'data/ui_state';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import f from 'common-ui/utils/f';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import CAiApplicationAccessForm from 'containers/policies/ai_policies/c_ai_application_access_form';
import CAiApplicationAccessContentRestriction from 'containers/policies/ai_policies/c_ai_application_access_content_restriction';

@inject('aiPoliciesStore', 'sensitiveDataStore')
@observer
class CAIPermissions extends Component {
    @observable _vState = {
        allPermissionPolicy: null,
        loading: true
    }
    constructor(props) {
        super(props)

        this.cPolicies = f.initCollection();
        this.cSensitiveData = f.initCollection();

        this.cPolicies.params = {
            size: 999,//DEFAULTS.DEFAULT_PAGE_SIZE,
            sort: 'createTime,desc'
        }

        this.cSensitiveData.params = {
            size: 999
        };

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.AI_POLICIES.PROPERTY);
    }
    componentDidMount() {
        this.fetchSensitiveData();
        this.fetchPolicies();
    }
    fetchSensitiveData = () => {
        f.beforeCollectionFetch(this.cSensitiveData);
        this.props.sensitiveDataStore.fetchSensitiveData({
            params: this.cSensitiveData.params
           
        }).then(f.handleSuccess(this.cSensitiveData), f.handleError(this.cSensitiveData));
    }
    @action
    fetchPolicies = async () => {
        const {id} = this.props?.match?.params || {};
        f.beforeCollectionFetch(this.cPolicies);

        try {
            let model = await this.props.aiPoliciesStore.getGlobalPermissionPolicy(id);
            this._vState.allPermissionPolicy = model;
        } catch(e) {
            console.log(e);
            this._vState.allPermissionPolicy = null;
            f.handleError()(e);
        }

        try {
            let {models, pageState} = await this.props.aiPoliciesStore.getAllPolicies(id, {
                params: this.cPolicies.params
            });
            if (Array.isArray(models)) {
                models.sort((a, b) => b.status - a.status);
            }
            f.resetCollection(this.cPolicies, models, pageState);
            this._vState.loading = false;
        } catch(e) {
            this._vState.loading = false;
            f.handleError(this.cPolicies)(e);
        }
    }
    handleBackButton = () => {
        const {id} = this.props?.match?.params || {};
        this.props.history.push('/ai_application/' + id);
    }
    postUpdateAllPermissionPolicy = (policy) => {
        this._vState.allPermissionPolicy = policy;
    }
    render() {
        const {id} = this.props?.match?.params || {};
        const {application} = this.props._vState;
        return (
            <Fragment>
                <Loader isLoading={this._vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                    {
                        application
                        ?
                            (
                                <Fragment>
                                    <Box component={Paper} className={`m-t-sm ${ id ? 'm-b-xl' : 'm-b-sm'}`} data-track-id="ai-app-global-access-policy-form">
                                        <CAiApplicationAccessForm
                                            application={application}
                                            policy={this._vState.allPermissionPolicy}
                                            permission={this.permission}
                                            cPolicies={this.cPolicies}
                                            postUpdateAllPermissionPolicy={this.postUpdateAllPermissionPolicy}
                                        />
                                    </Box>
                                    <Box component={Paper} className="m-t-sm" data-track-id="ai-app-content-restriction">
                                        <CAiApplicationAccessContentRestriction
                                            application={application}
                                            permission={this.permission}
                                            cPolicies={this.cPolicies}
                                            cSensitiveData={this.cSensitiveData}
                                            handlePageChange={this.fetchPolicies}
                                            fetchPolicies={this.fetchPolicies}
                                        />
                                    </Box>
                                </Fragment>
                            )
                        :
                            (
                                <Grid containers spacing={3}>
                                    <Grid item xs={12}>
                                        Application not found
                                    </Grid>
                                </Grid>
                            )
                    }
                </Loader>
            </Fragment>
        );
    }
}

export default withRouter(CAIPermissions);