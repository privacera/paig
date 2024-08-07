import React, {Component} from 'react';
import {observer, inject} from 'mobx-react';
import {observable} from 'mobx';

import { Grid, Button, Typography}  from "@material-ui/core";
import CircularProgress from "@material-ui/core/CircularProgress/CircularProgress";

import f from 'common-ui/utils/f';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import AIPolicyFormUtil from 'containers/policies/ai_policies/ai_policy_form_util';
import VAIApplicationAccessForm from 'components/policies/v_ai_application_access_form';
import {PENDO_GUIDE_NAME, triggerPendoFeedbackGuideManual} from 'components/pendo/pendo_initializer';

@inject('aiPoliciesStore')
@observer
class CAiApplicationAccessForm extends Component {
    @observable _vState = {
        editMode: false,
        saving: false
    }
    constructor(props) {
        super(props);

        const policy = props.policy || {};

        this.aiPolicyFormUtil = new AIPolicyFormUtil();

        this.accessFields = [
            observable({
                accessType: 'allow',
                users: [],
                groups:[],
                roles: []
            }),
            observable({
                accessType: 'deny',
                users: [],
                groups:[],
                roles: []
            })
        ]

        this.setFormData(policy);
    }
    setFormData = (policy={}) => {
        let allowObj = this.accessFields[0];
        allowObj.users = policy.allowedUsers || [];
        allowObj.roles = policy.allowedRoles || [];
        allowObj.groups = [];
        if (policy.allowedGroups) {
            policy.allowedGroups.forEach(group => {
                if (group === 'public') {
                    group = 'Everyone';
                }
                allowObj.groups.push(group);
            })
        }

        let denyObj = this.accessFields[1];
        denyObj.users = policy.deniedUsers || [];
        denyObj.roles = policy.deniedRoles || [];
        denyObj.groups = [];
        if (policy.deniedGroups) {
            policy.deniedGroups.forEach(group => {
                if (group === 'public') {
                    group = 'Everyone';
                }
                denyObj.groups.push(group);
            })
        }
    }
    handleEdit = () => {
        this._vState.editMode = true;
    }
    handleCancelEdit = () => {
        this.setFormData(this.props.policy);
        this._vState.editMode = false;
    }
    reAssignOthersOptionToGroups = () => {
        const data = {
            allowedUsers: this.accessFields[0].users.slice(),
            allowedGroups: this.accessFields[0].groups.slice(),
            allowedRoles: this.accessFields[0].roles.slice(),
            deniedUsers: this.accessFields[1].users.slice(),
            deniedGroups: this.accessFields[1].groups.slice(),
            deniedRoles: this.accessFields[1].roles.slice()
        };

        if (data.allowedGroups.length === 1 && data.allowedGroups[0] === 'Everyone') {
            data.allowedGroups = ['public'];
        }

        if (data.deniedGroups.length === 1 && data.deniedGroups[0] === 'Everyone') {
            data.deniedGroups = ['public'];
        }

        return data;
    }
    checkHasAnyUsersGroups = (data) => {
        let hasAnyUsersGroups = false;

        if (data.allowedUsers?.length || data.allowedGroups?.length || data.deniedUsers?.length || data.deniedGroups?.length) {
            hasAnyUsersGroups = true;
        }

        return hasAnyUsersGroups;
    }
    handleUpdate = async () => {
        const { application, cPolicies, policy } = this.props;
        const appId = application.id;
        if (appId) {
            // For save policies assign others option value to groups;
            const data = this.reAssignOthersOptionToGroups();
            data.applicationId = appId;

            const hasAnyUsersGroups = this.checkHasAnyUsersGroups(data);

            if (policy && policy.id && hasAnyUsersGroups) {
                data.id = policy.id;
            }

            if ((!hasAnyUsersGroups && !f.models(cPolicies).length)) {
                f.notifyError(`Please select atleast one user or group.`);
                return;
            }

            this._vState.saving = true;
            this.props.aiPoliciesStore.updateGlobalPermissionPolicy(appId, data)
                .then((response) => {
                    f.notifySuccess('Restriction updated successfully.');
                    this.setFormData(response);
                    this.props.postUpdateAllPermissionPolicy(response);
                    this._vState.editMode = false;
                    this._vState.saving = false;

                    triggerPendoFeedbackGuideManual(PENDO_GUIDE_NAME.POLICY_PAGE_FEEDBACK);
                }, (e) => {
                    this._vState.saving = false;
                    f.handleError()(e);
                });
        }
    }

    render() {
        const { policy, permission } = this.props;

        return (
            <Grid container spacing={3} style={{padding: '5px 15px'}} data-testid="ai-app-access-card"
                data-track-id="ai-app-access-card"
            >
                <Grid item sm={8} xs={12}>
                    <Typography variant="body1">
                        AI Application Access
                    </Typography>
                </Grid>
                <Grid item sm={4} xs={12} className="text-right">
                    {
                        !this._vState.editMode &&
                        <div style={{marginBottom: '7px'}}>
                            <ActionButtonsWithPermission
                                permission={permission}
                                onEditClick={this.handleEdit}
                                hideDelete={true}
                            />
                        </div>
                    }
                    {
                        this._vState.editMode &&
                        <div>
                            <Button
                                data-testid="edit-save-btn"
                                data-track-id="edit-global-policy-save-btn"
                                variant="contained"
                                color="primary"
                                className="m-r-sm"
                                size="small"
                                disabled={this._vState.saving}
                                onClick={this.handleUpdate}
                            >
                                {
                                    this._vState.saving &&
                                    <CircularProgress size="15px" className="m-r-xs" />
                                }
                                SAVE
                            </Button>
                            <Button
                                data-testid="edit-cancel-btn"
                                data-track-id="edit-global-policy-cancel-btn"
                                variant="outlined"
                                color="primary"
                                size="small"
                                onClick={this.handleCancelEdit}
                            >CANCEL</Button>
                        </div>
                    }
                </Grid>
                <VAIApplicationAccessForm
                    ref={ref => this.policyFormRef = ref}
                    editMode={this._vState.editMode}
                    form={this.form}
                    accessFields={this.accessFields}
                    aiPolicyFormUtil={this.aiPolicyFormUtil}
                />
            </Grid>
        );
    }
}

export default CAiApplicationAccessForm;