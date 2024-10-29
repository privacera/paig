import React, {Component, Fragment} from 'react';
import {observer, inject} from 'mobx-react';
import {observable} from 'mobx';

import { Grid, Card, CardContent, Button, Typography, Paper, Box }  from "@material-ui/core";
import CircularProgress from "@material-ui/core/CircularProgress/CircularProgress";
import FormLabel from '@material-ui/core/FormLabel';

import UiState from 'data/ui_state';
import VAIApplicationForm, {ai_application_form_def, application_guardrail_form_def} from 'components/applications/ai_applications/v_ai_application_form';
import {configProperties} from 'utils/config_properties';
import {DEPLOYMENT_TYPE} from 'utils/globals';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import {CanUpdate, ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {FormGroupSwitch} from 'common-ui/components/form_fields';
import OrderList from 'common-ui/components/order_list';

@inject('aiApplicationStore')
@observer
class CAIApplicationForm extends Component {
    @observable _vState = {
        editMode: false,
        saving: false
    }
    constructor(props) {
        super(props);

        const application = props.application || {};

        this.form = createFSForm(ai_application_form_def);
        this.guardrailForm = createFSForm(application_guardrail_form_def);

        if (application.id) {
            this.handleFormRefresh(application);
        }
    }
    handleEdit = () => {
        this._vState.editMode = true;
    }
    handleFormRefresh(application) {
        this.form.refresh(application);
        if (application.guardrailDetails) {
            this.guardrailForm.refresh(Utils.parseJSON(application.guardrailDetails));
        } else {
            this.guardrailForm.clearForm();
        }
    }
    handleCancelEdit = () => {
        this._vState.editMode = false;
        this.handleFormRefresh(this.props.application);
    }

    handleCreate = async () => {
        let valid = await this.form.validate();
        let guardrailDetailsValid = await this.guardrailForm.validate();
        if (!this.form.valid || !this.guardrailForm.valid) {
            return;
        }
        let data = this.form.toJSON();
        delete data.id;

        let guardrailDetails = this.guardrailForm.toJSON();
        if (guardrailDetails.guardrail_enable) {
            data.guardrailDetails = JSON.stringify(guardrailDetails);
        } else {
            data.guardrailDetails = null;
        }

        // TODO remove this from body
        data.tenantId = UiState.getTenantId();

        if (typeof data.vectorDBs === 'string') {
            data.vectorDBs = data.vectorDBs.split(',').filter(db => db);
        }

        try {
            this._vState.saving = true;

            let response = await this.props.aiApplicationStore.createAIApplication(data, UiState.getHeaderWithTenantId());
            f.notifySuccess("The AI Application created successfully");
            this.props.handlePostCreate?.(response);
        } catch(e) {
            this._vState.saving = false;
            f.handleError()(e);
        }
    }
    handleUpdate = async () => {
        let valid = await this.form.validate();
        let guardrailDetailsValid = await this.guardrailForm.validate();
        if (!this.form.valid || !this.guardrailForm.valid) {
            return;
        }
        let data = this.form.toJSON();
        let guardrailDetails = this.guardrailForm.toJSON();
        if (guardrailDetails.guardrail_enable) {
            data.guardrailDetails = JSON.stringify(guardrailDetails);
        } else {
            data.guardrailDetails = null;
        }

        if (typeof data.vectorDBs === 'string') {
            data.vectorDBs = data.vectorDBs.split(',').filter(db => db);
        }

        let {application} = this.props;
        data = Object.assign({}, application, data);

        try {
            this._vState.saving = true;
            let response = await this.props.aiApplicationStore.updateAIApplication(data, UiState.getHeaderWithTenantId())
            f.notifySuccess("The AI Application updated successfully");
            this.props.handlePostUpdate?.(data.id);
        } catch(e) {
            this._vState.saving = false;
            f.handleError()(e);
        }
    }
    handleConfigToggle = (e) => {
        let deploymentType = e.target.checked ? DEPLOYMENT_TYPE.SELF_MANAGED.VALUE : DEPLOYMENT_TYPE.CLOUD.VALUE;

        f._confirm.show({
            title: `Update Privacera Shield Endpoint`,
            children: <Fragment>Are you sure you want to <b>{e.target.checked ? 'Enable' : 'Disable'}</b> the <b>Self Managed Privacera Shield</b>?</Fragment>,
            btnCancelText: 'Cancel',
            btnOkText: 'Save',
            btnOkColor: 'primary',
            btnOkVariant: 'contained'
        })
        .then((confirm) => {
            let data = Object.assign({}, this.props.application, {deploymentType});

            this.props.aiApplicationStore.updateAIApplication(data)
            .then((response) => {
                confirm.hide();
                f.notifySuccess('Updated Privacera Shield Endpoint Successfully');
                this.props.handlePostUpdate?.(data.id);
            }, f.handleError(null, ()=>{
            }, {confirm}));
        }, () => {});
    }

    render() {
        const {application, permission, handleCancel} = this.props;
        const {handleCreate, handleUpdate} = this;

        return (
            <Fragment>
                <Box component={Paper} className={`m-t-sm ${ application?.id ? 'm-b-md' : 'm-b-sm'}`}>
                    <Grid container spacing={3} style={{padding: '5px 15px'}} data-track-id="application-info">
                        <Grid item sm={8} xs={12}>
                            <Typography variant="h6" component="h2">
                                Information
                            </Typography>
                        </Grid>
                        <Grid item sm={4} xs={12} className="text-right">
                            {
                                application?.id != null && !this._vState.editMode &&
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
                                        variant="contained"
                                        color="primary"
                                        className="m-r-sm"
                                        size="small"
                                        disabled={this._vState.saving}
                                        onClick={handleUpdate}
                                        data-testid="edit-save-btn"
                                        data-track-id="app-edit-save-btn"
                                    >
                                        {
                                            this._vState.saving &&
                                            <CircularProgress size="15px" className="m-r-xs" />
                                        }
                                        SAVE
                                    </Button>
                                    <Button
                                        variant="outlined"
                                        color="primary"
                                        size="small"
                                        onClick={this.handleCancelEdit}
                                        data-testid="edit-cancel-btn"
                                        data-track-id="app-edit-cancel-btn"
                                    >CANCEL</Button>
                                </div>
                            }
                        </Grid>
                        <VAIApplicationForm
                            form={this.form}
                            guardrailForm={this.guardrailForm}
                            editMode={this._vState.editMode}
                        />
                    </Grid>
                </Box>
                {/* TODO: [PAIG-2025] Uncomments to enable Shield Configuration */}
                {/* <Fragment>
                    {
                        configProperties.isShieldConfigEnable() && application.id &&
                        <Box className="m-b-md m-t-lg">
                            <Card>
                                <CardContent>
                                    <Typography variant="body1">Switch Privacera Shield Endpoint</Typography>
                                    <Typography className="m-t-sm" component="div" variant="body2">
                                        You are about to switch the hosting location of the Privacera Shield. Please be aware of the following important steps:
                                    </Typography>
                                    <OrderList>
                                        <li>
                                            <Typography component="span" variant="body2">
                                                Download New Configuration: After switching, it's essential to download a new application configuration file tailored to the new hosting environment.
                                            </Typography>
                                        </li>
                                        <li>
                                            <Typography component="span" variant="body2">
                                                Update Your Application:  Ensure to update your application with the newly downloaded configuration to maintain seamless functionality and security.
                                            </Typography>
                                        </li>
                                    </OrderList>
                                    <Grid item xs={12} className="m-t-lg">
                                        <FormLabel>Self Managed Privacera Shield</FormLabel>
                                        <FormGroupSwitch
                                            showLabel={false}
                                            checked={application.deploymentType === DEPLOYMENT_TYPE.SELF_MANAGED.VALUE}
                                            onChange={this.handleConfigToggle}
                                            inputColAttr={{ xs: 12}}
                                            data-testid="self-managed-status"
                                        />
                                    </Grid>
                                </CardContent>
                            </Card>
                        </Box>
                    }
                </Fragment> */}
                {
                    application?.id == null &&
                    <CanUpdate permission={permission}>
                        <Grid container spacing={3} className="m-t-md">
                            <Grid item xs={12}>
                                <Button
                                    variant="contained"
                                    color="primary"
                                    className="m-r-sm"
                                    disabled={this._vState.saving}
                                    onClick={handleCreate}
                                    data-testid="create-app-btn"
                                    data-track-id="create-app-btn"
                                >
                                    {
                                        this._vState.saving &&
                                        <CircularProgress size="18px" className="m-r-xs" />
                                    }
                                    CREATE
                                </Button>
                                <Button
                                    data-testid="cancel-btn"
                                    data-track-id="cancel-create-app-btn"
                                    variant="contained"
                                    onClick={handleCancel}
                                >
                                    CANCEL
                                </Button>
                            </Grid>
                        </Grid>
                    </CanUpdate>
                }
            </Fragment>
        );
    }
}

export default CAIApplicationForm;