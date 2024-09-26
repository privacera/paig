import { observable } from "mobx";
import { inject } from 'mobx-react';
import React, { Component, Fragment } from "react";

import { Typography } from "@material-ui/core";

import { createFSForm } from 'common-ui/lib/form/fs_form';
import f from 'common-ui/utils/f';
import BaseContainer from 'containers/base_container';
import VShieldConfigForm, {shield_config_form_def} from "components/shield_configuration/v_shield_configuration_form";

@inject('aiApplicationStore', 'shieldConfigStore')
class CShieldConfig extends Component {
    constructor(props){
        super(props);
        this.form = createFSForm(shield_config_form_def);
    }
    
    @observable _vState = {
        showAlert: false,
        shieldObj: null,
        isLoading: true,
    }

    componentDidMount() {
        this.handleRefresh();
    }

    handleRefresh = () => {
        this.fetchConfigUrl();
    }

    fetchConfigUrl = async () => {
		this._vState.isLoading = true;
        this._vState.showAlert = false

        try {
            let resp = await this.props.shieldConfigStore.getConfigUrl();
            this._vState.shieldObj = resp;
            this.form.refresh(resp);
            this._vState.isLoading = false;
        } catch(e) {
			this._vState.isLoading = false;
            f.handleError()(e);
        }
    }

    handleShieldConfigDownload = async () => {
        await this.form.validate();
        let data = this.form.toJSON();
        let initialUrl = this._vState.shieldObj?.shieldServerUrl?.trim();
        let changedUrl = data.shieldServerUrl;
        let isUrlChanged = initialUrl !== changedUrl || this._vState.shieldObj?.shieldAuditServerUrl?.trim() !== data.shieldAuditServerUrl;

        if (!this.form.valid || isUrlChanged) {
            this._vState.showAlert = true;
            return;
        }
        this._vState.showAlert = false;

        let url = this.props.aiApplicationStore.downloadShieldConfig();
        window.open(url, '_blank');
    }

    handleSave = async () => {
        let data = this.form.toJSON();
        let initialUrl = this._vState.shieldObj?.shieldServerUrl?.trim();
        let isUrlChanged = initialUrl !== data.shieldServerUrl || this._vState.shieldObj?.shieldAuditServerUrl?.trim() !== data.shieldAuditServerUrl;

        await this.form.validate();
        if (!this.form.valid) {
            return;
        }

        if(!initialUrl && isUrlChanged) {
            this.saveConfigUrl();
        } else if(isUrlChanged) {
            this.handleOnSaveClick();
        } else {
            this._vState.showAlert = false;
            f.notifyInfo("Config Url is unchanged");
        }
    }

    handleOnSaveClick = async () => {
        f._confirm.show({
            title: `Attention: PAIG Shield Service Endpoint Update`,
            children: (
                <Fragment>
                    <Typography>
                        You are about to change the PAIG Shield Service Endpoint URL. This update is a significant configuration change for the Self Managed PAIG Shield. Please take note of the following critical steps:
                    </Typography>
                    <ol>
                        <li>
                            <Typography className="m-t-md">
                                Download New Configuration File: Post-update, it is mandatory to download the new application configuration files. This is essential for aligning your applications with the updated PAIG Shield Service Endpoint.
                            </Typography>
                        </li>
                        <li>
                            <Typography>
                                Restart Applications: After updating the configuration file, you must restart all applications that are utilizing the Self Managed Privacera Shield to ensure they function correctly with the new settings.
                            </Typography>

                        </li>
                    </ol>
                </Fragment>
            ),
            btnCancelText: 'Cancel',
            btnOkText: 'Save',
            btnOkColor: 'primary',
            btnOkVariant: 'contained'
        })
        .then((confirm) => {
            this.saveConfigUrl(confirm);
        }, () => {});
    }

    saveConfigUrl = async (confirm) => {
        let data = this.form.toJSON();

        try {
            await this.props.shieldConfigStore.saveConfigUrl({params: data});
            confirm?.hide();
            f.notifySuccess("Config Url saved successfully");
            this._vState.showAlert = false;
            this.fetchConfigUrl();
        } catch(e) {
            f.handleError()(e);
        }
    }
 
  render() {
    const { handleShieldConfigDownload, handleSave, _vState } = this;

    return (
        <BaseContainer handleRefresh={this.handleRefresh}>
            <VShieldConfigForm
                handleShieldConfigDownload={handleShieldConfigDownload}
                handleSave={handleSave}
                _vState={_vState}
                form={this.form}
            />
        </BaseContainer>
    )
  }
}

export default CShieldConfig;