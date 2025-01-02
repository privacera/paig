import React, {Fragment} from 'react';
import {observer} from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';

import {FormGroupInput} from 'common-ui/components/form_fields';
import {InputGroupSelect2} from 'common-ui/components/filters';
import {aiApplicationLookup} from 'components/reports/fields_lookup';

const VEvaluationDetailsForm = observer(({_vState, form}) => {
  const { run_id, application_name, purpose, application_client } = form.fields;
  const handleApplicationChange = (value) => {
    _vState.application = value;
    form.fields.application_name.value = value;
  };
  return (
    <Fragment>
      <Grid item xs={12}>
        <FormLabel>AI Applications</FormLabel>
        <InputGroupSelect2
          colAttr={{ md: 12, sm: 12 }}
          value={_vState.application}
          labelKey={'label'}
          valueKey={'value'}
          placeholder="Select GenAI Applications"
          allowCreate={false}
          multiple={false}
          onChange={handleApplicationChange}
          loadOptions={(searchString, callback) => {
            aiApplicationLookup(searchString, callback, 'application');
          }}
          data-testid="reports-select-application"
        />
      </Grid>
      <FormGroupInput
        label="Purpose"
        as="textarea"
        fieldObj={purpose}
        data-testid="purpose"
      />
    </Fragment>
  );
})

const evaluation_details_form_def = {
  run_id: {},
  application_name: {},
  purpose: {},
  application_client: {
    defaultValue: "openai:gpt-4o-mini",
  } 
}

export default VEvaluationDetailsForm;
export {
  evaluation_details_form_def
}