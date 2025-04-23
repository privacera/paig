import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import {observable} from 'mobx';

import {Box, Paper} from '@material-ui/core';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import FSModal from 'common-ui/lib/fs_modal';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {createFSForm} from 'common-ui/lib/form/fs_form';
import BaseContainer from 'containers/base_container';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import {Filters, VResponseTemplate} from 'components/guardrail/v_response_template';
import VResponseTemplateForm, {response_template_form_def} from 'components/guardrail/v_response_template_form';

@inject('guardrailResponseTemplateStore')
class CResponseTemplate extends Component {
    @observable _vState = {
        searchValue: ''
    }
    constructor(props) {
        super(props);

        this.cResponseTemplate = f.initCollection();
        this.cResponseTemplate.params = {
            size: DEFAULTS.DEFAULT_PAGE_SIZE,
            sort: 'id,desc'
        }

        this.form = createFSForm(response_template_form_def);

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.GUARDRAILS.PROPERTY);
    }
    componentDidMount() {
        this.handleRefresh();
    }
    handleRefresh = () => {
        this.fetchResponseTemplate();
    }
    fetchResponseTemplate = () => {
        f.beforeCollectionFetch(this.cResponseTemplate);
        this.props.guardrailResponseTemplateStore.searchResponseTemplate({
            params: this.cResponseTemplate.params
        }).then(f.handleSuccess(this.cResponseTemplate), f.handleError(this.cResponseTemplate));
    }
    handlePageChange = () => {
        this.handleRefresh();
    };
    handleOnChange = (e, val) => {
        this._vState.searchValue = val;
        this.cResponseTemplate.params.response = val || undefined;
    }
    handleSearch = () => {
        delete this.cResponseTemplate.params.page;
        this.fetchResponseTemplate();
    }
    handleCreate = () => {
        this.form.clearForm();
        this.Modal.show({
          title: "Add Response Template"
        });
    }
    handleEdit = (model) => {
        this.form.clearForm();
        this.form.refresh(model);
        this.form.model = model;
        this.Modal.show({
          title: "Edit Response Template"
        });
    }
    handleSave = async() => {
        await this.form.validate();
        if (!this.form.valid) {
          return;
        }
        let data = this.form.toJSON();
        data = Object.assign({}, this.form.model, data);

        this.Modal.okBtnDisabled(true);

        if (data.id) {
            try {
                data = await this.props.guardrailResponseTemplateStore.updateResponseTemplate(data.id, data);
                this.Modal.hide();
                f.notifySuccess("Response Template updated successfully");
                this.handleRefresh();
            } catch (e) {
                f.handleError(null, null, {modal: this.Modal})(e);
                console.error("Error updating response template:", e);
            }
        } else {
            delete data.id;
            try {
                await this.props.guardrailResponseTemplateStore.createResponseTemplate(data);
                this.Modal.hide();
                f.notifySuccess("Response Template added successfully");
                this.handleRefresh();
            } catch (e) {
                f.handleError(null, null, {modal: this.Modal})(e);
                console.error("Error creating response template:", e);
            }
        }
    }
    handleDelete = (model) => {
        f._confirm.show({
            title: 'Confirm Delete',
            children: <Fragment>Are you sure you want to delete <b>{model.response}</b> response template?</Fragment>,
            btnCancelText: 'Cancel',
            btnOkText: 'Delete',
            btnOkColor: 'secondary',
            btnOkVariant: 'text'
        }).then((confirm) => {
            this.props.guardrailResponseTemplateStore.deleteResponseTemplate(model.id, {
                models: this.cResponseTemplate
            }).then(() => {
                f.notifySuccess(`The response template deleted successfully`);
                confirm.hide();
                f.handlePagination(this.cResponseTemplate, this.cResponseTemplate.params);
                this.handleRefresh();
            }, f.handleError());
        }, () => {});
    }
    render() {
        return (
            <BaseContainer
                handleRefresh={this.handleRefresh}
            >
                <Box component={Paper} p={2} className="m-t-sm">
                    <Filters
                        _vState={this._vState}
                        handleOnChange={this.handleOnChange}
                        handleSearch={this.handleSearch}
                        permission={this.permission}
                        data={this.cResponseTemplate}
                        handleCreate={this.handleCreate}
                    />
                    <VResponseTemplate
                        permission={this.permission}
                        data={this.cResponseTemplate}
                        handlePageChange={this.fetchResponseTemplate}
                        handleEdit={this.handleEdit}
                        handleDelete={this.handleDelete}
                    />
                </Box>
                <FSModal ref={ref => this.Modal = ref} dataResolve={this.handleSave}>
                    <VResponseTemplateForm form={this.form} />
                </FSModal>
            </BaseContainer>
        )
    }
}

export default CResponseTemplate;