import React, {Fragment} from 'react';
import {observer} from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';

import {FormGroupSelect2} from 'common-ui/components/form_fields';

const VEvaluationCategoriesForm = observer(({_vState, form, categories}) => {
  const categoryOptions = categories.map(category => ({ label: category, value: category }));
  const handleCategoryChange = (selectedOptions) => {
    if (typeof selectedOptions === 'string') {
      selectedOptions = selectedOptions.split(',').map(option => ({ label: option, value: option }));
    }
    if (!Array.isArray(selectedOptions)) {
      selectedOptions = [];
    }
    _vState.categories = selectedOptions.map(option => option.value);
    form.fields.categories = _vState.categories;
  };
  return (
    <Fragment>
      <Grid item xs={12}>
        <FormLabel>Categories</FormLabel>
      </Grid>
      <FormGroupSelect2
        value={_vState.categories.map(category => ({ label: category, value: category }))}
        variant="standard"
        multiple={true}
        fieldKey={'categories'}
        labelKey={'label'}
        valueKey={'value'}
        placeholder="Select Categories"
        data={categoryOptions}
        onChange={handleCategoryChange}
        data-testid="sensitive-data-restriction"
      />
    </Fragment>
  );
})

const evaluation_categories_form_def = {
  categories: {}
}

export default VEvaluationCategoriesForm;
export {
  evaluation_categories_form_def
}