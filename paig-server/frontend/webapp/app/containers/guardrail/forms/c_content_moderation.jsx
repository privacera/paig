import React, {Component, Fragment} from 'react';
import {observable} from 'mobx';
import {observer} from 'mobx-react';

import {Grid, Typography, Box, Paper} from '@material-ui/core';
import {Alert} from '@material-ui/lab';

import f from 'common-ui/utils/f';
import {FormGroupSwitch} from 'common-ui/components/form_fields';
import {GUARDRAIL_CONFIG_TYPE} from 'utils/globals';
import {content_moderation_list} from 'components/guardrail/forms/content_moderation_list';
import {VContentModeration} from 'components/guardrail/forms/v_content_moderation';
import {VHeaderWithStatus} from 'components/guardrail/forms/v_guardrail_form_component';
import CResponse from 'containers/guardrail/forms/c_response';
import MContentModeration from 'data/models/m_content_moderation';

@observer
class CContentModeration extends Component {
    @observable _vState = {
        status: false,
        contentModeration: {}
    }
    constructor(props) {
        super(props);

        let config = this.props.formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.CONTENT_MODERATION.NAME);
        if (config) {
            this._vState.status = Boolean(config.status);
        } else {
            config = {
                configType: GUARDRAIL_CONFIG_TYPE.CONTENT_MODERATION.NAME,
                status: 0,
                responseMessage: '',
                configData: {
                    configs: []
                }
            }

            this.props.formUtil.setData({guardrailConfigs: [...this.props.formUtil.getData().guardrailConfigs, config]});
        }

        this.config = config;

        const provider = this.props.formUtil.getProvider();

        let contentModerationList = content_moderation_list.filter(c => c.providers.includes(provider)).map(c => new MContentModeration(c));

        contentModerationList.forEach(m => {
            let configData = this.config.configData.configs.find(c => c.category === m.category);
            if (configData) {
                m.filterSelected = true;
                m.filterStrengthPrompt = configData.filterStrengthPrompt;
                m.filterStrengthResponse = configData.filterStrengthResponse;

                if (m.filterStrengthPrompt !== m.filterStrengthResponse) {
                    m.customReply = true;
                }
            }
        });

        this.cContentModeration = f.initCollection({loading: false}, contentModerationList);
    }
    handleEnableFilter = (e) => {
        this._vState.status = e.target.checked;
        this.config.status = +this._vState.status;
    }
    handleContentSelection = (model, isChecked) => {
        let configs = this.config.configData.configs;
        let configIndex = configs.findIndex(c => c.category === model.category);

        model.filterSelected = isChecked;

        if (isChecked) {
            if (configIndex === -1) {
                configs.push({
                    category: model.category,
                    guardrailProvider: this.props.formUtil.getProvider(),
                    filterStrengthPrompt: model.filterStrengthPrompt,
                    filterStrengthResponse: model.filterStrengthResponse
                });
            }
        } else if (configIndex !== -1) {
            configs.splice(configIndex, 1);
        }
    }
    handleCustomizeReplyChange = (e, model) => {
        model.customReply = e.target.checked;
        if (!model.customReply) {
            this.handleStrengthChange(model.filterStrengthPrompt, model);
        }
    }
    handleStrengthChange = (val, model) => {
        model.filterStrengthPrompt = val;
        if (!model.customReply) {
            model.filterStrengthResponse = val;
        }

        let configs = this.config.configData.configs;
        let configIndex = configs.findIndex(c => c.category === model.category);
        if (configIndex !== -1) {
            configs[configIndex].filterStrengthPrompt = model.filterStrengthPrompt;
            configs[configIndex].filterStrengthResponse = model.filterStrengthResponse;
        }
    }
    handleStrengthResponseChange = (val, model) => {
        model.filterStrengthResponse = val;

        let configs = this.config.configData.configs;
        let configIndex = configs.findIndex(c => c.category === model.category);
        if (configIndex !== -1) {
            configs[configIndex].filterStrengthResponse = model.filterStrengthResponse;
        }
    }
    handleResponse = (response) => {
        this.config.responseMessage = response;
    }
    render() {
        const error = this.props.formUtil.getErrors();

        return (
            <Fragment>
                <VHeaderWithStatus
                    label="Content Moderation"
                    description="Enable detection and blocking of harmful user inputs and model responses. Increase filter strength to enhance the likelihood of filtering harmful content in specific categories. This applies to both prompts and responses."
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
                            error.contentModerationFilters?.contentModeration &&
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <Alert severity="error" data-testid="content-moderation-error-alert">
                                        {error.contentModerationFilters.contentModeration}
                                    </Alert>
                                </Grid>
                            </Grid>
                        }
                        <VContentModeration
                            data={this.cContentModeration}
                            handleContentSelection={this.handleContentSelection}
                            handleStrengthChange={this.handleStrengthChange}
                            handleStrengthResponseChange={this.handleStrengthResponseChange}
                            handleCustomizeReplyChange={this.handleCustomizeReplyChange}
                        />
                    </Box>
                }
            </Fragment>
        )
    }
}

export default CContentModeration;