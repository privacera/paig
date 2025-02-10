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

const VEvaluationPurposeForm = observer(({_vState, form}) => {
    const {  purpose } = form.fields;
  return (
    <Fragment>
    <box>
      <Typography>Purpose</Typography>
      <p>To ensure accurate assessments, clearly define your evaluation goals by specifying which aspects of model performance are most important, such as accuracy, relevance, safety, or bias. You can select one of the provided templates and modify it, or create a completely new evaluation tailored to your needs.</p>
      <Grid item xs={12}>
        <FormLabel required="true">Purpose</FormLabel>
        <FormGroupInput
               as="textarea"
               fieldObj={purpose}
               data-testid="purpose"
        />
      </Grid>
      <p><b>Example Purpose:</b> As a finance team member consider a comprehensive evaluation of the financial model to access its accuracy, identify potential biases and ensure compliances with relevant regulation</p>
      <Typography>Templates</Typography>
    </box>
    </Fragment>
  );
})

export default VEvaluationPurposeForm;