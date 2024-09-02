import React, {Component, Fragment} from 'react';
import {action, observable} from 'mobx';
import {inject, observer} from 'mobx-react';
import {withRouter} from 'react-router';

import { Grid, Paper, Box }  from '@material-ui/core';

import BaseContainer from 'containers/base_container';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import f from 'common-ui/utils/f';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import CVectorDBAccessForm from 'containers/policies/vector_db/c_vector_db_access_form';
import CVectorDBAccessContentRestriction from 'containers/policies/vector_db/c_vector_db_access_content_restriction';

@inject('vectorDBPolicyStore')
@observer
class CVectorDBPermissions extends Component {
    @observable _vState = {
        loading: true
    }
    constructor(props) {
        super(props)

        this.cPolicies = f.initCollection();
        this.cMetaData = f.initCollection();

        this.cPolicies.params = {
            size: 999,
            sort: 'createTime,desc'
        }

        this.cMetaData.params = {
            size: 999
        };

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.VECTOR_DB_POLICIES.PROPERTY);
    }
    componentDidMount = () => {
        this.fetchPolicies();
    }
    // fetchMetaData = () => {
    //     f.beforeCollectionFetch(this.cMetaData);
    //     this.props.metaDataStore.fetchMetaData({
    //         params: this.cMetaData.params
           
    //     }).then(f.handleSuccess(this.cMetaData), f.handleError(this.cMetaData));
    // }

    @action
    fetchPolicies = async () => {
        const {id} = this.props?.match?.params || {};
        f.beforeCollectionFetch(this.cPolicies);

        try {
            let {models, pageState} = await this.props.vectorDBPolicyStore.getAllPolicies(id, {
                params: this.cPolicies.params
            });

            f.resetCollection(this.cPolicies, models, pageState);
            this._vState.loading = false;
        } catch(e) {
            this._vState.loading = false;
            f.handleError(this.cPolicies)(e);
        }
    }
    postPermissionUpdate = (vectorDB) => {
        Object.assign(this.props._vState.model, vectorDB);
    }
    handleBackButton = () => {
        const {id} = this.props?.match?.params || {};
        this.props.history.push('/vector_db/' + id);
    }
    render() {
        const {id} = this.props?.match?.params || {};
        const {model: vectorDBModel} = this.props._vState;
        return (
            <Fragment>
                <Loader isLoading={this._vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                    {
                        vectorDBModel
                        ?
                            (
                                <Fragment>
                                    <Box component={Paper} className={`m-t-sm ${ id ? 'm-b-xl' : 'm-b-sm'}`}>
                                        <CVectorDBAccessForm
                                            vectorDBModel={vectorDBModel}
                                            permission={this.permission}
                                            postPermissionUpdate={this.postPermissionUpdate}
                                        />
                                    </Box>
                                    <Box component={Paper} className="m-t-sm" data-track-id="vector-db-data-filtering" 
                                        data-testid="vector-db-data-filtering"
                                    >
                                        <CVectorDBAccessContentRestriction
                                            vectorDBModel={vectorDBModel}
                                            permission={this.permission}
                                            cPolicies={this.cPolicies}
                                            cMetaData={this.cMetaData}
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
                                        Vector DB not found
                                    </Grid>
                                </Grid>
                            )
                    }
                </Loader>
            </Fragment>
        );
    }
}

export default withRouter(CVectorDBPermissions);