import React, {Component, Fragment} from 'react';
import { observer, inject } from 'mobx-react';
import { observable } from 'mobx';
import { cloneDeep } from 'lodash';

import {Grid, Typography} from '@material-ui/core';

import UiState from 'data/ui_state';
import VAIPoliciesForm, { ai_policy_form_def } from 'components/policies/v_ai_policy_form';
import AIPolicyFormUtil from 'containers/policies/ai_policies/ai_policy_form_util';
import { sensitiveDataLookUps } from 'components/policies/field_lookups';
import VAIApplicationAccessContentRestriction from 'components/policies/v_ai_application_access_content_restriction'
import {triggerPendoFeedbackGuideManual, PENDO_GUIDE_NAME} from 'components/pendo/pendo_initializer';
import {FormGroupSelect2} from 'common-ui/components/form_fields';
import { SearchField } from 'common-ui/components/filters';
import { createFSForm } from 'common-ui/lib/form/fs_form';
import f from 'common-ui/utils/f';
import { STATUS } from 'common-ui/utils/globals';
import FSModal from 'common-ui/lib/fs_modal';
import { AddButtonWithPermission } from 'common-ui/components/action_buttons';

@inject('aiPoliciesStore')
@observer
class CAiApplicationAccessContentRestriction extends Component {
    @observable _vState = {
        sensitiveData: null
    }
    constructor(props) {
        super(props);

        this.form = createFSForm(ai_policy_form_def);

        this.aiPolicyFormUtil = new AIPolicyFormUtil();
        this.aiPolicyFormUtil.init(this.form);
    }
    handleStatusUpdate = (value, model) => {
        const { disabled, enabled} = STATUS;
        const statusObj = disabled.value === value ? disabled : enabled;
        f._confirm.show({
            title: `Update Restriction Status`,
            children: <Fragment>Are you sure you want to <b>{statusObj.label}</b> the "{model.description}" restriction status?</Fragment>,
            btnOkVariant: "contained",
            btnOkColor: 'primary',
            btnOkText: statusObj.label,
            btnCancelText: 'Cancel'
        })
        .then((confirm) => {
            model.status = value;
            this.props.aiPoliciesStore.updatePolicy(model.id, model.applicationId, model, UiState.getHeaderWithTenantId())
            .then(() => {
                confirm.hide();
                this.props.fetchPolicies();
                f.notifySuccess(`Restriction ${statusObj.name} successfully.`);
            }, f.handleError(null, null, {confirm}));
        }, () => {});
    }
    handlePolicyEdit = model => {
        const { application } = this.props;
        this.aiPolicyFormUtil.setNewPayloadInForm(cloneDeep(model));
        this.addPolicyModalRef?.show({
          title: `Edit Restriction in "${application.name}" application`
        });
    }
    reAssignOthersOptionToGroups = () => {
        const data = cloneDeep(this.aiPolicyFormUtil.getFormData());
        if (data.others?.length) {
            data.groups = ['public'];
        }
        if (data.groups.length === 1 && data.groups[0] === 'Everyone') {
            data.groups = ['public'];
        }
        delete data.others;
        return data;
    }
    handlePolicySave = async () => {
        const {cPolicies} = this.props;
        const { application } = this.props;
        const appId = application.id;
        const valid = await this.aiPolicyFormUtil.formValidation();
        const modal = this.addPolicyModalRef;
        if (valid && appId) {

            modal && modal.okBtnDisabled(true);
            // For save policies assign others option value to groups;
            let data = this.reAssignOthersOptionToGroups();
            data.applicationId = appId;
            data.tenantId = UiState.getTenantId();

            if (this.form.model) {
                data = Object.assign({}, this.form.model || {}, data);
            }

            if (data.id) {
                this.props.aiPoliciesStore.updatePolicy(data.id, appId, data, UiState.getHeaderWithTenantId())
                    .then(() => {
                        this.aiPolicyFormUtil.resetForm();
                        modal && modal.hide();
                        this.props.fetchPolicies();
                        f.notifySuccess(`Restriction updated successfully.`);

                        triggerPendoFeedbackGuideManual(PENDO_GUIDE_NAME.POLICY_PAGE_FEEDBACK);
                    }, f.handleError(cPolicies, null, {
                        modal
                    }));
            } else {
                this.props.aiPoliciesStore.createPolicy(appId, data, UiState.getHeaderWithTenantId())
                    .then(() => {
                        this.aiPolicyFormUtil.resetForm();
                        modal && modal.hide();
                        this.props.fetchPolicies();
                        f.notifySuccess(`Restriction added successfully.`);

                        triggerPendoFeedbackGuideManual(PENDO_GUIDE_NAME.POLICY_PAGE_FEEDBACK);
                    }, f.handleError(cPolicies, null, {
                        modal
                    }));
            }
        }
    }
    handleReject = () => {
        this.aiPolicyFormUtil.resetForm();
        this.addPolicyModalRef.hide();
    }
    handlePolicyDelete = model => {
        const {cPolicies} = this.props;

        f._confirm.confirmDelete({
          children: <Fragment>Are you sure you want to <b>Delete</b> the "{model.description}" restriction?</Fragment>,
        })
        .then((confirm) => {
          this.props.aiPoliciesStore.deletePolicy(model.id, model.applicationId, {
                models: cPolicies,
                ...UiState.getHeaderWithTenantId()
            })
            .then(() => {
              confirm.hide();
              f.handlePagination(cPolicies, cPolicies.params);
              this.props.fetchPolicies();
              f.notifySuccess('Restriction has been deleted.');
            }, f.handleError(null, null, {confirm}));
        }, () => {});
    }
    handleAdd = () => {
        const {application} = this.props;
        // this.aiPolicyFormUtil.addItems();
        this.addPolicyModalRef.show({
          title: `Add Restriction to "${application.name}" application`
        });
    }
    handleSearch = (value) => {
        const {cPolicies, fetchPolicies} = this.props;
        delete cPolicies.params.page;
        cPolicies.params.description = value || undefined;
        fetchPolicies();
    }
    handleSensitiveDataFilter = (value) => {
        const {cPolicies, fetchPolicies} = this.props;
        delete cPolicies.params.page;
        this._vState.sensitiveData = value;
        cPolicies.params.tag = value || undefined;
        fetchPolicies();
    }
    render() {
        const {_vState, handleSearch, handleSensitiveDataFilter} = this;
        const {cPolicies, cSensitiveData, handlePageChange, permission} = this.props;

        return (
            <Fragment>
                <Grid container spacing={3} style={{padding: '5px 15px'}}>
                    <Grid item className="flex-grow-2">
                        <Typography variant="h6" gutterBottom>
                            Content Restriction
                        </Typography>
                    </Grid>
                    <SearchField
                        colAttr={{xs:12, sm: 12, md: 3, lg: 3, 'data-track-id': 'search-ai-app-content-restriction'}}
                        placeholder="Search"
                        onEnter={handleSearch}
                        data-testid="ai-app-content-restriction-search"
                    />
                    <FormGroupSelect2
                        inputColAttr={{
                            xs: 12,
                            md: 3,
                            lg: 3
                        }}
                        showLabel={false}
                        value={_vState.sensitiveData}
                        labelKey="label"
                        valueKey="value"
                        placeholder="Filter Tags"
                        triggerOnLoad={true}
                        openText="Options"
                        loadOptions={(searchString, callback) => {
                            sensitiveDataLookUps(searchString, options => callback(options));
                        }}
                        onChange={handleSensitiveDataFilter}
                        data-track-id="search-content-restriction-by-sensitive-data"
                        data-testid="sensitive-data-filter"
                    />
                    <AddButtonWithPermission
                        colAttr={null}
                        permission={permission}
                        label="Add Restriction"
                        data-track-id="ai-app-add-restriction"
                        onClick={this.handleAdd}
                        data-testid="add-restriction-button"
                    />
                </Grid>
                <VAIApplicationAccessContentRestriction
                    permission={permission}
                    cPolicies={cPolicies}
                    cSensitiveData={cSensitiveData}
                    handlePageChange={handlePageChange}
                    handleStatusUpdate={this.handleStatusUpdate}
                    handlePolicyEdit={this.handlePolicyEdit}
                    handlePolicyDelete={this.handlePolicyDelete}
                />
                <FSModal
                    maxWidth="lg"
                    ref={ref => this.addPolicyModalRef = ref}
                    dataResolve={this.handlePolicySave}
                    reject={this.handleReject}
                >
                    <div className="restriction-modal">
                        <VAIPoliciesForm ref={ref => this.policyFormRef = ref}
                            form={this.form}
                            aiPolicyFormUtil={this.aiPolicyFormUtil}
                        />
                    </div>
                </FSModal>
            </Fragment>
        )
    }
}

export default CAiApplicationAccessContentRestriction;
