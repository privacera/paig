import React, {Component} from 'react';
import {observable} from 'mobx';
import {inject} from "mobx-react";

import Box from '@material-ui/core/Box';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import Stepper from '@material-ui/core/Stepper';
import Step from '@material-ui/core/Step';
import StepLabel from '@material-ui/core/StepLabel';

import f from "common-ui/utils/f";
import BaseContainer from 'containers/base_container';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import VEvaluationDetailsForm, {evaluation_details_form_def} from 'components/applications/evaluation/v_evaluation_details_form';
import VEvaluationCategoriesForm, {evaluation_categories_form_def} from 'components/applications/evaluation/v_evaluation_categories_form'; 
import VEvaluationCustomisedPromptsForm, {v_evaluation_customised_prompts_form_def} from 'components/applications/evaluation/v_evaluation_customised_prompts_form';

@inject("evaluationStore")
class CEvaluationForm extends Component {
  @observable _vState = {
    application: '',
    saving: false,
    step1Response: null,
    step2Response: null,
    categories: []
  }
	constructor(props) {
		super(props);

    this.form = createFSForm(evaluation_details_form_def);
    this.state = {
      activeStep: 0
    };
	}

  handleRedirect = () => {
    this.props.history.push('/evaluations');
  }

  handleBackButton = () => {
    this.handleRedirect();
  }

  handlePostCreate = (response) => {
    //handle post final form submission
    this.props.history.replace('/evaluations/');
  }

  handleCreate = async () => {
    await this.form.validate();
    const form = this.form;
    if (!form.valid) {
      return;
    }
    let data = form.toJSON();
    if (this.form.model) {
      data = Object.assign({}, this.form.model, data);
    }
    if (this.Modal) {
      this.Modal.okBtnDisabled(true);
    }
    try {
      this._vState.saving = true;
      let response = await this.props.evaluationStore.generateEvaluation(data);
      f.notifySuccess('Evaluation generated successfully');
      this.handlePostCreate(response);
    } catch(e) {
      this._vState.saving = false;
      f.handleError()(e);
    }
  }

  getSteps = () => {
    return ['Basic Details', 'Categories', 'Customised prompts'];
  }

  handleNext = async () => {
    const { activeStep } = this.state;
    if (activeStep === 0) {
      await this.form.validate();
      const form = this.form;
      if (!form.valid) {
        return;
      }
      let data = form.toJSON();
      if (this.form.model) {
        data = Object.assign({}, this.form.model, data);
      }
      try {
        this._vState.saving = true;
        // Hardcoded response
        let response = {
          "run_id": "UUID",
          "application_name": "IT Support Chatbot",
          "purpose": "To support IT helpdesk",
          "application_client": "openai:gpt-4o-mini",
          "categories": [
            "pii",
            "excessive-agency",
            "hallucination",
            "hijacking",
            "harmful:cybercrime",
            "pii:api-db",
            "pii:direct",
            "pii:session",
            "pii:social",
            "harmful:privacy"
          ]
        };
        this._vState.step1Response = response;
        this._vState.categories = response.categories;
        this._vState.saving = false;
      } catch (e) {
        this._vState.saving = false;
        f.handleError()(e);
        return;
      }
    }
    this.setState((prevState) => ({
      activeStep: prevState.activeStep + 1
    }));
  }

  handleBack = () => {
    this.setState((prevState) => ({
      activeStep: prevState.activeStep - 1
    }));
  }

  handleReset = () => {
    this.setState({
      activeStep: 0
    });
  }

  renderStepContent = (step) => {
    const { step1Response, step2Response } = this._vState;
    switch (step) {
      case 0:
        return <VEvaluationDetailsForm _vState={this._vState} form={this.form} />;
      case 1:
        return <VEvaluationCategoriesForm _vState={this._vState} form={this.form} categories={step1Response.categories} />;
      case 2:
        return <VEvaluationCustomisedPromptsForm _vState={this._vState} form={this.form} step2Response={step2Response} />;
      default:
        return 'Unknown step';
    }
  }

	render() {
    const {_vState, handleBackButton, handleCreate} = this;
    const { activeStep } = this.state;
    const steps = this.getSteps();
		return (
			<BaseContainer
        showRefresh={false}
        showBackButton={true}
        backButtonProps={{
          size: 'small',
          onClick: handleBackButton
        }}
				titleColAttr={{
					sm: 8,
					md: 8
				}}
			>
      <Stepper activeStep={activeStep} className='m-b-md'>
        {steps.map((label, index) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <Box component={Paper} className="m-t-sm">
        <Grid container spacing={3} style={{padding: '5px 15px'}} data-track-id="application-info">
          {this.renderStepContent(activeStep)}
        </Grid>
      </Box>
      <Grid container spacing={3} className="m-t-md">
        <Grid item xs={12}>
          <Button
            disabled={activeStep === 0}
            onClick={this.handleBack}
            className="m-r-sm"
          >
            Back
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={activeStep === steps.length - 1 ? handleCreate : this.handleNext}
            data-testid="create-app-btn"
            data-track-id="create-app-btn"
          >
            {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
          </Button>
          {activeStep === steps.length && (
            <Button onClick={this.handleReset}>
              Reset
            </Button>
          )}
        </Grid>
      </Grid>
			</BaseContainer>
		)
	}
}

export default CEvaluationForm;