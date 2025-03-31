import React, { useRef, useState } from "react";
import { observer } from "mobx-react";

import { makeStyles } from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import CallMadeIcon from '@material-ui/icons/CallMade';
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Chip from "@material-ui/core/Chip";
import Paper from '@material-ui/core/Paper';
import { Box, Button, Checkbox, FormControlLabel } from '@material-ui/core';

import f from 'common-ui/utils/f';
import { FormGroupInput } from "common-ui/components/form_fields";
import FSModal from 'common-ui/lib/fs_modal';

const useStyles = makeStyles({
  customCardContent: {
    "&:last-child": {
      padding: "16px",
    },
  },
});

const VEvaluationPurposeForm = observer(({ _vState, data, form }) => {
  const classes = useStyles();
  const modalRef = useRef(null);
  const { purpose } = form.fields;

  // Track the selected template
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const handleTemplateSelect = () => {
    if (selectedTemplate) {
      purpose.value = selectedTemplate.description;
    }
    modalRef.current?.hide();
  };

  const handleCheckboxChange = (template) => {
    setSelectedTemplate(template);
  };

  const insertTemplate = () => {
    modalRef.current?.show({
      title: 'Templates',
      btnOkText: "Insert"

    });
  };

  const clearTemplate = () => {
    purpose.value = '';
    setSelectedTemplate(null);
  };

  const handleModalClose = () => {
    modalRef.current?.hide();
    setSelectedTemplate(null);
  }

  return (
    <Box component={Paper} elevation={0} p="15px">
      <Typography variant="h6" data-testid="header">
        Evaluation Focus 
      </Typography>
      <p>Clarify your evaluation goals by identifying key performance aspects such as accuracy, relevance, safety, or bias. Choose from templates or create a custom evaluation suited to your needs.</p>
      <Grid container>
        <Grid item xs={6}>
            <Typography variant="body1">Purpose</Typography>
        </Grid>
        <Grid item xs={6} style={{ display: "flex", justifyContent: "flex-end" }}>
          <Button onClick={insertTemplate} color="primary">
            Insert Template
          </Button>
          <Button onClick={clearTemplate} color="primary">
            Clear
          </Button>
        </Grid>
      </Grid>
      <Grid item xs={12}>
        <FormGroupInput as="textarea" fieldObj={purpose} data-testid="purpose" />
      </Grid>
      <FSModal ref={modalRef} maxWidth="lg" dataResolve={handleTemplateSelect}  reject={handleModalClose}>
        <Grid container spacing={2}>
          {["Non-Custom", "Custom"].map((type) => (
            <Grid item xs={12} sm={6} key={type}>
              {f.models(data)
                .filter(template =>
                  type === "Custom" ? template.title.includes("Custom") : !template.title.includes("Custom")
                )
                .map((template, index) => (
                  <Card
                    key={`${type}-${index}`}
                    className="pointer"
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
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                        <Typography
                          variant="subtitle1"
                        >
                        <FormControlLabel
                          control={
                            <Checkbox
                                checked={selectedTemplate?.index === template.index} // Compare by unique ID
                                onChange={() => handleCheckboxChange(template)}
                                color="primary"
                              />
                          }
                          label={<Typography variant="button" style={{color: "black"}}>{template.title}</Typography>}
                        />
                      </Typography>
                      {!template.chip && <CallMadeIcon className="m-l-xs" fontSize="small" color="primary" />}
                        {template.chip && (
                          <Chip
                            label={template.chip}
                            style={{
                              bgcolor: "#EAF2FF",
                              color: "#000",
                              borderRadius: "16px"
                            }}
                          />
                        )}
                      </div>
                      <Typography variant="body2" style={{ overflow: "hidden", textOverflow: "ellipsis", display: "block" }}>
                        {template.description}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
            </Grid>
          ))}
        </Grid>
      </FSModal>
    </Box>
  );
});

export default VEvaluationPurposeForm;
