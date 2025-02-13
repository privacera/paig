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
                inputProps={{'data-testid': 'topic'}}
            />
            <FormGroupInput
                required={true}
                as="textarea"
                label="Definition"
                placeholder="Example - Health diagnostics refers to the process of analyzing symptoms, medical history, or test results to determine the presence or cause of a medical condition or disease"
                fieldObj={definition}
                inputProps={{'data-testid': 'definition'}}
            />
            <FormGroupInput
                as="textarea"
                placeholder="Example: What might be causing my persistent headaches?"
                label="Sample Phrases"
                fieldObj={samplePhrases}
                inputProps={{'data-testid': 'samplePhrases'}}
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
              return (field.value || '').trim().length > 0;
            }
        }
    },
    definition: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                return (field.value || '').trim().length > 0;
            }
        }
    },
    samplePhrases: {},
    action: {
        defaultValue: PROMPT_REPLY_ACTION_TYPE.DENY.VALUE
    }
}

export {
    VOffTopicFilterForm,
    off_topic_filter_form_def
}