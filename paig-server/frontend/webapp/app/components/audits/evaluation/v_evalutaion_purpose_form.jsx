import React from "react";
import { observer } from "mobx-react";

import { makeStyles } from "@material-ui/core/styles";
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

const useStyles = makeStyles({
  customCardContent: {
    "&:last-child": {
      padding: "16px",
    },
  },
});

const VEvaluationPurposeForm = observer(({ _vState, data, form }) => {
  const classes = useStyles();
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
      <Typography className="m-t-lg m-b-md">Templates</Typography>
      <Grid container spacing={2}>
        {["Non-Custom", "Custom"].map((type) => (
          <Grid item xs={12} sm={6} key={type}>
            {f.models(data).filter((template) =>
                type === "Custom" ? template.title.includes("Custom") : !template.title.includes("Custom")
              )
              .map((template, index) => (
                <Card
                  key={`${type}-${index}`}
                  onClick={() => handleTemplateSelect(template.description)} className="pointer" 
                  style={{
                    minHeight: "160px",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    cursor: "pointer",
                    marginBottom: "10px"
                  }}
                >
                  <CardContent style={{ position: "relative", flex: 1 }} className={classes.customCardContent}>
                    <Typography
                      variant="subtitle1"
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between"
                      }}
                      className="m-b-sm"
                    >
                      <span>
                        {template.title}
                        <CallMadeIcon className="m-l-xs" fontSize="small" color="primary" />
                      </span>
                      {template.chip && (
                        <Chip
                          label={template.chip}
                          style={{
                            position: "absolute",
                            top: 8,
                            right: 8,
                            bgcolor: "#EAF2FF",
                            color: "#000",
                            borderRadius: "16px"
                          }}
                        />
                      )}
                    </Typography>
                    <Typography
                      variant="body2"
                      style={{
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        display: "block"
                      }}
                    >
                      {template.description}
                    </Typography>
                  </CardContent>
                </Card>
              ))}
          </Grid>
        ))}
      </Grid>
    </Box>
  );
});

export default VEvaluationPurposeForm;