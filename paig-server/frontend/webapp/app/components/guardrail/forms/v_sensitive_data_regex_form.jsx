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
                data-testid="action"
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
                let length = (field.value || '').trim().length;

                if (!length) {
                    field._originalErrorMessage = 'Required!';
                    return false;
                } else if (length > 100) {
                    field._originalErrorMessage = 'Max 100 characters allowed!';
                    return false;
                }

                return true;
            }
        }
    },
    description: {
        validators: {
            errorMessage: 'Max 1000 characters allowed!',
            fn: (field) => {
                let length = (field.value || '').trim().length;

                return !(length && length > 1000);
            }
        }
    },
    pattern: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                let length = (field.value || '').trim().length;

                if (!length) {
                    field._originalErrorMessage = 'Required!';
                    return false;
                } else if (length > 500) {
                    field._originalErrorMessage = 'Max 500 characters allowed!';
                    return false;
                }
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