import React, {useState, useEffect} from 'react';

import {Delete, Add} from '@material-ui/icons';
import FormLabel from '@material-ui/core/FormLabel';
import {Grid, Typography, IconButton, Button} from '@material-ui/core';

import {FormHorizontal, FormGroupInput, FormGroupSelect2} from 'common-ui/components/form_fields';

const SUPPORTED_METHODS = [
    { name: 'POST', value: 'POST' },
    { name: 'PUT', value: 'PUT' },
    { name: 'GET', value: 'GET' }
];

const VEvalTargetForm = ({form}) => {

    const {
        id,
        ai_application_id,
        name,
        connectionType,
        url,
        headers,
        body,
        transformResponse,
        method
    } = form.fields;

    // Initialize headers list from form field or default to empty array
    const initialHeaders = headers.value && headers.value.length > 0 ? headers.value : [{ key: '', value: '' }];
    const [headersList, setHeadersList] = useState(initialHeaders);

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

    useEffect(() => {
        const generateReportName = () => {
            if (!id.value) {
                const now = new Date();
                const formattedDate = now.toLocaleDateString('en-GB').split('/').reverse().join(''); // Format: DDMMYYYY
                const formattedTime = now.toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit',
                }).replace(':', ''); // Format: HHmm
                return `eval-target-${formattedDate}${formattedTime}`;
            }
            return name.value;
        };
    
        name.value = generateReportName();
    }, [id.value, name]);

    return (
        <FormHorizontal>
            <Grid container spacing={3}>
                <FormGroupInput
                    inputColAttr={{ xs: 12, sm: 6 }}
                    disabled={ai_application_id.value}
                    required={true}
                    label={id ? "Name" : "Name (Auto Generated, Editable)"}
                    placeholder="Enter configuration name"
                    fieldObj={name}
                    inputProps={{ 'data-testid': 'name-input' }}
                />
                <Grid item xs={12}>
                    <Typography variant="h7" gutterBottom>Target Details</Typography>
                </Grid>
                <FormGroupInput
                    inputColAttr={{ xs: 12, sm: 4 }}
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
                    inputColAttr={{ xs: 12, sm: 4 }}
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
                {/* Headers Section */}
                <Grid item xs={12}>
                <FormLabel>Headers</FormLabel>
                    {headersList.map((header, index) => (
                        <Grid container spacing={2} alignItems="center" key={index}>
                            <FormGroupInput
                                inputColAttr={{ xs: 5 }}
                                value={header.key}
                                onChange={(e) => handleHeaderChange(index, e.target.value, header.value)}
                                placeholder="Authorization"
                                inputProps={{ 'data-testid': `header-key-${index}` }}
                            />
                            <FormGroupInput
                                inputColAttr={{ xs: 5 }}
                                value={header.value}
                                onChange={(e) => handleHeaderChange(index, header.key, e.target.value)}
                                placeholder="Bearer {{api_key}}"
                                inputProps={{ 'data-testid': `header-value-${index}` }}
                            />
                            <Grid item xs={2}>
                                <IconButton onClick={() => handleRemoveHeader(index)} color="primary">
                                    <Delete />
                                </IconButton>
                            </Grid>
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
    ai_application_id: {},
    target_id: {},
    desc: {},
    name: {
        validators: {
            errorMessage: 'Name is required!',
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
        defaultValue: [{ key: 'Authorization', value: 'Bearer {{api_key}}' }]
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