import React, {Component, Fragment} from 'react';
import { observer, inject } from 'mobx-react';
import { observable } from 'mobx';
import { cloneDeep } from 'lodash';

import {Grid, Typography} from '@material-ui/core';

import UiState from 'data/ui_state';
import VVectorDBPolicyForm, { vector_db_policy_form_def } from 'components/policies/v_vector_db_policy_form';
import VectorDBPolicyFormUtil from 'containers/policies/vector_db/vector_db_policy_form_util';
import { metaDataLookUps } from 'components/policies/field_lookups';
import VVectorDBAccessContentRestriction from 'components/policies/v_vector_db_access_content_restriction'
import {FormGroupSelect2} from 'common-ui/components/form_fields';
import { SearchField } from 'common-ui/components/filters';
import { createFSForm } from 'common-ui/lib/form/fs_form';
import f from 'common-ui/utils/f';
import { STATUS } from 'common-ui/utils/globals';
import FSModal from 'common-ui/lib/fs_modal';
import { AddButtonWithPermission } from 'common-ui/components/action_buttons';

@inject('vectorDBPolicyStore')
@observer
class CVectorDBAccessContentRestriction extends Component {
    @observable _vState = {
        metadataKey: null
    }
    constructor(props) {
        super(props);

        this.form = createFSForm(vector_db_policy_form_def);

        this.vectorDBPolicyFormUtil = new VectorDBPolicyFormUtil();
        this.vectorDBPolicyFormUtil.init(this.form);
    }
    handleStatusUpdate = (value, model) => {
        const {disabled, enabled} = STATUS;
        const statusObj = disabled.value === value ? disabled : enabled;
        //"{model.description}"
        f._confirm.show({
            title: `Update Restriction Status`,
            children: <Fragment>Are you sure you want to <b>{statusObj.label}</b> the restriction status?</Fragment>,
            btnOkVariant: "contained",
            btnOkColor: 'primary',
            btnOkText: statusObj.label,
            btnCancelText: 'Cancel'
        })
        .then((confirm) => {
            model.status = value;
            this.props.vectorDBPolicyStore.updatePolicy(model.id, model.vectorDBId, model)
            .then(() => {
                confirm.hide();
                this.props.fetchPolicies();
                f.notifySuccess(`Restriction ${statusObj.name} successfully.`);
            }, f.handleError(null, null, {confirm}));
        }, () => {});
    }
    reAssignOthersOptionToGroups = () => {
        const data = cloneDeep(this.vectorDBPolicyFormUtil.getFormData());
        // if (data.others?.length) {
        //     data.groups = ['public'];
        // }
        if (data.allowedGroups.length === 1 && data.allowedGroups[0] === 'Everyone') {
            data.allowedGroups = ['public'];
        }
        if (data.deniedGroups.length === 1 && data.deniedGroups[0] === 'Others') {
            data.deniedGroups = ['public'];
        }
        data.allowedGroups = data.allowedGroups.map(group => group === 'Others' ? 'public' : group);
        data.deniedGroups = data.deniedGroups.map(group => group === 'Others' ? 'public' : group);
        // delete data.others;
        return data;
    }
    handlePolicySave = async () => {
        const {cPolicies} = this.props;
        const { vectorDBModel } = this.props;
        const valid = await this.vectorDBPolicyFormUtil.formValidation();
        const modal = this.addPolicyModalRef;
        if (valid && vectorDBModel.id) {

            modal && modal.okBtnDisabled(true);
            // For save policies assign others option value to groups;
            let data = this.reAssignOthersOptionToGroups();
            data.vectorDBId = vectorDBModel.id;
            data.tenantId = UiState.getTenantId();

            if (this.form.model) {
                data = Object.assign({}, this.form.model || {}, data);
            }

            if (data.id) {
                this.props.vectorDBPolicyStore.updatePolicy(data.id, vectorDBModel.id, data)
                    .then(() => {
                        this.vectorDBPolicyFormUtil.resetForm();
                        modal && modal.hide();
                        this.props.fetchPolicies();
                        f.notifySuccess(`Restriction updated successfully.`);
                    }, f.handleError(cPolicies, null, {
                        modal
                    }));
            } else {
                this.props.vectorDBPolicyStore.createPolicy(vectorDBModel.id, data)
                    .then(() => {
                        this.vectorDBPolicyFormUtil.resetForm();
                        modal && modal.hide();
                        this.props.fetchPolicies();
                        f.notifySuccess(`Restriction added successfully.`);
                    }, f.handleError(cPolicies, null, {
                        modal
                    }));
            }
        }
    }
    handleReject = () => {
        this.vectorDBPolicyFormUtil.resetForm();
        this.addPolicyModalRef.hide();
    }
    handleAdd = () => {
        const {vectorDBModel} = this.props;
        this.addPolicyModalRef.show({
          title: `Add/Edit RAG Contextual Data Filtering to "${vectorDBModel.name}"`
        });
    }
    handlePolicyEdit = model => {
        const { vectorDBModel } = this.props;
        this.vectorDBPolicyFormUtil.setNewPayloadInForm(cloneDeep(model));
        this.addPolicyModalRef?.show({
          title: `Edit Restriction in "${vectorDBModel.name}" vector DB`
        });
    }
    handlePolicyDelete = model => {
        const {cPolicies} = this.props;

        //"{model.description || model.name}"
        f._confirm.confirmDelete({
          children: <Fragment>Are you sure you want to <b>Delete</b> the restriction?</Fragment>,
        })
        .then((confirm) => {
          this.props.vectorDBPolicyStore.deletePolicy(model.id, model.vectorDBId, {
                models: cPolicies
            })
            .then(() => {
              confirm.hide();
              f.handlePagination(cPolicies, cPolicies.params);
              this.props.fetchPolicies();
              f.notifySuccess('Restriction has been deleted.');
            }, f.handleError(null, null, {confirm}));
        }, () => {});
    }
    handleSearch = (value) => {
        const {cPolicies, fetchPolicies} = this.props;
        delete cPolicies.params.page;
        cPolicies.params.description = value || undefined;
        fetchPolicies();
    }
    handleMetaDataFilter = (value) => {
        const {cPolicies, fetchPolicies} = this.props;
        delete cPolicies.params.page;
        this._vState.metadataKey = value;
        cPolicies.params.metadataKey = value || undefined;
        fetchPolicies();
    }
    render() {
        const {_vState, handleSearch, handleMetaDataFilter, vectorDBPolicyFormUtil} = this;
        const {cPolicies, cMetaData, handlePageChange, permission} = this.props;

        return (
            <Fragment>
                <Grid container spacing={3} style={{padding: '5px 15px'}}>
                    <Grid item className="flex-grow-2">
                        <Typography variant="h6" gutterBottom>
                            RAG Contextual Data Filtering
                        </Typography>
                    </Grid>
                    {/* <SearchField
                        colAttr={{sm: 12, md: 3, lg: 3}}
                        placeholder="Search"
                        onEnter={handleSearch}
                    /> */}
                    <FormGroupSelect2
                        inputColAttr={{
                            xs: 12,
                            sm: 8,
                            md: 4,
                            lg: 3
                        }}
                        showLabel={false}
                        value={_vState.metadataKey}
                        labelKey="label"
                        valueKey="label"
                        placeholder="Filter Vector DB Metadata"
                        triggerOnLoad={true}
                        openText="Options"
                        loadOptions={(searchString, callback) => {
                            metaDataLookUps(searchString, options => callback(options));
                        }}
                        onChange={handleMetaDataFilter}
                        data-track-id="vector-db-rag-filter-by-meta-data"
                        data-testid="vector-db-rag-filter-by-meta-data"
                    />
                    <AddButtonWithPermission
                        colAttr={null}
                        permission={permission}
                        label="Add Data Filtering"
                        onClick={this.handleAdd}
                        data-track-id="vector-db-add-data-filtering"
                    />
                </Grid>
                <VVectorDBAccessContentRestriction
                    permission={permission}
                    cPolicies={cPolicies}
                    cMetaData={cMetaData}
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
                        <VVectorDBPolicyForm
                            ref={ref => this.policyFormRef = ref}
                            form={this.form}
                            vectorDBPolicyFormUtil={vectorDBPolicyFormUtil}
                        />
                    </div>
                </FSModal>
            </Fragment>
        )
    }
}

export default CVectorDBAccessContentRestriction;