import React from 'react';
import {observer} from 'mobx-react';

import {Stepper, Step, StepLabel, StepButton, StepConnector, Typography} from '@material-ui/core';

import CBasicInfo from 'containers/guardrail/forms/c_basic_info';
import CContentModeration from 'containers/guardrail/forms/c_content_moderation';
import CSensitiveDataCategories from 'containers/guardrail/forms/c_sensitive_data_categories';
import COffTopicFilters from 'containers/guardrail/forms/c_off_topic_filters';
import CDeniedTerms from 'containers/guardrail/forms/c_denied_terms';
import CPromptSafety from 'containers/guardrail/forms/c_prompt_safety';
import VReview from 'components/guardrail/forms/v_review';
import CTestGuardrail from 'containers/guardrail/forms/c_test_guardrail';
import CGuardrailApplication from 'containers/guardrail/forms/c_guardrail_application';
import {GUARDRAIL_PROVIDER, GUARDRAIL_CONFIG_TYPE} from 'utils/globals';

const BASIC_INFORMATION = {
    step: 'basic_info',
    title: 'Guardrail Details',
    subtitle: 'Basic information',
    component: CBasicInfo,
    validationFunction: 'validateBasicInfo',
    reviewComponent: 'VBasicInfo'
}

const CONTENT_MODERATION = {
    step: 'content_moderation',
    title: 'Content Moderation',
    subtitle: 'Optional',
    component: CContentModeration,
    configType: GUARDRAIL_CONFIG_TYPE.CONTENT_MODERATION.NAME,
    validationFunction: 'validateContentModeration',
    reviewComponent: 'VContentModeration'
}

const SENSITIVE_DATA_FILTERS = {
    step: 'sensitive_data_filters',
    title: 'Sensitive Data Filters',
    subtitle: 'Optional',
    component: CSensitiveDataCategories,
    configType: GUARDRAIL_CONFIG_TYPE.SENSITIVE_DATA.NAME,
    validationFunction: 'validateSensitiveDataFilters',
    reviewComponent: 'VSensitiveDataFilters'
}

const OFF_TOPIC_FILTERS = {
    step: 'off_topic_filters',
    title: 'Off-topic filters',
    subtitle: 'Optional',
    component: COffTopicFilters,
    configType: GUARDRAIL_CONFIG_TYPE.OFF_TOPIC.NAME,
    validationFunction: 'validateOffTopicFilters',
    reviewComponent: 'VOffTopicFilters'
}

const DENIED_TERMS = {
    step: 'denied_terms',
    title: 'Denied Terms',
    subtitle: 'Optional',
    component: CDeniedTerms,
    configType: GUARDRAIL_CONFIG_TYPE.DENIED_TERMS.NAME,
    validationFunction: 'validateDeniedTerms',
    reviewComponent: 'VDeniedTerms'
}

const PROMPT_SAFETY = {
    step: 'prompt_safety',
    title: 'Prompt Safety',
    subtitle: 'Prompt attacks and injections',
    component: CPromptSafety,
    configType: GUARDRAIL_CONFIG_TYPE.PROMPT_SAFETY.NAME,
    validationFunction: 'validatePromptSafety',
    reviewComponent: 'VPromptSafety'
}

const REVIEW = {
    step: 'review',
    title: 'Review',
    subtitle: 'Guardrail summary',
    component: VReview,
    validationFunction: 'validateReview'
}

const TEST_GUARDRAIL = {
    step: 'test_guardrail',
    title: 'Test Guardrail',
    subtitle: 'Realtime test',
    component: CTestGuardrail,
    validationFunction: 'validateTestGuardrail'
}

const CONNECT_ACCOUNTS = {
    step: 'connect_accounts',
    title: 'Select AI Application and Save',
    subtitle: 'Connect guardrails to accounts',
    component: CGuardrailApplication,
    validationFunction: 'validateGuardrailConnections'
}

const stepsConfig = {
    [GUARDRAIL_PROVIDER.PAIG.NAME]: [
        BASIC_INFORMATION,
        {...SENSITIVE_DATA_FILTERS, subtitle: 'Mandatory'},
        REVIEW,
        TEST_GUARDRAIL,
        CONNECT_ACCOUNTS
    ],
    [GUARDRAIL_PROVIDER.AWS.NAME]: [
        BASIC_INFORMATION,
        CONTENT_MODERATION,
        SENSITIVE_DATA_FILTERS,
        OFF_TOPIC_FILTERS,
        DENIED_TERMS,
        PROMPT_SAFETY,
        REVIEW,
        TEST_GUARDRAIL,
        CONNECT_ACCOUNTS
    ]
}

const getStepsForProvider = (providerName) => stepsConfig[providerName] || [];

// StepRenderer dynamically maps the active step to the corresponding component
const StepRenderer = ({ activeStep, providerName, formUtil, handleProviderChange, onStepClick }) => {
    const steps = getStepsForProvider(providerName);

    // Get the configuration for the current step (based on array index)
    const stepConfig = steps[activeStep];

    if (stepConfig && stepConfig.component) {
        const StepComponent = stepConfig.component;
        return <StepComponent formUtil={formUtil} handleProviderChange={handleProviderChange} onStepClick={onStepClick} />;
    }

    return null; // Fallback for invalid steps
};

const GuardrailStepper = observer(({_vState, stepper, onStepClick}) => {
    return (
        <Stepper activeStep={_vState.activeStep} orientation="vertical"
            data-testid="guardrail-stepper"
            connector={<StepConnector style={{padding: 0}} />}
        >
            {stepper.map((step, index) => {
                let failed = _vState.failedSteps.includes(step.step);
                return (
                    <Step key={index} className="pointer"
                        data-testid={`step-${index}`}
                        onClick={e => onStepClick(step, index)}
                    >
                        <StepLabel error={failed}>
                            <Typography variant="body2" data-testid={`step-${index}-title`} >{step.title}</Typography>
                            {/* <Typography variant="caption" data-testid={`step-${index}-subtitle`}>{step.subtitle}</Typography> */}
                        </StepLabel>
                    </Step>
                )
            })}
        </Stepper>
    )
})

export default GuardrailStepper;
export {
    StepRenderer,
    getStepsForProvider
};