import React from "react";
import { observer } from "mobx-react";

import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import CallMadeIcon from '@material-ui/icons/CallMade';
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Chip from "@material-ui/core/Chip";
import Paper from '@material-ui/core/Paper';
import { Box } from '@material-ui/core';

import f from 'common-ui/utils/f';
import { FormGroupInput } from "common-ui/components/form_fields";

const VEvaluationPurposeForm = observer(({ _vState, data, form }) => {
  const { purpose } = form.fields;

  const handleTemplateSelect = (description) => {
    purpose.value = description;
  };

  return (
    <Box component={Paper} elevation={0} p="15px">
      <Typography variant="h6" data-testid="header">
        Purpose 
      </Typography>
      <p>To ensure accurate assessments, clearly define your evaluation goals by specifying which aspects of model performance are most important, such as accuracy, relevance, safety, or bias. You can select one of the provided templates and modify it, or create a completely new evaluation tailored to your needs.</p>
      <Grid item xs={12}>
        <FormGroupInput
          label={"Purpose"}
          required={true}
          as="textarea" 
          fieldObj={purpose}
          data-testid="purpose"
        />
      </Grid>
      <Grid item xs={12}>
        Example Purpose: As a finance team member, consider a comprehensive evaluation of the financial model to assess its accuracy, identify potential biases, and ensure compliance with relevant regulations.
      </Grid>
      <Typography className="m-t-lg m-b-lg" >Templates</Typography>
      <Grid container spacing={2}>
        {f.models(data).map((template, index) => (
          <Grid item xs={12} sm={6} key={index}>
            <Card onClick={() => handleTemplateSelect(template.description)} className="pointer" style={{ minHeight: '140px' }}>
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
    </Box>
  );
});

export default VEvaluationPurposeForm;