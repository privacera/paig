import React from 'react';

import {METADATA_DATA_TYPE} from 'utils/globals';
import { FormHorizontal, FormGroupInput, FormGroupSelect2 } from 'common-ui/components/form_fields';

const VMetadataForm = ({ form}) => {
    const {name, /*valueDataType,*/ description} = form.fields;

    return (
        <FormHorizontal>
            <FormGroupInput
                required={true}
                label="Name"
                fieldObj={name}
                inputProps={{'data-testid': 'name'}}
            />
            {/*<FormGroupSelect2
                required={true}
                label="Data Type"
                data={Object.values(METADATA_DATA_TYPE)}
                labelKey="LABEL"
                valueKey="TYPE"
                fieldObj={valueDataType}
                data-testid="data-type"
            />*/}
            <FormGroupInput
                label="Description"
                as="textarea"
                fieldObj={description}
                inputProps={{'data-testid': 'description'}}
            />
        </FormHorizontal>
    )
}

const metadata_form_def = {
    id: {},
    type: {
        defaultValue: 'USER_DEFINED'
    },
    name: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
              return (field.value || '').trim().length > 0;
            }
        }
    },
    valueDataType: {
        defaultValue: METADATA_DATA_TYPE.MULTI_VALUE.TYPE
    },
    description: {}
}

export default VMetadataForm;
export {
    metadata_form_def
}