import React, {Component, Fragment} from 'react';

import {Grid} from '@material-ui/core';

import f from 'common-ui/utils/f';
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {FEATURE_PERMISSIONS} from 'utils/globals';
import FSModal from 'common-ui/lib/fs_modal';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {VSensitiveDataRegex} from 'components/guardrail/forms/v_sensitive_data_regex';
import {VSensitiveDataRegexForm, sensitive_data_regex_form_def} from 'components/guardrail/forms/v_sensitive_data_regex_form';

class CSensitiveDataRegex extends Component {
    constructor(props) {
        super(props);

        this.cRegex = f.initCollection({loading: false});

        this.form = createFSForm(sensitive_data_regex_form_def);

        let configs = this.props.getConfigs();
        if (configs) {
            let models = [];
            configs.forEach(c => {
                models.push(c);
            })
            f.resetCollection(this.cRegex, models);
        }

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.GUARDRAILS.PROPERTY);
    }
    handleAdd = () => {
        this.form.clearForm();
        this.form.model = null;
        this.form.index = null;
        this.regexModal.show({
            title: 'Add Regex',
            btnOkText: 'Add'
        });
    }
    handleEdit = (model, i) => {
        this.form.clearForm();
        this.form.refresh(model);
        this.form.model = model;
        this.form.index = i;
        this.regexModal.show({
            title: 'Edit Regex',
            btnOkText: 'Save'
        });
    }
    handleSave = async() => {
        let valid = await this.form.validate();
        if (!this.form.valid) return;

        let data = this.form.toJSON();

        let models = f.models(this.cRegex);

        let indexEmailRegex = models.findIndex(m => m.name === data.name);
        let indexPattern = models.findIndex(m => m.pattern === data.pattern);

        if (this.form.index != null) {
            if (indexEmailRegex !== -1 && indexEmailRegex != this.form.index) {
                f.notifyError(`The email regex ${data.name} already exists`);
                return;
            }
            if (indexPattern !== -1 && indexPattern != this.form.index) {
                f.notifyError(`The pattern ${data.pattern} already exists`);
                return;
            }
            Object.assign(models[this.form.index], data);
        } else {
            if (indexEmailRegex !== -1) {
                f.notifyError(`The email regex ${data.name} already exists`);
                return;
            }
            if (indexPattern !== -1) {
                f.notifyError(`The pattern ${data.pattern} already exists`);
                return;
            }
            models.push(data);
        }

        f.resetCollection(this.cRegex, models);

        this.regexModal?.hide?.();

        this.props.onChange?.(models);
    }
    handleOnChange = () => {
        const models = f.models(this.cRegex).map((model) => ({
            type: 'regex',
            name: model.name,
            description: model.description,
            pattern: model.pattern,
            action: model.action
        }));
        this.props.onChange?.(models);
    }
    handleRemove = (model) => {
        f._confirm.show({
            title: `Confirm Remove`,
            children: <Fragment>Are you sure want to remove <b>{model.name}</b> regex?</Fragment>,
            btnOkVariant: "contained",
            btnOkColor: 'primary'
        })
        .then(confirm => {
            confirm.hide();

            const models = f.models(this.cRegex).filter((m) => m.name !== model.name);
            f.resetCollection(this.cRegex, models);

            this.handleOnChange();
        }, () => {});
    }
    handleActionChange = (value, model) => {
        model.action = value;
        this.handleOnChange();
    }
    render() {
        return (
            <Fragment>
                <Grid container spacing={3}>
                    <AddButtonWithPermission
                        colAttr={{
                            xs: 12,
                            style: {
                                position: 'absolute',
                                right: '30px',
                                marginTop: '-55px'
                            }
                        }}
                        permission={this.permission}
                        onClick={this.handleAdd}
                        label="Add Regex"
                        data-test="add-regex"
                    />
                </Grid>
                <VSensitiveDataRegex
                    data={this.cRegex}
                    permission={this.permission}
                    handleEdit={this.handleEdit}
                    handleRemove={this.handleRemove}
                    handleActionChange={this.handleActionChange}
                />
                <FSModal ref={ref => this.regexModal = ref}
                    dataResolve={this.handleSave}
                    maxWidth="md"
                >
                    <VSensitiveDataRegexForm
                        form={this.form}
                    />
                </FSModal>
            </Fragment>
        )
    }
}

export default CSensitiveDataRegex;