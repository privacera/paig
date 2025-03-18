import React from 'react';

import { FormHorizontal, FormGroupInput } from 'common-ui/components/form_fields';

const VResponseTemplateForm = ({ form}) => {
    const {response, description} = form.fields;

    return (
        <FormHorizontal>
            <FormGroupInput
                required={true}
                as="textarea"
                label="Response"
                fieldObj={response}
                inputProps={{'data-testid': 'response'}}
                data-testid="response-template"
            />
            <FormGroupInput
                as="textarea"
                label="Description"
                fieldObj={description}
                inputProps={{'data-testid': 'description'}}
            />
        </FormHorizontal>
    )
}

const response_template_form_def = {
    id: {},
    response: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
              return (field.value || '').trim().length > 0;
            }
        }
    },
    description: {}
}

export default VResponseTemplateForm;
export {
    response_template_form_def
}