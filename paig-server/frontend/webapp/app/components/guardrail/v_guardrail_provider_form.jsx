import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';

import {Grid, Box, Button, CircularProgress, Typography} from '@material-ui/core';
import {Alert} from '@material-ui/lab';

import { FormHorizontal, FormGroupInput, FormGroupRadioList } from 'common-ui/components/form_fields';
import {GUARDRAIL_PROVIDER, AWS_PROVIDER_CONNECTION_CONFIG_TYPE} from 'utils/globals';

const VGuardrailProviderBasicForm = ({form, getPropertiesForm, connectionState, handleTestConnection}) => {
    const {name, description, guardrailsProvider} = form.fields;

    const provider = Object.values(GUARDRAIL_PROVIDER).find(p => p.NAME === guardrailsProvider.value);

    return (
        <div className="application-connector-modal">
            <div className="application-connector-left">
                <div>
                    <div className="connector-modal-tab-left pointer active">
                        <div className="connector-container" data-testid="connector-container">
                            <div className="connector-icon">
                                {
                                    provider && provider.IMG_URL &&
                                    <div className="appstore-landing-container">
                                        <div className="connector-widget">
                                            <img className="services-logo" src={provider.IMG_URL} alt="service-logo" />
                                        </div>
                                    </div>
                                }
                            </div>
                            <div className="connector-text" data-testid="connector-name">{provider?.LABEL || guardrailsProvider.value}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="application-nav-card-content">
                <div className="app-content-scroll">
                    <div className="app-content-padding">
                        <form autoComplete="off">
                            <FormHorizontal>
                                <FormGroupInput
                                    required={true}
                                    label="Connection Name"
                                    fieldObj={name}
                                    inputColAttr={{
                                        xs: 12,
                                        'data-testid': 'name'
                                    }}
                                />
                                <FormGroupInput
                                    as="textarea"
                                    rows={1}
                                    rowsMax={5}
                                    label="Connection Description"
                                    fieldObj={description}
                                    inputColAttr={{
                                        xs: 12,
                                        'data-testid': 'description'
                                    }}
                                />
                                {
                                    getProviderForm(guardrailsProvider.value, getPropertiesForm())
                                }
                                <Grid item xs={12}>
                                    <TestConnectionButton
                                        connectionState={connectionState}
                                        onClick={handleTestConnection}
                                    />
                                </Grid>
                            </FormHorizontal>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}

const TestConnectionButton = observer(({
  connectionState, onClick, containerProps={}, buttonProps={}, alertClassName = ''
}) => {

    return (
        <Box className="m-t-xs" {...containerProps}>
            <Button color="primary" variant="outlined" data-testid="test-connection" aria-label="Test Connection"
                onClick={onClick}
                {...buttonProps}
            >Test Connection
            </Button>
            {connectionState && (connectionState.inProgress || connectionState.showTestConnectionMsg) &&
                <Box mt={"10px"} className={"w-b-bw "+ alertClassName} data-testid="connection-status">
                    <Alert severity={connectionState.inProgress ? 'warning' : connectionState.testConnectionResponse.statusCode == 1 ? 'success' : 'error'}
                        icon={connectionState.inProgress ? <CircularProgress size="20px" /> : null}
                    >
                        {connectionState.inProgress && 'Connecting'}
                        {connectionState.showTestConnectionMsg && (connectionState.testConnectionResponse.msgDesc || 'No Response')}
                    </Alert>
                </Box>
            }
        </Box>
    )
});

const AWSProviderForm = observer(({form}) => {
    const {config_type, access_key, secret_key, session_token, iam_role, region} = form.fields;

    let fields = [
        <FormGroupRadioList
            key="config_type"
            label="Connection Type"
            fieldObj={config_type}
            labelKey="LABEL"
            valueKey="TYPE"
            inputColAttr={{
                xs: 12,
                'data-testid': "config-type"
            }}
        />
    ];

    if (config_type.value === AWS_PROVIDER_CONNECTION_CONFIG_TYPE.IAM_ROLE.TYPE) {
        fields.push(
            <FormGroupInput
                key="iam_role"
                required={true}
                label="IAM Role"
                fieldObj={iam_role}
                inputColAttr={{
                    xs: 12,
                    'data-testid': 'iam-role'
                }}
            />
        )
    } else if (config_type.value === AWS_PROVIDER_CONNECTION_CONFIG_TYPE.ACCESS_SECRET_KEY.TYPE) {
        fields.push(...[
            <FormGroupInput
                key="access_key"
                required={true}
                label="Access Key"
                fieldObj={access_key}
                inputColAttr={{
                    xs: 12,
                    'data-testid': 'access-key'
                }}
            />,
            <FormGroupInput
                key="secret_key"
                required={true}
                type="password"
                label="Secret Key"
                fieldObj={secret_key}
                inputColAttr={{
                    xs: 12,
                    'data-testid': 'secret-key'
                }}
            />,
            <FormGroupInput
                key="session_token"
                label="Session Token"
                fieldObj={session_token}
                inputColAttr={{
                    xs: 12,
                    'data-testid': 'session-token'
                }}
            >
                <Typography variant="caption">
                    Session token is a short-lived token for temporary access.
                </Typography>
            </FormGroupInput>
        ]);
    }

    if (config_type.value !== AWS_PROVIDER_CONNECTION_CONFIG_TYPE.INSTANCE_ROLE.TYPE) {
        fields.push(
            <FormGroupInput
                required={true}
                label="Region"
                fieldObj={region}
                inputColAttr={{
                    xs: 12,
                    'data-testid': 'region'
                }}
            />
        )
    }

    return (
        <Fragment>
            {fields}
        </Fragment>
    )
})

const getProviderForm = (provider, propertiesForm) => {
    switch (provider) {
        case GUARDRAIL_PROVIDER.AWS.NAME:
            return (
                <AWSProviderForm form={propertiesForm} />
            )
        default:
            return null;
    }
}

const guardrail_provider_form_def = {
    name: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                return (field.value || '').trim().length > 0;
            }
        }
    },
    description: {},
    guardrailsProvider: {}
}

const aws_provider_form_def = {
    config_type: {
        defaultValue: AWS_PROVIDER_CONNECTION_CONFIG_TYPE.IAM_ROLE.TYPE,
        fieldOpts: {
            values: Object.values(AWS_PROVIDER_CONNECTION_CONFIG_TYPE)
        }
    },
    access_key: {
        validators: {
            errorMessage: 'Required!',
            fn: (field, fields) => {
                if (fields.config_type.value !== AWS_PROVIDER_CONNECTION_CONFIG_TYPE.ACCESS_SECRET_KEY.TYPE) {
                    return true;
                }
                return (field.value || '').trim().length > 0;
            }
        }
    },
    secret_key: {
        validators: {
            errorMessage: 'Required!',
            fn: (field, fields) => {
                if (fields.config_type.value !== AWS_PROVIDER_CONNECTION_CONFIG_TYPE.ACCESS_SECRET_KEY.TYPE) {
                    return true;
                }
                return (field.value || '').trim().length > 0;
            }
        }
    },
    session_token: {},
    iam_role: {
        validators: {
            errorMessage: 'Required!',
            fn: (field, fields) => {
                if (fields.config_type.value !== AWS_PROVIDER_CONNECTION_CONFIG_TYPE.IAM_ROLE.TYPE) {
                    return true;
                }
                let val = (field.value || '').trim();
                if (val.length === 0) {
                    field._originalErrorMessage = 'Required!';
                    return false;
                }
                if (val.length < 20) {
                    field._originalErrorMessage = 'Minimum length required is 20 characters!';
                    return false;
                }
                return true;
            }
        }
    },
    region: {
        validators: {
            errorMessage: 'Required!',
            fn: (field, fields) => {
                if (fields.config_type.value === AWS_PROVIDER_CONNECTION_CONFIG_TYPE.INSTANCE_ROLE.TYPE) {
                    return true;
                }
                return (field.value || '').trim().length > 0;
            }
        }
    }
}

const paig_provider_form_def = {
}

const provider_form_def = {
    [GUARDRAIL_PROVIDER.AWS.NAME]: aws_provider_form_def,
    [GUARDRAIL_PROVIDER.PAIG.NAME]: paig_provider_form_def
}

export {
    VGuardrailProviderBasicForm,
    guardrail_provider_form_def,
    provider_form_def
}