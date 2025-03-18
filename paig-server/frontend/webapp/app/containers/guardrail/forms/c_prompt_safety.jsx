import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';
import {observable} from 'mobx';

import {Grid, Typography, Slider, Box, Paper} from '@material-ui/core';
import {Alert} from '@material-ui/lab';

import f from 'common-ui/utils/f';
import {GUARDRAIL_CONFIG_TYPE} from 'utils/globals';
import {FormGroupSwitch} from 'common-ui/components/form_fields';
import {VHeaderWithStatus} from 'components/guardrail/forms/v_guardrail_form_component';
import CResponse from 'containers/guardrail/forms/c_response';

@observer
class CPromptSafety extends Component {
    @observable _vState = {
        status: false,
        promptAttack: 'MEDIUM'
    }
    marks = [
        {
            value: 0,
            label: 'None'
        },
        {
            value: 33,
            label: 'LOW'
        },
        {
            value: 66,
            label: 'MEDIUM'
        },
        {
            value: 100,
            label: 'HIGH'
        }
    ]
    constructor(props) {
        super(props);

        let config = this.props.formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.PROMPT_SAFETY.NAME);
        if (config) {
            this._vState.status = Boolean(config.status);
        } else {
            config = {
                configType: GUARDRAIL_CONFIG_TYPE.PROMPT_SAFETY.NAME,
                status: 0,
                responseMessage: '',
                configData: {
                    configs: [{
                        "category": "PROMPT_ATTACK",
                        "filterStrengthPrompt": "MEDIUM"
                    }]
                }
            }

            this.props.formUtil.setData({guardrailConfigs: [...this.props.formUtil.getData().guardrailConfigs, config]});
        }

        this.config = config;

        this._vState.promptAttack = this.config.configData.configs[0].filterStrengthPrompt
    }
    handleEnableFilter = (e) => {
        this._vState.status = e.target.checked;
        this.config.status = +this._vState.status;
    }
    handleResponse = (response) => {
        this.config.responseMessage = response;
    }
    handleChange = (e, val) => {
        this._vState.promptAttack = this.marks.find(m => m.value === val).label;
        this.config.configData.configs[0].filterStrengthPrompt = this._vState.promptAttack;
    }
    render() {
        const error = this.props.formUtil.getErrors();

        const value = this.marks.find(m => m.label === this._vState.promptAttack).value || 0;

        return (
            <Fragment>
                <VHeaderWithStatus
                    label="Prompt Safety"
                    description="Guardrails prevent prompt injections by validating inputs, filtering harmful patterns, and analyzing context to block malicious instructions. They ensure user input cannot manipulate or mislead the model into unsafe behavior."
                    status={this._vState.status}
                    onChange={this.handleEnableFilter}
                />
                {
                    this._vState.status &&
                    <Box component={Paper} elevation={0} p="15px" className="border-top">
                        <CResponse
                            value={this.config.responseMessage}
                            onChange={this.handleResponse}
                        />
                        {
                            error.promptSafetyFilters?.promptSafety &&
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <Alert severity="error">
                                        {error.promptSafetyFilters.promptSafety}
                                    </Alert>
                                </Grid>
                            </Grid>
                        }
                        <Grid container>
                            <Grid item xs={12}>
                                <Typography variant="subtitle1" gutterBottom>
                                    Prompt attack sensitivity
                                </Typography>
                                <Typography variant="body2" gutterBottom color="textSecondary">
                                    The prompts attack sensitivity slider adjusts the system's ability to detect and defend against prompt injection or manipulation attempts.
                                    Higher sensitivity enhances protection by applying stricter checks, while lower sensitivity offers more flexibility but may reduce resilience to advanced attacks.
                                </Typography>
                            </Grid>
                            <Grid item xs={12} sm={8} style={{paddingLeft: '20px'}}>
                                <Slider
                                    value={value}
                                    onChange={this.handleChange}
                                    valueLabelFormat={val => `${val}%`}
                                    getAriaValueText={val => `${val}%`}
                                    aria-labelledby="prompt attack sensitivity"
                                    step={null}
                                    valueLabelDisplay="auto"
                                    marks={this.marks}
                                />
                            </Grid>
                        </Grid>
                    </Box>
                }
            </Fragment>
        )
    }
}

export default CPromptSafety;