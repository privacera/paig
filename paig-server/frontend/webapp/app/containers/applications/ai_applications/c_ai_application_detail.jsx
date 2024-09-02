import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';
import {withRouter} from 'react-router';

import {Grid} from '@material-ui/core';

import {FEATURE_PERMISSIONS} from 'utils/globals';
import CAIApplicationForm from 'containers/applications/ai_applications/c_ai_application_form';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';
import CAIPolicesDetail from 'containers/policies/ai_policies/c_ai_policies_detail';

@observer
class CAIApplications extends Component {
	constructor(props) {
		super(props);
		this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.AI_APPLICATIONS.PROPERTY);
        this.policyPermission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.AI_POLICIES.PROPERTY);
	}
    handleRedirect = () => {
        // redirect to listing page
        this.props.history.push('/ai_applications');
    }
    handleCancel = () => {
        this.handleRedirect();
    }
    handlePostCreate = (response) => {
        this.props.history.replace('/ai_application/' + response.id);
    }

	render() {
	    const {handleCancel, handlePostCreate} = this;
        const {_vState, handlePostUpdate} = this.props;
		return (
            <Fragment>
				<Loader isLoading={_vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                    {
                        _vState.application == null
                        ? (
                            <Grid containers spacing={3}>
                                <Grid item xs={12}>
                                    Application not found
                                </Grid>
                            </Grid>
                        )
                        : (
                            <CAIApplicationForm
                                permission={this.permission}
                                application={_vState.application}
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
                                _vState.application?.id && <CAIPolicesDetail application={_vState.application} handleTabSelect={this.props.handleTabSelect}/>
                            }
                        </Loader>
                    )
                }
            </Fragment>
		)
	}
}

export default withRouter(CAIApplications);