import React from 'react';
import {observer} from 'mobx-react';

import {FormHorizontal, FormGroupSelect2} from 'common-ui/components/form_fields';

const VDeniedTermsForm = observer(({form}) => {
    const {keywords} = form.fields;

    return (
        <FormHorizontal>
            <FormGroupSelect2
                required={true}
                label="Keywords"
                fieldObj={keywords}
                placeholder="Enter keywords or phrases and press enter"
                splitValueDelimiter="##|##"
                allowCreate={true}
                multiple={true}
                errorMessage={keywords.errorMessage}
                data-testid="phrases-and-keywords"
            />
        </FormHorizontal>
    )
});

const denied_terms_form_def = {
    keywords: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                let values = (field.value || '').split('##|##').map(v => v.trim());
                let invalidValue = values.find(v => v.length > 100);

                if (!values.length || values.some(v => !v.length)) {
                    field._originalErrorMessage = 'Required!';
                    return false;
                } else if (invalidValue) {
                    field._originalErrorMessage = 'Each keyword can contain up to 100 characters';
                    return false;
                } else if (values.length > 10000) {
                    field._originalErrorMessage = 'You can enter up to 10,000 phrases or keywords';
                    return false;
                }

                return true;
            }
        }
    }
}

export {
    VDeniedTermsForm,
    denied_terms_form_def
}