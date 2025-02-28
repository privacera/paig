import React from 'react';

import {FormHorizontal, FormGroupInput, FormGroupSelect2} from 'common-ui/components/form_fields';
import {PROMPT_REPLY_ACTION_TYPE} from 'utils/globals';

const VSensitiveDataRegexForm = ({form}) => {
    const {name, description, pattern, action} = form.fields;

    return (
        <FormHorizontal>
            <FormGroupInput
                required={true}
                label="Name"
                placeholder="Example - Invoice Number"
                fieldObj={name}
                inputProps={{'data-testid': 'name'}}
            />
            <FormGroupInput
                required={true}
                label="Pattern"
                placeholder="Example - \d{3}-\d{2}-\d{4}"
                fieldObj={pattern}
                inputProps={{'data-testid': 'pattern'}}
            />
            <FormGroupSelect2
                required={true}
                data={Object.values(PROMPT_REPLY_ACTION_TYPE)}
                label="Action"
                fieldObj={action}
                disableClearable={true}
                labelKey="LABEL"
                valueKey="VALUE"
                inputProps={{'data-testid': 'action'}}
            />
            <FormGroupInput
                as="textarea"
                label="Description"
                fieldObj={description}
                placeholder="Example - Invoice Number is used to uniquely identify and track financial transactions or bills issued to customers."
                inputProps={{'data-testid': 'description'}}
            />
        </FormHorizontal>
    )
}

const sensitive_data_regex_form_def = {
    type: {
        defaultValue: "regex"
    },
    name: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
              return (field.value || '').trim().length > 0;
            }
        }
    },
    description: {},
    pattern: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
              return (field.value || '').trim().length > 0;
            }
        }
    },
    action: {
        defaultValue: PROMPT_REPLY_ACTION_TYPE.REDACT.VALUE
    }
}

export {
    VSensitiveDataRegexForm,
    sensitive_data_regex_form_def
}