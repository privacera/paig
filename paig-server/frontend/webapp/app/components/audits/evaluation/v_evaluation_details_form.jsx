import React, {Fragment} from 'react';
import {observer} from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';
import TextField from '@material-ui/core/TextField';
import {FormGroupInput} from 'common-ui/components/form_fields';
import {InputGroupSelect2} from 'common-ui/components/filters';
import {aiApplicationLookup} from 'components/reports/fields_lookup';
import CEvaluationAppsList from  'components/audits/evaluation/v_evaluation_list_applications'
import { Typography } from '@material-ui/core';

const VEvaluationDetailsForm = observer(({_vState, form}) => {
  const { eval_id, application_name, purpose, application_client } = form.fields;
  const handleApplicationChange = (value) => {
    _vState.application = value;
    form.fields.application_name.value = value;
  };

  const targets = (searchString, callback) => {
    let target =  aiApplicationLookup(searchString, callback, 'application');
    return target
  }

  return (
    <Fragment>
    <box>
      <Typography>Details</Typography>
      <p>Select a connection method to proceed with evaluation. 
        Using a Pre-registered Application allows for a quicker setup with existing configurations,
         while adding a New Connection provides flexibility for custom integrations.</p>
      <Grid item xs={12}>
        <FormLabel required="true">Evaluation Name</FormLabel>
        <TextField
            label=""
            readOnly
            variant="outlined"
            value={_vState.name}
            fullWidth
		    />
      </Grid>
      <CEvaluationAppsList></CEvaluationAppsList>
    </box>
    </Fragment>
  );
})

const evaluation_details_form_def = {
  name: {},
  application_names: {}
}

export default VEvaluationDetailsForm;
export {
  evaluation_details_form_def
}