import React from 'react';
import {observer} from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import FormLabel from '@material-ui/core/FormLabel';
import Paper from '@material-ui/core/Paper';
import { Box } from '@material-ui/core';

import {FormGroupInput} from 'common-ui/components/form_fields';
import CEvaluationAppsList from  'containers/audits/evaluation/c_evaluation_list_applications'
import { Typography } from '@material-ui/core';

const VEvaluationDetailsForm = observer(({form, _vState, permission}) => {
  const { name } = form.fields;

  return (
    <Box component={Paper} elevation={0} p="15px">
      <Typography variant="h6" data-testid="header">
        Details 
      </Typography>
      <p>Select a connection method to proceed with evaluation. 
        Using a Pre-registered Application allows for a quicker setup with existing configurations,
         while adding a New Connection provides flexibility for custom integrations.</p>
      <Grid item xs={12} className='m-b-md'>
        <FormLabel required="true">Evaluation Name</FormLabel>
        <FormGroupInput
          label=""
          readOnly
          variant="outlined"
          fieldObj={name}
          fullWidth
		    />
      </Grid>
      <Typography variant="h6" data-testid="header" className='m-b-sm'>
        Application Configurations
      </Typography>
      <CEvaluationAppsList 
        form={form} 
        _vState={_vState}
        permission={permission}
      />
    </Box>
  );
})

const evaluation_form_def = {
  id: {},
  name: {
    validators: {
      errorMessage: 'Evaluation Name is required!',
      fn: (field) => (field.value || '').trim().length > 0
    }
  },
  application_ids: {},
  purpose: {
    validators: {
      errorMessage: 'Purpose is required!',
      fn: (field) => (field.value || '').trim().length > 0
    }
  },
  categories: {},
  report_name: {
    validators: {
      errorMessage: 'Report Name is required!',
      fn: (field) => (field.value || '').trim().length > 0
    }
  }
}

export default VEvaluationDetailsForm;
export {
  evaluation_form_def
}