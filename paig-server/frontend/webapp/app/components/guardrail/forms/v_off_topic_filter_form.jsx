import React, {Fragment} from 'react';

import {Typography} from '@material-ui/core';

import { FormHorizontal, FormGroupInput } from 'common-ui/components/form_fields';
import { PROMPT_REPLY_ACTION_TYPE } from 'utils/globals';

const VOffTopicFilterForm = ({form}) => {
    const {topic, definition, samplePhrases} = form.fields;
    return (
        <FormHorizontal>
            <FormGroupInput
                required={true}
                label="Topic"
                placeholder="Enter name of the topic"
                fieldObj={topic}
                data-testid="topic"
            />
            <FormGroupInput
                required={true}
                as="textarea"
                label="Definition"
                placeholder="Example - Health diagnostics refers to the process of analyzing symptoms, medical history, or test results to determine the presence or cause of a medical condition or disease"
                fieldObj={definition}
                data-testid="definition"
            />
            <FormGroupInput
                as="textarea"
                placeholder="Example: What might be causing my persistent headaches?"
                label="Sample Phrases"
                fieldObj={samplePhrases}
                data-testid="sample-phrases"
            >
                <Typography variant="caption">
                    Enter sample phrases separated by a new line
                </Typography>
            </FormGroupInput>
        </FormHorizontal>
    );
};

const off_topic_filter_form_def = {
    topic: {
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
                } else if (!/^[A-Z0-9_ \-!?\.]+$/i.test(field.value)) {
                   field._originalErrorMessage = 'Only alphanumeric characters, spaces, underscores, hyphens, exclamation points, question marks, and periods are allowed!';
                   return false;
                }
                return true;
            }
        }
    },
    definition: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                let length = (field.value || '').trim().length;

                if (!length) {
                    field._originalErrorMessage = 'Required!';
                    return false;
                } else if (length > 200) {
                    field._originalErrorMessage = 'Max 200 characters allowed!';
                    return false;
                }

                return true;
            }
        }
    },
    samplePhrases: {
        validators: {
            errorMessage: 'Max 100 characters allowed!',
            fn: (field) => {
                let length = (field.value || '').trim().length;

                return !(length && length > 100);
            }
        }
    },
    action: {
        defaultValue: PROMPT_REPLY_ACTION_TYPE.DENY.VALUE
    }
}

export {
    VOffTopicFilterForm,
    off_topic_filter_form_def
}