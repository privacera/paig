import React, {Fragment} from 'react';
import {observer} from 'mobx-react';

import {FormGroupInput} from 'common-ui/components/form_fields';

const VEvaluationCustomisedPromptsForm = observer(({_vState, form, step2Response}) => {
  const { prompt, criteria } = form.fields;
  return (
    <Fragment>
      <FormGroupInput
        required={true}
        label="Prompt"
        fieldObj={prompt}
        data-testid="prompt"
      />
      <FormGroupInput
        label="Criteria"
        as="textarea"
        fieldObj={criteria}
        data-testid="criteria"
      />
    </Fragment>
  );
})

const evaluation_customised_prompts_form_def = {
  prompt: {},
  criteria: {}
}

export default VEvaluationCustomisedPromptsForm;
export {
  evaluation_customised_prompts_form_def
}