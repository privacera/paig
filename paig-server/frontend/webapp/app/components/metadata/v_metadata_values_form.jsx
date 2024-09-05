import React from 'react';

import { FormHorizontal, FormGroupInput } from 'common-ui/components/form_fields';

const VMetaDataValueForm = ({ form}) => {
    const {metadataValue} = form.fields;

    return (
        <FormHorizontal>
            <FormGroupInput
                required={true}
                label="Value"
                fieldObj={metadataValue}
                inputProps={{'data-testid': 'metadata-value'}}
            />
        </FormHorizontal>
    )
}

const metadata_value_form_def = {
    id: {},
    metadataId: {},
    metadataValue: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
              return (field.value || '').trim().length > 0;
            }
        }
    }
}

export default VMetaDataValueForm;
export {
    metadata_value_form_def
}