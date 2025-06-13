import React, {useState, useEffect} from 'react';

import {Delete, Add} from '@material-ui/icons';
import FormLabel from '@material-ui/core/FormLabel';
import {Grid, Typography, Button} from '@material-ui/core';
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';
import {FormHorizontal, FormGroupInput, FormGroupSelect2, FormGroupRadioList} from 'common-ui/components/form_fields';
import f from 'common-ui/utils/f';

const SUPPORTED_METHODS = [
    { name: 'POST', value: 'POST' },
    { name: 'PUT', value: 'PUT' },
    { name: 'GET', value: 'GET' }
];

const VEvalTargetForm = (props) => {
    const { form, cApplications } = props;
    const {
        id,
        ai_application_id,
        name,
        connectionType,
        url,
        headers,
        body,
        transformResponse,
        method,
        username
    } = form.fields;

    // Initialize headers list from form field or default to empty array
    const authHeader = headers.value?.find(h => h.key?.toLowerCase() === 'authorization');
    const initialHeaders = headers.value?.filter(h => h.key?.toLowerCase() !== 'authorization') || [];
    if (authHeader) {
        initialHeaders.unshift(authHeader);
    }
    let initialAuthType = 'noauth';
    let initialToken = '';
    let initialPassword = '';
    if (authHeader) {
        const authValue = authHeader.value;
        if (authValue.startsWith('Basic ')) {
            try {
                const decoded = atob(authValue.replace('Basic ', '').trim());
                const [user, pass] = decoded.split(':');
                initialAuthType = 'basicauth';
                initialPassword = pass || '';
                username.value = user
            } catch (e) {
                console.warn('Invalid Basic Auth encoding');
            }
        } else {
            initialAuthType = 'bearertoken';
            initialToken = authValue.trim();
        }
    }
    const [headersList, setHeadersList] = useState(initialHeaders);
    const [authType, setAuthType] = useState(initialAuthType);
    const [password, setPassword] = useState(initialPassword);
    const [token, setToken] = useState(initialToken);
    const [applicationType, setApplicationType] = useState('ai_application');
    const fieldObj = {
        value: applicationType,
        fieldOpts: {
            values: [
                { id: 'ai_application', name: 'AI Application' },
                { id: 'custom', name: 'custom' }
            ],
        },
    };

    const handleRadioChange = (e) => {
        setApplicationType(e.target.value);
        if (e.target.value === 'custom') {
            name.value = generateReportName();
            ai_application_id.value = null;
        } else {
            let applications = cApplications?f.models(cApplications):[]
            if (applications.length > 0) {
                handleApplicationNameChange(applications[0]);
            }
        }
    };

    const handleApplicationNameChange = (option) => {
        if (!option) return;
        const selectedOption = Array.isArray(option) ? option[0] : option;
        name.value = selectedOption?.name || '';
        ai_application_id.value = selectedOption?.id || null;
    };

    // Update headers field in form
    const updateFormHeaders = (updatedHeaders) => {
        setHeadersList(updatedHeaders);
        headers.value = updatedHeaders;
    };

    const handleAddHeader = () => {
        updateFormHeaders([...headersList, { key: '', value: '' }]);
    };

    const handleRemoveHeader = (index) => {
        if (headersList.length > 1) {
            const updatedHeaders = headersList.filter((_, i) => i !== index);
            updateFormHeaders(updatedHeaders);
        } else {
            const updatedHeaders = headersList.map((header, i) => 
                i === index ? { key: '', value: '' } : header
            );
            updateFormHeaders(updatedHeaders);
        }
    };

    const handleHeaderChange = (index, key, value) => {
        const updatedHeaders = headersList.map((header, i) => 
            i === index ? { key, value } : header
        );
        updateFormHeaders(updatedHeaders);
    };

    const handleMethodChange = (method) => {
        form.fields.method.value = method;
    };


    const update_auths = () => {
        let newHeaders = headersList.filter(h => h.key.toLowerCase() !== 'authorization');
        if (authType === 'basicauth' && username.value && password) {
            const authValue = `Basic ${btoa(`${username.value}:${password}`)}`;
            newHeaders = [{ key: 'Authorization', value: authValue }, ...newHeaders];
        } else if (authType === 'bearertoken' && token) {
            newHeaders = [{ key: 'Authorization', value: `${token}` }, ...newHeaders];
        }
        updateFormHeaders(newHeaders);
    }

    const generateReportName = () => {
        const now = new Date();
        const formattedDate = now.toLocaleDateString('en-GB').split('/').reverse().join(''); // Format: DDMMYYYY
        const formattedTime = now.toLocaleTimeString('en-GB', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        }).replace(/:/g, '') + now.getMilliseconds().toString().padStart(3, '0'); // Format: HHmmssSSS
        return `eval-target-${formattedDate}${formattedTime}`;
    };

    useEffect(() => {
        if (applicationType === 'custom' && !id.value) {
            name.value = generateReportName();
        }
    }, [id.value, name]);

    useEffect(() => {
        update_auths()
    }, [authType, password, token]);

    const handleUsernameChange = (e) => {
        username.value = e.target.value
        update_auths()
    };

    useEffect(() => {
        if (!id.value) {
            let applications = cApplications?f.models(cApplications):[]
            if (applications.length > 0 && applicationType === 'ai_application') {
                handleApplicationNameChange(applications[0]);
            }
        }
    }, [cApplications]);

    
    return (
        <FormHorizontal>
            <Grid container spacing={3}>
                {!id.value &&<FormGroupRadioList
                    fieldObj={fieldObj}
                    onChange={handleRadioChange}
                    valueKey="id"
                    labelKey="name"
                    inputProps={{ 'data-testid': 'radio-button-app-type' }}
                />}
                {(applicationType==='custom' || id.value)? <FormGroupInput
                    inputColAttr={{ xs: 12, sm: 7 }}
                    disabled={ai_application_id.value}
                    required={true}
                    label={id ? "Name" : "Name (Auto Generated, Editable)"}
                    placeholder="Enter configuration name"
                    fieldObj={name}
                    inputProps={{ 'data-testid': 'name-input' }}
                />:
                <FormGroupSelect2
                    inputColAttr={{ xs: 12, sm: 7 }}
                    required={true}
                    label={"AI Applications"}
                    showLabel={true}
                    fieldObj={ai_application_id}
                    data={cApplications?f.models(cApplications):[]}
                    labelKey={'name'}
                    valueKey={'id'}
                    disableClearable={true}
                    onChange={(value, option) => handleApplicationNameChange(option)}
                    data-testid="application-name"
                />}
                <Grid item xs={12}>
                    <Typography variant="h7" gutterBottom>Target Details</Typography>
                </Grid>
                <FormGroupInput
                    inputColAttr={{ xs: 12, sm: 7 }}
                    label="Connection type"
                    placeholder="HTTP/HTTPS-Endpoint"
                    fieldObj={connectionType}
                    inputProps={{'data-testid': 'connection-type'}}
                    disabled={true}
                />
                <FormGroupInput
                    inputColAttr={{ xs: 12 }}
                    required={true}
                    label="Endpoint URL"
                    placeholder="http://127.0.0.1:3535/securechat/api/v1/conversations/prompt"
                    fieldObj={url}
                    inputProps={{'data-testid': 'endpoint-url'}}
                />
                <Grid item xs={12}>
                    <Typography variant="h7" gutterBottom>Endpoint Configuration</Typography>
                </Grid>
                <FormGroupSelect2
                    inputColAttr={{ xs: 12, sm: 7 }}
                    required={true}
                    label={"Method"}
                    showLabel={true}
                    fieldObj={method}
                    data={SUPPORTED_METHODS}
                    labelKey={'name'}
                    valueKey={'value'}
                    disableClearable={true}
                    onChange={handleMethodChange}
                    data-testid="method"
                />
                <FormGroupSelect2
                    inputColAttr={{ xs: 12, sm: 7 }}
                    label="Authorization Type"
                    data={[
                        { label: 'No Auth', value: 'noauth' },
                        { label: 'Basic Auth', value: 'basicauth' },
                        { label: 'Bearer Token', value: 'bearertoken' }
                    ]}
                    value={authType}
                    onChange={(value) => setAuthType(value)}
                    required={true}
                    multiple={false}
                    disableClearable={true}
                />
                <FormGroupInput
                    inputColAttr={{ xs: 12, sm: 7 }}
                    required={true}
                    label="Username - user as target user for AI Application"
                    placeholder="Enter username"
                    fieldObj={username}
                    onChange={(value) =>handleUsernameChange(value)}
                    inputProps={{ 'data-testid': 'name-input-username' }}
                />
                {authType === 'basicauth' && (<FormGroupInput
                        inputColAttr={{ xs: 12, sm: 7 }}
                        label={'Password'}
                        type={'password'}
                        value={password}
                        placeholder="password"
                        inputProps={{ 'data-testid': 'userpassword-input' }}
                        onChange={(e) => setPassword(e.target.value)}
                      />)}
                {authType === 'bearertoken' && (<FormGroupInput
                        inputColAttr={{ xs: 12, sm: 7 }}
                        required={true}
                        label={"Bearer Token"}
                        value={token}
                        placeholder="Bearer <token>"
                        inputProps={{ 'data-testid': 'token-input' }}
                        onChange={(e) => setToken(e.target.value)}
                        />
                 )}
                {/* Headers Section */}
                <Grid item xs={12}>
                <FormLabel>Headers</FormLabel>
                    {headersList.map((header, index) => (
                        <Grid container spacing={2} alignItems="center" key={index}>
                            <FormGroupInput
                                inputColAttr={{ xs: 5 }}
                                value={header.key}
                                onChange={(e) => handleHeaderChange(index, e.target.value, header.value)}
                                placeholder="Header"
                                inputProps={{ 'data-testid': `header-key-${index}` }}
                                disabled={header.key.toLowerCase() === 'authorization'}
                            />
                            <FormGroupInput
                                inputColAttr={{ xs: 5 }}
                                value={header.value}
                                onChange={(e) => handleHeaderChange(index, header.key, e.target.value)}
                                placeholder="Value"
                                inputProps={{ 'data-testid': `header-value-${index}` }}
                                disabled={header.key.toLowerCase() === 'authorization'}
                            />
                            {header.key.toLowerCase() !== 'authorization' && (
                            <Grid item xs={2}>
                                <CustomAnchorBtn
                                    tooltipLabel="Delete"
                                    color="primary"
                                    onClick={() => handleRemoveHeader(index)}
                                    icon={<Delete />}
                                />
                            </Grid>
                            )}
                        </Grid>
                    ))}

                    {/* Add Header Button */}
                    <Grid item xs={12}>
                        <Button
                            variant="outlined"
                            color="primary"
                            startIcon={<Add className='m-l-sm'/>}
                            onClick={handleAddHeader}
                            size="small"
                            className='m-t-sm'
                        >
                        </Button>
                    </Grid>
                </Grid>

                <FormGroupInput
                    required={true}
                    as="textarea"
                    label="Request Body"
                    placeholder={`{\n "ai_application_name": "sales_model",\n"prompt": "{{prompt}}"\n}`}
                    fieldObj={body}
                    inputProps={{
                        'data-testid': 'request-body',
                        rows: 4
                    }}
                />

                <FormGroupInput
                    as="textarea"
                    label="Response Transform"
                    placeholder={"json.messages && json.messages.length > 0 \n  ? (json.messages.find(message => message.type === 'reply') || {}).content || \"No reply found.\"\n  : \"No response from the server.\"\n"}
                    fieldObj={transformResponse}
                    inputProps={{
                        'data-testid': 'response-transform',
                        rows: 4
                    }}
                />
            </Grid>
        </FormHorizontal>
    );
};

const eval_target_form_def = {
    id: {},
    status: {},
    ai_application_id: {},
    target_id: {},
    desc: {},
    name: {
        validators: {
            errorMessage: 'Name is required!',
            fn: (field) => (field.value || '').trim().length > 0
        }
    },
    username: {
        validators: {
            errorMessage: 'Username is required!',
            fn: (field) => (field.value || '').trim().length > 0
        }
    },
    connectionType: {
        defaultValue: 'HTTP/HTTPS-Endpoint'
    },
    url: {
        validators: {
            errorMessage: 'Endpoint URL is required!',
            fn: (field) => (field.value || '').trim().length > 0
        }
    },
    headers: {
        defaultValue: []
    },
    body: {
        validators: {
            errorMessage: 'Request body is required!',
            fn: (field) => (field.value || '').trim().length > 0
        }
    },
    transformResponse: {},
    method: {
        defaultValue: 'POST'
    }

};

export {
    eval_target_form_def
}

export {VEvalTargetForm};