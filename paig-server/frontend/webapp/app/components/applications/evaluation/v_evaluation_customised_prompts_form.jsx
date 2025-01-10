import React, { Fragment, useState } from 'react';
import { observer } from 'mobx-react';
import { FormGroupInput } from 'common-ui/components/form_fields';
import AddIcon from '@material-ui/icons/Add';
import RemoveIcon from '@material-ui/icons/Remove';
import IconButton from '@material-ui/core/IconButton';
import Grid from '@material-ui/core/Grid'; 
import { FormHorizontal } from 'common-ui/components/form_fields';
const VEvaluationCustomisedPromptsForm = observer(({ _vState, form, step2Response }) => {
  const [fields, setFields] = useState(_vState.static_prompts);
  const addField = () => {
    console.log('addField', addField);
    setFields([...fields, { prompt: '', criteria: '' }]);
    _vState.static_prompts = fields;
  };
  const removeField = (index) => {
    console.log('index', index);
    const updatedFields = fields.filter((_, idx) => idx !== index);
    console.log('updatedFields', updatedFields);
    setFields(updatedFields);
    console.log('filetered', updatedFields);
    _vState.static_prompts = updatedFields;
  };
  const handleChange = (index, key, value) => {
    const updatedFields = [...fields];
    console.log('updatedFields', updatedFields);
    updatedFields[index][key] = value;
    setFields(updatedFields);
    _vState.static_prompts = fields;
  };
  return (
    <div>
        <Fragment>
        {fields.map((field, index) => (
          <Grid container spacing={2} alignItems="center" key={index} className="m-b-md">
            <Grid item xs={5}>
              <FormGroupInput
                label={`Prompt ${index + 1}`}
                value={field.prompt}
                onChange={(e) => handleChange(index, 'prompt', e.target.value)}
                data-testid={`prompt-${index}`}
              />
            </Grid>
            <Grid item xs={5}>
              <FormGroupInput
                label={`Criteria ${index + 1}`}
                value={field.criteria}
                onChange={(e) => handleChange(index, 'criteria', e.target.value)}
                data-testid={`criteria-${index}`}
              />
            </Grid>
            <Grid item xs={2}>
              {fields.length > 1 && (
                <IconButton color="primary" size="small" onClick={() => removeField(index)} data-test="remove">
                  <RemoveIcon />
                </IconButton>
              )}
            </Grid>
          </Grid>
        ))}
        <IconButton color="primary" size="small" onClick={addField} data-test="add">
          <AddIcon />
        </IconButton>
      </Fragment>

    </div>
  );
});
const evaluation_customised_prompts_form_def = [
  {
    prompt: '',
    criteria: '',
  },
];
export default VEvaluationCustomisedPromptsForm;
export {
  evaluation_customised_prompts_form_def,
};