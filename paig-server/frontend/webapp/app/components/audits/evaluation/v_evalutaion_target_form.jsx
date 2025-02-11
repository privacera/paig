import React, {useState} from 'react';

import { Grid, Typography, IconButton, Button } from '@material-ui/core';
import { Delete, Add } from '@material-ui/icons';

import { FormHorizontal, FormGroupInput, FormGroupSelect2 } from 'common-ui/components/form_fields';

const SUPPORTED_METHODS = [
    { name: 'POST', value: 'POST' },
    { name: 'PUT', value: 'PUT' },
    { name: 'GET', value: 'GET' }
];

const VEvalTargetForm = ({form}) => {

    const {
        id,
        name,
        connectionType,
        url,
        headers,
        requestBody,
        responseTransform,
        config,
        method
    } = form.fields;

    const [headersList, setHeadersList] = useState([{ key: '', value: '' }]);

    const handleAddHeader = () => {
        setHeadersList([...headersList, { key: '', value: '' }]);
    };

    const handleRemoveHeader = (index) => {
        if (headersList.length > 1) {
            const updatedHeaders = headersList.filter((_, i) => i !== index);
            setHeadersList(updatedHeaders);
        }
    };

    const handleMethodChange = (method) => {
        form.fields.method.value = method;
    };

    return (
        <FormHorizontal>
            <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                    <FormGroupInput
                        required={true}
                        label={id?.value ? "Name" : "Name (Auto Generated, Editable)"}
                        placeholder="Enter name of the topic"
                        fieldObj={name}
                        inputProps={{ 'data-testid': 'name-input' }}
                    />
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="h7" gutterBottom>Target Details</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                    <FormGroupInput
                        required={true}
                        label="Connection type"
                        placeholder="HTTP/HTTPS-Endpoint"
                        fieldObj={connectionType}
                        inputProps={{'data-testid': 'connection-type'}}
                    />
                </Grid>
                <Grid item xs={12}>
                    <FormGroupInput
                        required={true}
                        label="Endpoint URL"
                        placeholder="http://127.0.0.1:3535/securechat/api/v1/conversations/prompt"
                        fieldObj={url}
                        inputProps={{'data-testid': 'endpoint-url'}}
                    />
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="h7" gutterBottom>Endpoint Configuration</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>  
                    <FormGroupSelect2
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
                </Grid>

                {/* Headers Section */}
                <Grid item xs={12}>
                    <Typography variant="h7" gutterBottom>Headers</Typography>
                </Grid>
                <Grid item xs={12}>
                    {headersList.map((header, index) => (
                        <Grid container spacing={2} alignItems="center" key={index}>
                            <Grid item xs={5}>
                                <FormGroupInput
                                    fieldObj={header}
                                    placeholder="Authorization"
                                    inputProps={{ 'data-testid': `header-key-${index}` }}
                                />
                            </Grid>
                            <Grid item xs={5}>
                                <FormGroupInput
                                    placeholder="Bearer {{api_key}}"
                                    inputProps={{ 'data-testid': `header-value-${index}` }}
                                />
                            </Grid>
                            <Grid item xs={2}>
                                <IconButton onClick={() => handleRemoveHeader(index)} color="secondary">
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
                            startIcon={<Add />}
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
                    placeholder={`{
                    "ai_application_name": "sales_model",
                    "prompt": "{{prompt}}"
                }`}
                    fieldObj={requestBody}
                    inputProps={{
                        'data-testid': 'request-body',
                        rows: 4
                    }}
                />

                <FormGroupInput
                    as="textarea"
                    label="Response Transform"
                    placeholder={"json.messages && json.messages.length > 0 \n  ? (json.messages.find(message => message.type === 'reply') || {}).content || \"No reply found.\"\n  : \"No response from the server.\"\n"}
                    fieldObj={responseTransform}
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
    application_id: {},
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
    config: {},
    url: {
        validators: {
            errorMessage: 'Endpoint URL is required!',
            fn: (field) => (field.value || '').trim().length > 0
        }
    },
    headers: {
        defaultValue: 'Authorization: Bearer {{api_key}}'
    },
    requestBody: {
        validators: {
            errorMessage: 'Request body is required!',
            fn: (field) => (field.value || '').trim().length > 0
        }
    },
    responseTransform: {},
    method: {
        defaultValue: 'POST'
    }

};

export {
    eval_target_form_def
}

export {VEvalTargetForm};