import React, { Fragment } from "react";
import { observer } from "mobx-react";
import Grid from "@material-ui/core/Grid";
import FormLabel from "@material-ui/core/FormLabel";
import Typography from "@material-ui/core/Typography";
import IconButton from "@material-ui/core/IconButton";
import PlayCircleOutlineIcon from '@material-ui/icons/PlayCircleOutline';
import CallMadeIcon from '@material-ui/icons/CallMade';
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import CardActions from "@material-ui/core/CardActions";
import { FormGroupInput } from "common-ui/components/form_fields";
import Chip from "@material-ui/core/Chip";

import f from 'common-ui/utils/f';

const VEvaluationPurposeForm = observer(({ _vState, data, form }) => {
  const { purpose } = form.fields;

  const handleTemplateSelect = (description) => {
    purpose.value = description;
  };

  const handlePurposeChange = (e) => {
    purpose.value = e.target.value;
  };

  return (
    <Fragment>
      <Typography variant="h6">Purpose</Typography>
      <Typography variant="body2">
        To ensure accurate assessments, clearly define your evaluation goals by specifying which aspects of model performance are most important, such as accuracy, relevance, safety, or bias. You can select one of the provided templates and modify it, or create a completely new evaluation tailored to your needs.
      </Typography>

      <Grid item xs={12}>
        <FormLabel required>Purpose</FormLabel>
        <FormGroupInput 
          as="textarea" 
          value={purpose.value}
          onChange={handlePurposeChange}
          data-testid="purpose"
        />
      </Grid>

      <Typography variant="body2">
        <b>Example Purpose:</b> As a finance team member, consider a comprehensive evaluation of the financial model to assess its accuracy, identify potential biases, and ensure compliance with relevant regulations.
      </Typography>

      <Typography variant="h6">Templates</Typography>
      <Grid container spacing={2}>
        {f.models(data).map((template, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Card onClick={() => handleTemplateSelect(template.description)} className="pointer">
              <CardContent>
                <Typography
                  variant="subtitle1"
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <span>
                    {template.title}
                    <CallMadeIcon fontSize="small" color="primary" />
                  </span>
                  { template.chip && 
                    <Chip label={template.chip} sx={{ bgcolor: "#EAF2FF", color: "#000", borderRadius: "16px" }} />
                  }
                </Typography>
                <Typography variant="body2">{template.description}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Fragment>
  );
});

const evaluation_purpose_form_def = {
  purpose: {}
}

export {
  evaluation_purpose_form_def
}

export default VEvaluationPurposeForm;