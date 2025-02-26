import React, {Component, createRef} from 'react';
import {inject, observer} from "mobx-react";
import {observable} from 'mobx';

import Box from '@material-ui/core/Box';
import Grid from '@material-ui/core/Grid';
import Step from '@material-ui/core/Step';
import Paper from '@material-ui/core/Paper';
import Button from '@material-ui/core/Button';
import Stepper from '@material-ui/core/Stepper';
import StepLabel from '@material-ui/core/StepLabel';
import StepConnector from '@material-ui/core/StepConnector';
import CircularProgress from "@material-ui/core/CircularProgress/CircularProgress";

import f from "common-ui/utils/f";
import FSModal from 'common-ui/lib/fs_modal';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import BaseContainer from 'containers/base_container';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import VRunReportForm from 'components/audits/evaluation/v_run_report_form';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import CEvaluationPurposeForm from "containers/audits/evaluation/c_evaluation_purpose_form";
import CEvaluationCategoriesForm from "containers/audits/evaluation/c_evaluation_categories_form";
import VEvaluationDetailsForm, {evaluation_form_def} from 'components/audits/evaluation/v_evaluation_details_form';

@inject("evaluationStore")
@observer
class CEvaluationForm extends Component {
  runReportModalRef = createRef();
  @observable _vState = {
    application: '',
    saving: false,
    purposeResponse: null,
    static_prompts: [{"prompt": "", "criteria": ""}],
    errorMsg: "",
  }
	constructor(props) {
		super(props);

    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.EVALUATION_CONFIG.PROPERTY);

    this.evalForm = createFSForm(evaluation_form_def);
    this.state = {
      activeStep: 0
    };
	}

  handlePostCreate = () => {
    this.props.history.replace('/eval_reports');
  }

  handlePostSave = () => {
    this.props.history.replace('/eval_configs');
  }

  handleCreate = async () => {
    const form = this.evalForm;
    const formData = form.toJSON();
    formData.application_ids = formData.application_ids.join(',');
    formData.custom_prompts = [];

    try {
      this._vState.saving = true;
      let response = await this.props.evaluationStore.saveAndRunEvaluationConfig(formData);
      this._vState.saving = false;
      this.runReportModalRef.current.hide();
      f.notifySuccess('Your evaluation is triggered successfully');
      this.handlePostCreate(response);
      this._vState.saving = false;
    } catch(e) {
      this._vState.saving = false;
      f.handleError()(e);
    }
  }

  getSteps = () => {
    return ['Details', 'Purpose', 'Categories'];
  }

  scrollIntoView = () => {
    this.containerRef?.scrollIntoView({behavior: 'smooth', top: 0});
  }

  handleNext = async () => {
    const { activeStep } = this.state;
    const form = this.evalForm;
    if (activeStep === 0) {
      const nameField = form.fields.name;
      const application_ids = form.fields.application_ids;
      await nameField.validate(true);
      if (!nameField.valid) {
        return;
      }
      if (!application_ids.value) {
        this._vState.errorMsg = "Please select atleast one application"
        return;
      }
    } else if (activeStep == 1) {
      const purposeField = form.fields.purpose;
      await purposeField.validate(true);
      if (!purposeField.valid) {
        return;
      }
      const data = { purpose: form.fields.purpose.value };
      try {
        this._vState.saving = true;
        let response = await this.props.evaluationStore.addCategories(data);
        this._vState.purposeResponse = response;
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
    this.scrollIntoView();
    this.setState((prevState) => ({
      activeStep: prevState.activeStep - 1
    }));
  }

  handleCancel = () => {
    this.props.history.push('/eval_configs');
  }

  handleReset = () => {
    this.setState({
      activeStep: 0
    });
  }

  renderStepContent = (step) => {
    switch (step) {
      case 0:
        return <VEvaluationDetailsForm form={this.evalForm} _vState={this._vState} permission={this.permission}/>;
      case 1:
        return <CEvaluationPurposeForm form={this.evalForm} _vState={this._vState}/>;
      case 2:
        return <CEvaluationCategoriesForm form={this.evalForm} _vState={this._vState}/>;
      default:
        return 'Unknown step';
    }
  }

  handleSaveConfiguration = async () => {
    const form = this.evalForm;
    const categories = form.fields.categories;
    await categories.validate(true);
    if (categories.value.length === 0) {
      this._vState.errorMsg = "Please select atleast one category"
      return;
    }
    const formData = form.toJSON();
    formData.application_ids = formData.application_ids.join(',');
    formData.custom_prompts = [];

    try {
      this._vState.saving = true;
      let response = await this.props.evaluationStore.saveEvaluationConfig(formData);
      this._vState.saving = false;
      f.notifySuccess('Your evaluation is saved successfully');
      this.handlePostSave(response);
      this._vState.saving = false;
    } catch(e) {
      this._vState.saving = false;
      f.handleError()(e);
    }
  } 

  openRunReportModal = async () => {
    const form = this.evalForm;
    const categories = form.fields.categories;
    await categories.validate(true);
    if (categories.value.length === 0) {
      this._vState.errorMsg = "Please select atleast one category"
      return;
    }
    if (this.runReportModalRef.current) {
      this.runReportModalRef.current.show({
        title: 'Run Report',
        btnOkText: 'Run',
        btnCancelText: 'Cancel'
      })
    }
  };

  render() {
    const { handleSaveConfiguration } = this;
    const { activeStep } = this.state;
    const steps = this.getSteps();
	return (
		<BaseContainer
      showRefresh={false}
      showBackButton={true}
		>
      <Paper>
        <Grid container spacing={1} ref={ref => this.containerRef = ref}>
          <Grid item xs={12} sm={3} className='border-right'>
            <Stepper activeStep={activeStep} orientation="vertical" connector={<StepConnector style={{padding: 0}} />} >
              {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
              ))}
            </Stepper>
          </Grid>
          <Grid item xs={12} sm={9} className="m-t-xs">
            {this.renderStepContent(activeStep)}
            <Box component={Paper} elevation={0} p={1} className="sticky-actions border-top" style={{zIndex: 10, opacity: '90%', top: 'calc(100vh - 100px)'}}>
              <Grid container spacing={1} justify="space-between">
                <Grid item>
                  {
                    <Button
                      data-testid="cancel-button"
                      color="primary"
                      onClick={this.handleCancel}
                    >
                      CANCEL
                    </Button>
                  }
                </Grid>
                <Grid item>
                  {activeStep > 0 &&
                    <Button
                      disabled={activeStep === 0 || this._vState.saving}
                      onClick={this.handleBack}
                      color="primary"
                    >
                      Back
                    </Button>
                  }
                  {activeStep === steps.length - 1 && (
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={handleSaveConfiguration}
                      data-testid="save-config-btn"
                      data-track-id="save-config-btn"
                      disabled={this._vState.saving}
                      className="m-l-sm"
                    >
                      Save Configuration
                    </Button>
                  )}
                  <Button
                    variant="contained"
                    color="primary"
                    className="m-l-sm"
                    onClick={activeStep === steps.length - 1 ? this.openRunReportModal : this.handleNext}
                    data-testid="create-app-btn"
                    data-track-id="create-app-btn"
                    disabled={this._vState.saving}
                  >
                    {activeStep === steps.length - 1 ? 'Save And Run' : 'Continue'}
                    {
                      this._vState.saving &&
                      <CircularProgress size="15px" className="m-l-xs" />
                    }
                  </Button>
                </Grid>
              </Grid>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      <FSModal ref={this.runReportModalRef} dataResolve={this.handleCreate}>
        <VRunReportForm form={this.evalForm} mode="create_report"/>
      </FSModal>
	  </BaseContainer>
	)}
}

export default CEvaluationForm;