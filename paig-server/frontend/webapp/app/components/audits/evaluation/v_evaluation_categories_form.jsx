import React from "react";
import { observer } from "mobx-react";

import { 
  Paper, 
  Switch, 
  FormControlLabel, 
  Checkbox, 
  FormGroup, 
  FormControl,
  Typography,
  Tooltip,
  Box,
  Grid
} from "@material-ui/core";
import { makeStyles } from '@material-ui/core/styles';
import Alert from '@material-ui/lab/Alert';

import {ErrorLogo} from 'components/site/v_error_page_component';

const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(3),
    border: `1px solid ${theme.palette.divider}`
  },
  checkboxGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", 
    gap: "8px"
  },
  checkboxItem: {
    display: "flex",
    alignItems: "center",
  },
  categoryName: {
    color: theme.palette.text.primary,
  }
}));

const VEvaluationCategories = observer(({ form, selectedCategories, showSuggested, handleToggle, filteredCategories, setSelectedCategories, _vState }) => {
  const { categories } = form.fields;
  const classes = useStyles();

  const handleCheckboxChange = (category) => {
    _vState.errorMsg = '';
    const updatedCategories = selectedCategories.includes(category)
      ? selectedCategories.filter((c) => c !== category)
      : [...selectedCategories, category];
    setSelectedCategories(updatedCategories);
    console.log(updatedCategories, 'updatedCategories')
    categories.value = updatedCategories;
  };

  return (
    <Box component={Paper} elevation={0} p="15px">
      <Typography variant="h6" data-testid="header">
        Evaluation categories 
      </Typography>
      <p>Evaluation categories help you focus on specific aspects of model performance that align with your goals. These categories enable you to assess key areas like accuracy, fairness, safety, and relevance, ensuring the evaluation process is comprehensive and tailored to your needs. By selecting the relevant categories, you can ensure a well-rounded analysis that addresses your most important criteria.</p>
      <Alert severity="info" className="alert-on-modal">
        Categories and types are displayed based on the evaluation purpose in the previous step. To explore all available options, disable Suggested filters to override the filter.
      </Alert>
      <FormControlLabel
        control={
          <Switch 
            color="primary" 
            checked={showSuggested} 
            onChange={handleToggle} 
          />
        }
        label={<Typography variant="subtitle1">Suggested filters</Typography>}
        className="m-t-md m-b-md"
      />
      {_vState.errorMsg && (
        <Grid container spacing={3} className="m-b-sm">
          <Grid item xs={12}>
            <Alert severity="error">
              {_vState.errorMsg}
            </Alert>
          </Grid>
        </Grid>
      )}
      <Paper className={classes.paper} elevation={0}>
        {filteredCategories.length === 0 ? (   
          <Grid container spacing={2} className="align-items-center m-t-md m-b-md justify-center">
            <Grid item>
              <ErrorLogo errorCode="" imageProps={{width: 'auto', height: '100px'}} />
            </Grid>
            <Grid item xs={12} sm={7}>
              <Typography variant="h6" data-testid="no-ai-app-connected">No Categories Created</Typography>
              <Typography variant="body2" data-testid="no-ai-app-desc">
              The purpose you entered couldn't be used to generate categories. Try refining it with more context or choosing a broader description.
              </Typography>
            </Grid>
          </Grid>      
        ) : (
          <FormControl component="fieldset" fullWidth>
            <Typography variant="h7" className="m-b-sm">
              {showSuggested ? "Suggested Categories" : "All Categories"}
            </Typography>

            <FormGroup className={classes.checkboxGrid}>
              {filteredCategories.map((category) => (
                <FormControlLabel
                  key={category.Name}
                  control={
                    <Checkbox
                      color="primary"
                      checked={selectedCategories.includes(category.Name)}
                      onChange={() => handleCheckboxChange(category.Name)}
                    />
                  }
                  label={
                    <Tooltip key={category.Name} title={category.Description} arrow placement="top">  
                      <Typography variant="body1" className={classes.categoryName}>
                        {category.Name}
                      </Typography>
                    </Tooltip>
                  }
                />
              ))}
            </FormGroup>
          </FormControl>  
        )}
      </Paper>
    </Box>
  );
});

export default VEvaluationCategories;
