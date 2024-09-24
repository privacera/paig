import { observer } from 'mobx-react';
import React, { Component, Fragment } from "react";

import { Card, CardContent, Grid, Typography } from '@material-ui/core';
import VerifiedUserIcon from '@material-ui/icons/VerifiedUser';
import Alert from '@material-ui/lab/Alert';

import { AddButtonWithPermission, CustomAnchorBtn } from "common-ui/components/action_buttons";
import { FormGroupInput } from 'common-ui/components/form_fields';
import { Loader, getSkeleton } from 'common-ui/components/generic_components';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import { BookIcon } from 'components/site/privacera_logo';
import { REGEX, FEATURE_PERMISSIONS } from 'utils/globals';

@observer
class VShieldConfigForm extends Component {
    constructor(props){
        super(props);
		this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.ACCOUNT.SHIELD_CONFIGURATION.PROPERTY);
    }

    render() {
        const {_vState, form, handleShieldConfigDownload, handleSave} = this.props;
        const {isLoading, showAlert} = _vState;
        const { shieldServerUrl, shieldAuditServerUrl } = form.fields;

        return (
            <Fragment>
                <Grid container spacing={3}>
                    <Grid item xs={12} md={8} lg={6}>
                        <Card>
                            <CardContent style={{padding: '32px'}}>
                                <Grid container spacing={1} direction="row" >
                                    <Grid item >
                                        <VerifiedUserIcon className="heading-icon" />
                                    </Grid>
                                    <Grid item style={{flexGrow: 1}}>
                                        <Typography className="m-b-sm color-medium-grey" variant="h6">
                                            Shield Configuration
                                            <CustomAnchorBtn
                                                tooltipLabel="Documentation"
                                                className="doc-link"
                                                data-track-id="shield-documentation"
                                                onClick={() => {
                                                    window.open("docs/integration/self-managed-privacera-shield.html", '_blank')
                                                }}
                                                icon={<BookIcon />}
                                            />
                                        </Typography>
                                        <Typography>Default configuration for audit logs storage to PAIG.</Typography>
                                    </Grid>
                                </Grid>
                                <Typography className="m-t-md m-b-md" variant="body1">Why application configuration:</Typography>
                                <ul>
                                    <li>Use your own storage service for storing data.</li>
                                    <li>Can setup storage policies.</li>
                                    <li>Audit logs in your storage can be de-anonymised.</li>
                                    <li>API Access.</li>
                                </ul>  
                                <Loader isLoading={isLoading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                                    <Grid container spacing={3}>
                                        <FormGroupInput
                                            inputColAttr={{xs: 12}}
                                            required={true}
                                            label="Privacera Shield Service Endpoint URL"
                                            fieldObj={shieldServerUrl}
                                            onChange={(e) => shieldServerUrl.value = e.target.value.trim()}
                                            data-testid="config-url"
                                            data-track-id="shield-config-url"
                                        />
                                        <FormGroupInput
                                            inputColAttr={{xs: 12}}
                                            label="Audit Service Endpoint URL"
                                            fieldObj={shieldAuditServerUrl}
                                            onChange={(e) => shieldAuditServerUrl.value = e.target.value.trim()}
                                            data-testid="audit-endpoint-url"
                                            data-track-id="audit-endpoint-url"
                                        />
                                    </Grid>
                                    <Grid container spacing={3}>
                                        <AddButtonWithPermission
                                            permission={this.permission}
                                            label="Apply"
                                            variant="outlined"
                                            onClick={handleSave}
                                            className="pull-right m-t-sm"
                                            colAttr={{
                                                xs: 12,
                                                'data-testid': 'save-btn-grid',
                                                'data-track-id': 'shield-save-btn'
                                            }}
                                        />
                                    </Grid>
                                    <Grid container spacing={3} direction="column" >
                                        {showAlert && 
                                            <Grid item xs={12}>
                                                <Alert data-testid="download-alert" severity="error">
                                                    Please enter config url and save before downloading
                                                </Alert>
                                            </Grid>
                                        }
                                        <AddButtonWithPermission
                                            fullWidth={true}
                                            permission={this.permission}
                                            label="Download Shield Configuration"
                                            onClick={handleShieldConfigDownload}
                                            colAttr={{
                                                xs: 12,
                                                'data-testid': "download-btn-grid",
                                                className: "config-save-btn",
                                                'data-track-id': 'shield-download-btn'
                                            }}
                                        />
                                    </Grid>
                                </Loader>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Fragment>
        )
    }
}

const shield_config_form_def = {
    shieldServerUrl:{
        defaultValue: "",
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                if (field.value.trim().length > 0) {
                    if(!REGEX.VALID_URL.test(field.value)){
                        field._originalErrorMessage = "Invalid URL!";
                        return false;
                    }
                    return true;
                }
                return false;
            }
        }
    },
    shieldAuditServerUrl: {
        defaultValue: "",
        validators: {
            errorMessage: '',
            fn: (field) => {
                if (field.value.trim().length > 0 && !REGEX.VALID_URL.test(field.value)) {
                    field._originalErrorMessage = "Invalid URL!";
                    return false;
                }
                return true;
            }
        }
    }
}

export default VShieldConfigForm;
export {
    shield_config_form_def
}