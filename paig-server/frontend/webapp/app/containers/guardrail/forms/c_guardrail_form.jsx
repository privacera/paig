import React, {Component} from 'react';
import {observer, inject} from 'mobx-react';
import {observable, transaction} from 'mobx';

import {Grid, Box, Paper, Button, CircularProgress} from '@material-ui/core';

import f from 'common-ui/utils/f';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import { Loader, getSkeleton } from 'common-ui/components/generic_components'
import {FEATURE_PERMISSIONS} from 'utils/globals';
import BaseContainer from 'containers/base_container';
import GuardrailStepper, {StepRenderer, getStepsForProvider} from 'components/guardrail/forms/v_guardrail_stepper';
import {GuardrailFormUtil, initialData} from 'components/guardrail/forms/guardrail_form_util';

@inject('guardrailStore', 'aiApplicationStore')
@observer
class CGuardrailForm extends Component {
    @observable _vState = {
        activeStep: 0,
        failedSteps: [],
        guardrail: null,
        editMode: false,
        providerName: '',
        saving: false
    }
    stepper=[];
    constructor(props) {
        super(props);

        this.formUtil = new GuardrailFormUtil(initialData);

        this._vState.providerName = this.formUtil.getProvider();

        if (this.props.match.params.id) {
            this._vState.editMode = true;
        }

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.GUARDRAILS.PROPERTY);
    }
    componentDidMount() {
        let id = this.props.match.params.id || this.props.match.params.newId;
        if (id) {
            this.fetchGuardrail(id, !!this.props.match.params.newId);
        }
    }
    fetchGuardrail = async(id, moveToNextStep) => {
        try {
            const guardrail = await this.props.guardrailStore.getGuardrail(id);
            this.setGuardrail(guardrail, moveToNextStep);
        } catch(e) {
            this._vState.guardrail = null;
            f.handleError()(e);
        }
    }
    setGuardrail = (guardrail, moveToNextStep) => {
        guardrail.guardrailConfigs?.forEach(c => {
            c.status = 1;
        })
        transaction(() => {
            this.formUtil.resetData(guardrail);
            this._vState.guardrail = guardrail;
            this._vState.providerName = this.formUtil.getProvider();
        });
        if (moveToNextStep) {
            setTimeout(() => {
                let index = this.stepper?.findIndex(step => step.step === 'test_guardrail')
                if (index !== -1) {
                    this._vState.activeStep = index;
                }
            }, 1000);
        }
    }
    handleBack = () => {
        this.scrollIntoView();
        this._vState.activeStep -= 1;
    }
    handleCancel = () => {
        this.props.history.push('/guardrails');
    }
    getReviewIndex = () => {
        let index = this.stepper?.findIndex(s => s.step === 'Review');
        if (index === -1) {
            index = this.stepper?.length - 3;
        }
        return index;
    }
    handleSkipToReview = async() => {
        let index = this.getReviewIndex();

        if (index === -1) {
            return;
        }

        let valid = await this.validateStep();
        if (valid) {
            let currentStep = this.stepper[this._vState.activeStep];
            this._vState.failedSteps = this._vState.failedSteps.filter(step => step !== currentStep?.step);
        }

        this.scrollIntoView();
        this._vState.activeStep = index;

    }
    isReviewStep() {
        return this.stepper?.findIndex(step => step.step === 'review') === this._vState.activeStep;
    }
    isLastStep() {
        let totalSteps = this.stepper?.length || 0;
        return (totalSteps-1) === this._vState.activeStep;
    }
    handleContinue = async () => {
        if (this.isReviewStep()) {
            let saved = await this.handleSave();
            if (saved) {
                this.scrollIntoView();
                //this._vState.activeStep += 1;
            }
            return;
        }
        if (this.isLastStep()) {
            this.handleSave();
            return;
        }

        let valid = await this.validateStep();
        if (!valid) {
            return;
        }

        let currentStep = this.stepper[this._vState.activeStep];

        this._vState.failedSteps = this._vState.failedSteps.filter(step => step !== currentStep?.step);

        this.scrollIntoView();
        this._vState.activeStep += 1;
    }
    validateStep = async() => {
        let currentStep = this.stepper[this._vState.activeStep];

        let validationFunction = currentStep?.validationFunction;
        let valid = this.formUtil.validateFunction(validationFunction);
        if (!valid) {
            this._vState.failedSteps.push(currentStep.step);
        }
        return valid;
    }
    scrollIntoView = () => {
        this.containerRef?.scrollIntoView({behavior: 'smooth', top: 0});
    }
    handleStepClick = async(step, i) => {
        if (this._vState.activeStep === i) {
            return;
        }
        this.scrollIntoView();

        let valid = await this.validateStep();
        if (valid) {
            let currentStep = this.stepper[this._vState.activeStep];
            this._vState.failedSteps = this._vState.failedSteps.filter(step => step !== currentStep?.step);
        }

        this._vState.activeStep = i;
    }
    handleProviderChange = (provider) => {
        this._vState.providerName = provider || this.formUtil.getProvider();
    }
    handleSave = async() => {
        let validate = this.formUtil.validate();
        if (!validate.valid) {
            this._vState.failedSteps = validate.failedSteps || this._vState.failedSteps;
            return;
        }

        let data = this.formUtil.getSaveFormData();

        if (!data.guardrailConfigs?.length) {
            f.notifyError('Please enable at least one filter to continue');
            return;
        }

        try {
            this._vState.saving = true;
            if (data.id) {
                let apps = this.formUtil.getApps();
                if (apps) {
                    await this.props.aiApplicationStore.associateGuardrailToApplication({
                        guardrail: data.name,
                        applications: apps
                    });
                }

                let model = await this.props.guardrailStore.updateGuardrail(data.id, data);
                f.notifySuccess(`Guardrail ${data.name} updated successfully`);
                this.setGuardrail(model, true);
            } else {
                let model = await this.props.guardrailStore.createGuardrail(data);
                f.notifySuccess(`Guardrail ${data.name} created successfully`);
                this.setGuardrail(model);
                this.props.history.replace(`/guardrails/create/${model.id}`);
            }

            if (this.isLastStep()) {
                this.props.history.push('/guardrails');
            }

            this._vState.saving = false;
            return true;
        } catch(e) {
            this._vState.saving = false;
            f.handleError()(e);
            console.log(e);
        }
    }
    render() {
        this.stepper = getStepsForProvider(this._vState.providerName);
        const reviewIndex = this.getReviewIndex();

        this.formUtil.setSteps(this.stepper);

        let data = this.formUtil.getData();

        return (
            <BaseContainer
                showRefresh={false}
                showBackButton={true}
            >
                <Loader isLoading={this._vState.editMode && !this._vState.guardrail} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                    <Paper>
                        <Grid container spacing={1} ref={ref => this.containerRef = ref}>
                            <Grid item xs={12} sm={3} className="border-right">
                                <GuardrailStepper
                                    _vState={this._vState}
                                    stepper={this.stepper}
                                    onStepClick={this.handleStepClick}
                                />
                            </Grid>
                            <Grid item xs={12} sm={9} className="m-t-xs">
                                <StepRenderer
                                    activeStep={this._vState.activeStep}
                                    providerName={this._vState.providerName}
                                    formUtil={this.formUtil}
                                    handleProviderChange={this.handleProviderChange}
                                    onStepClick={this.handleStepClick}
                                />
                                <Box component={Paper} elevation={0} p={1} className="sticky-actions border-top" style={{zIndex: 10, opacity: '90%', top: 'calc(100vh - 100px)'}}>
                                    <Grid container spacing={1} justify="space-between" data-testid="sticky-action-buttons">
                                        <Grid item>
                                            <Button
                                                data-testid="cancel-button"
                                                color="primary"
                                                onClick={this.handleCancel}
                                            >
                                                CANCEL
                                            </Button>
                                        </Grid>
                                        <Grid item>
                                            {
                                                this._vState.activeStep > 0 && reviewIndex !== -1 && this._vState.activeStep < reviewIndex &&
                                                <Button
                                                    data-testid="skip-to-review"
                                                    className="m-l-sm"
                                                    color="primary"
                                                    onClick={this.handleSkipToReview}
                                                >
                                                    SKIP TO REVIEW
                                                </Button>
                                            }
                                            {
                                                this._vState.activeStep > 0 &&
                                                <Button
                                                    data-testid="back-button"
                                                    color="primary"
                                                    onClick={this.handleBack}
                                                >
                                                    BACK
                                                </Button>
                                            }
                                            <Button
                                                data-testid="continue-button"
                                                variant="contained"
                                                color="primary"
                                                className="m-l-sm"
                                                disabled={this._vState.saving || (!data.id && reviewIndex !== -1 && this._vState.activeStep > reviewIndex)}
                                                onClick={this.handleContinue}
                                            >
                                                {this._vState.saving ? <CircularProgress size={24} /> : null}
                                                {
                                                    this.isLastStep() ?
                                                    'FINISH' :
                                                    (
                                                        this.isReviewStep()?
                                                        'SAVE AND CONTINUE' :
                                                        'CONTINUE'
                                                    )
                                                }
                                            </Button>
                                        </Grid>
                                    </Grid>
                                </Box>
                            </Grid>
                        </Grid>
                    </Paper>
                </Loader>
            </BaseContainer>
        );
    }
}

export default CGuardrailForm;