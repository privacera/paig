import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';
import {withRouter} from 'react-router';

import {Grid} from '@material-ui/core';

import {FEATURE_PERMISSIONS} from 'utils/globals';
import CVectorDBForm from 'containers/applications/vector_db/c_vector_db_form';
import CVectorDBPolicesDetail from 'containers/policies/vector_db/c_vector_db_policies_detail';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';

@observer
class CVectorDBDetail extends Component {
	constructor(props) {
		super(props);
		this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.VECTOR_DB.PROPERTY);
        this.policyPermission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.VECTOR_DB_POLICIES.PROPERTY);
	}
    handleRedirect = () => {
        // redirect to listing page
        this.props.history.push('/vector_db');
    }
    handleCancel = () => {
        this.handleRedirect();
    }
    handlePostCreate = (response) => {
        this.props.history.replace('/vector_db/' + response.id);
    }

	render() {
	    const {handleCancel, handlePostCreate} = this;
        const {_vState, handlePostUpdate} = this.props;
		return (
            <Fragment item xs={12} md={6}>
                <Loader isLoading={_vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                    {
                        _vState.model == null
                        ? (
                            <Grid item xs={12} md={6}>
                                Vector DB not found
                            </Grid>
                        )
                        : (
                            <CVectorDBForm
                                permission={this.permission}
                                model={_vState.model}
                                handleCancel={handleCancel}
                                handlePostCreate={handlePostCreate}
                                handlePostUpdate={handlePostUpdate}
                            />
                        )
                    }
                </Loader>
                {
                    permissionCheckerUtil.checkHasReadPermission(this.policyPermission) && (
                        <Loader isLoading={_vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                            {
                                _vState.model?.id && <CVectorDBPolicesDetail vectorDBModel={_vState.model} handleTabSelect={this.props.handleTabSelect}/>
                            }
                        </Loader>
                    )
                }
            </Fragment>
		)
	}
}

export default withRouter(CVectorDBDetail);
