import React, {Component} from 'react';
import {observable} from 'mobx';
import {inject, observer} from "mobx-react";

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
import VEvaluationDetailsForm, {evaluation_details_form_def} from 'components/audits/evaluation/v_evaluation_details_form';
import VEvaluationCategoriesForm, {evaluation_categories_form_def} from 'components/applications/evaluation/v_evaluation_categories_form'; 
import VEvaluationCustomisedPromptsForm, {evaluation_customised_prompts_form_def} from 'components/applications/evaluation/v_evaluation_customised_prompts_form';
import CircularProgress from "@material-ui/core/CircularProgress/CircularProgress";

/* Details */


@inject("evaluationStore")
@observer
class CEvaluationForm extends Component {
  @observable _vState = {
    application: '',
    saving: false,
    step1Response: null,
    step2Response: null,
    categories: [],
    static_prompts: [{"prompt": "", "criteria": ""}]
  }
	constructor(props) {
		super(props);

    this.form = createFSForm(evaluation_details_form_def);
    this.form1 = createFSForm(evaluation_categories_form_def);
    this.form2 = createFSForm(evaluation_customised_prompts_form_def);
    this.state = {
      activeStep: 0
    };
	}

  handleRedirect = () => {
    this.props.history.push('/eval_configs');
  }

  handleBackButton = () => {
    this.handleRedirect();
  }

  handlePostCreate = (response) => {
    //handle post final form submission
    this.props.history.replace('/eval_reports/');
  }

  handleCreate = async () => {
    await this.form2.validate();
    const form = this.form2;
    if (!form.valid) {
      return;
    }
    let data = form.toJSON();
    if (form.model) {
      data = Object.assign({}, form.model, data);
    }
    if (this.Modal) {
      this.Modal.okBtnDisabled(true);
    }
    let form1Data = this._vState.step1Response;
    form1Data.categories = this._vState.categories;
    form1Data.static_prompts = this._vState.static_prompts;
    try {
      this._vState.saving = true;
      let response = await this.props.evaluationStore.generateEvaluation(form1Data);
      f.notifySuccess('Evaluation generated successfully');
      this.handlePostCreate(response);
      this._vState.saving = false;
      this.props.history.push('/evaluation_reports');
    } catch(e) {
      this._vState.saving = false;
      f.handleError()(e);
    }
  }

  getSteps = () => {
    return ['Details', 'Purpose', 'Categories'];
  }

  handleNext = async () => {
    console.log(this._vState.saving);
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
        let response = await this.props.evaluationStore.createEvaluation(data);
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
        return <div></div>
        // return <VEvaluationCategoriesForm _vState={this._vState} form={this.form1} categories={step1Response.categories} />;
      case 2:
        return <div></div>
        // return <VEvaluationCustomisedPromptsForm _vState={this._vState} form={this.form2} step2Response={step2Response} />;
      default:
        return 'Unknown step';
    }
  }

  render() {
    const {handleBackButton, handleCreate} = this;
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
      <Paper>
        <Grid container spacing={1} ref={ref => this.containerRef = ref}>
            <Grid item xs={12} sm={3}>
                <Stepper activeStep={activeStep} orientation="vertical" className="background-color">
                    {steps.map((label, index) => (
                    <Step key={label}>
                        <StepLabel>{label}</StepLabel>
                    </Step>
                    ))}
                </Stepper>
            </Grid>
            <Grid item xs={12} sm={9}>
                {this.renderStepContent(activeStep)}
            
            <Grid container spacing={3}>
                <Grid item xs={12}>
                    <Button
                        disabled={activeStep === 0 || this._vState.saving}
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
                        disabled={this._vState.saving}
                    >
                        {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
                        {
                        this._vState.saving &&
                        <CircularProgress size="15px" className="m-r-xs" />
                        }
                    </Button>
                    {activeStep === steps.length && (
                        <Button onClick={this.handleReset}>
                        Reset
                        </Button>
                    )}
                </Grid>
            </Grid>
            </Grid>
        </Grid>
        </Paper>
	    </BaseContainer>
	)}
}

export default CEvaluationForm;