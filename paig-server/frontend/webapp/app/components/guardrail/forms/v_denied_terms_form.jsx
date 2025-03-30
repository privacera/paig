import React from 'react';

import {FormHorizontal, FormGroupInput, FormGroupSelect2} from 'common-ui/components/form_fields';

const VDeniedTermsForm = ({form}) => {
    const {term, keywords} = form.fields;

    return (
        <FormHorizontal>
            <FormGroupInput
                required={true}
                label="Term"
                placeholder="Enter a term name"
                fieldObj={term}
                data-testid="term"
            />
            <FormGroupSelect2
                required={true}
                label="Keywords"
                fieldObj={keywords}
                placeholder="Enter keywords or phrases and press enter"
                splitValueDelimiter="##|##"
                allowCreate={true}
                multiple={true}
                data-testid="phrases-and-keywords"
            />
        </FormHorizontal>
    )
};

const denied_terms_form_def = {
    term: {
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
    keywords: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
                let values = (field.value || '').split(',').map(v => v.trim());
                let invalidValue = values.find(v => v.length > 100);

                if (!values.length || values.some(v => !v.length)) {
                    field._originalErrorMessage = 'Required!';
                    return false;
                } else if (invalidValue) {
                    field._originalErrorMessage = 'Each value must be 100 characters or less!';
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