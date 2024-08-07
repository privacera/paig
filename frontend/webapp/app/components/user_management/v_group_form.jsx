import React, {Component} from 'react';

import {STATUS} from 'common-ui/utils/globals';
import { FormHorizontal, FormGroupInput } from 'common-ui/components/form_fields';

const VGroupForm = ({form, readOnly}) => {
    const {id, name, description} = form.fields;

    return (
        <FormHorizontal>
            <FormGroupInput
                required={true}
                label="Name"
                textOnly={!!id.value || readOnly}
                fieldObj={name}
                data-testid="name"
            />
            <FormGroupInput
                label="Description"
                as="textarea"
                textOnly={readOnly}
                fieldObj={description}
                data-testid="description"
            />
        </FormHorizontal>
    )
}

const group_form_def = {
    id: {},
    name: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                return (field.value || '').length > 0;
            }
        }
    },
    description: {},
    status: {
        defaultValue: STATUS.enabled.value
    }
}

export default VGroupForm;
export {
    group_form_def
}