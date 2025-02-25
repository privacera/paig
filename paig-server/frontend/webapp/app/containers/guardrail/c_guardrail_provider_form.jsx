import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import {observable} from 'mobx';
import {isEmpty} from 'lodash';

import f from 'common-ui/utils/f';
import FSModal from 'common-ui/lib/fs_modal';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {AWS_PROVIDER_CONNECTION_CONFIG_TYPE} from 'utils/globals';
import {VGuardrailProviderBasicForm, guardrail_provider_form_def, provider_form_def} from 'components/guardrail/v_guardrail_provider_form';

@inject('guardrailConnectionProviderStore')
class CGuardrailProviderForm extends Component {
    @observable connectionState = {
        inProgress: false,
        showTestConnectionMsg: false,
        testConnectionResponse: {
            statusCode: 0,
            msgDesc: ''
        }
    }
    constructor(props) {
        super(props);

        this.form = createFSForm(guardrail_provider_form_def);
    }
    getPropertiesForm = () => {
        this.propertiesForm = createFSForm(provider_form_def[this.form.fields.guardrailsProvider.value] || {});

        if (this.form.model?.connectionDetails) {
            this.propertiesForm.refresh(this.form.model.connectionDetails);
            let configType = AWS_PROVIDER_CONNECTION_CONFIG_TYPE.IAM_ROLE.TYPE;
            if (this.form.model.connectionDetails.access_key) {
                configType = AWS_PROVIDER_CONNECTION_CONFIG_TYPE.ACCESS_SECRET_KEY.TYPE;
            } else if (isEmpty(this.form.model.connectionDetails)) {
                configType = AWS_PROVIDER_CONNECTION_CONFIG_TYPE.INSTANCE_ROLE.TYPE;
            }
            this.propertiesForm.refresh({
                config_type: configType
            })
        }

        return this.propertiesForm;
    }
    handleCreate = (provider) => {
        this.resetTestConnection();
        this.form.clearForm();
        this.form.model = null;
        this.form.refresh({
            guardrailsProvider: provider.NAME
        });

        this.Modal.show({
            title: "Add Connection"
        });
    }
    handleEdit = (model) => {
        this.resetTestConnection();
        this.form.clearForm();
        this.form.refresh(model);
        this.form.model = model;

        this.Modal.show({
            title: "Edit Connection"
        });
    }
    getData = async() => {
        await this.form.validate();
        await this.propertiesForm.validate();
        if (!this.form.valid || !this.propertiesForm.valid) {
          return;
        }
        let data = this.form.toJSON();
        data = Object.assign({}, this.form.model, data);
        data.connectionDetails = this.propertiesForm.toJSON();

        if (data.connectionDetails.config_type === AWS_PROVIDER_CONNECTION_CONFIG_TYPE.ACCESS_SECRET_KEY.TYPE) {
            delete data.connectionDetails.iam_role;
        } else if (data.connectionDetails.config_type === AWS_PROVIDER_CONNECTION_CONFIG_TYPE.IAM_ROLE.TYPE) {
            delete data.connectionDetails.access_key;
            delete data.connectionDetails.secret_key;
            delete data.connectionDetails.session_token;
        } else if (data.connectionDetails.config_type === AWS_PROVIDER_CONNECTION_CONFIG_TYPE.INSTANCE_ROLE.TYPE) {
            data.connectionDetails = {};
        }
        delete data.connectionDetails.config_type;

        return data;
    }
    handleSave = async() => {
        let data = await this.getData();

        if (!data) {
            return;
        }

        this.Modal.okBtnDisabled(true);

        if (data.id) {
            try {
                data = await this.props.guardrailConnectionProviderStore.updateGuardrailConnectionProvider(data.id, data);
                this.Modal.hide();
                f.notifySuccess("Connection updated successfully");
                this.props.handlePostSave?.();
            } catch (e) {
                f.handleError(null, null, {modal: this.Modal})(e);
            }
        } else {
            delete data.id;
            try {
                await this.props.guardrailConnectionProviderStore.createGuardrailConnectionProvider(data);
                this.Modal.hide();
                f.notifySuccess("Connection added successfully");
                this.props.handlePostSave?.();
            } catch (e) {
                f.handleError(null, null, {modal: this.Modal})(e);
            }
        }
    }
    resetTestConnection = () => {
        Object.assign(this.connectionState, {
            inProgress: false,
            showTestConnectionMsg: false,
            testConnectionResponse: {
                statusCode: 0,
                msgDesc: ''
            }
        });
    }
    handleTestConnection = async() => {
        let data = await this.getData();
        if (!data) {
            return;
        }

        Object.assign(this.connectionState, {
            inProgress: true,
            showTestConnectionMsg: false,
            testConnectionResponse: {
                statusCode: 0,
                msgDesc: ''
            }
        });

        try {
            const res = await this.props.guardrailConnectionProviderStore.guardrailProviderConnectionTest(data);
            Object.assign(this.connectionState, {
                inProgress: false,
                showTestConnectionMsg: true,
                testConnectionResponse: {
                    statusCode: +res.success,
                    msgDesc: res.response.message || res.response.error
                }
            });
        } catch (e) {
            Object.assign(this.connectionState, {
                inProgress: false,
                showTestConnectionMsg: true,
                testConnectionResponse: {
                    statusCode: 0,
                    msgDesc: "Failed to test connection"
                }
            });
        }
    }
    handleDelete = (model, coll) => {
        f._confirm.confirmDelete({
                children: <Fragment>Are you sure you want to delete <b>{model.name}</b> connection?</Fragment>,
            }).then((confirm) => {
                this.props.guardrailConnectionProviderStore.deleteGuardrailConnectionProvider(model.id, {
                        models: coll
                    })
                    .then((response) => {
                        f.notifySuccess(`The connection ${model.name} deleted successfully`);
                        confirm.hide();
                        f.handlePagination(coll, coll.params);
                        this.props.handlePostDelete?.();
                    }, f.handleError());
            }, () => {});
    }
    render() {
        return (
            <FSModal ref={ref => this.Modal = ref} maxWidth="md"
                className="connector-modal"
                dataResolve={this.handleSave}
            >
                <VGuardrailProviderBasicForm
                    connectionState={this.connectionState}
                    handleTestConnection={this.handleTestConnection}
                    form={this.form}
                    getPropertiesForm={this.getPropertiesForm}
                />
            </FSModal>
        )
    }
}

export default CGuardrailProviderForm;