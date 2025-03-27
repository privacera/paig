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
              return (field.value || '').trim().length > 0;
            }
        }
    },
    keywords: {
        validators: {
            errorMessage: 'Required!',
            fn: (field) => {
              return (field.value || '').trim().length > 0;
            }
        }
    }
}

export {
    VDeniedTermsForm,
    denied_terms_form_def
}