import React, {Component, Fragment} from 'react';
import {observable} from 'mobx';
import {observer} from 'mobx-react';

import {Grid, Typography, Tabs, Tab, Box, Paper} from '@material-ui/core';
import {Alert} from '@material-ui/lab';

import f from 'common-ui/utils/f';
import {FormGroupSwitch} from 'common-ui/components/form_fields';
import { TabPanel } from 'common-ui/components/generic_components';
import {GUARDRAIL_CONFIG_TYPE, GUARDRAIL_PROVIDER} from 'utils/globals';
import CResponse from 'containers/guardrail/forms/c_response';
import CSensitiveDataElements from 'containers/guardrail/forms/c_sensitive_data_elements';
import CSensitiveDataRegex from 'containers/guardrail/forms/c_sensitive_data_regex';
import {VHeaderWithStatus} from 'components/guardrail/forms/v_guardrail_form_component';

@observer
class CSensitiveDataCategories extends Component {
    @observable _vState = {
        status: false,
        defaultState: 0
    }
    constructor(props) {
        super(props);

        let config = this.props.formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.SENSITIVE_DATA.NAME);
        if (config) {
            this._vState.status = Boolean(config.status);
        } else {
            config = {
                configType: GUARDRAIL_CONFIG_TYPE.SENSITIVE_DATA.NAME,
                status: 0,
                responseMessage: '',
                configData: {
                    configs: []
                }
            }

            this.props.formUtil.setData({guardrailConfigs: [...this.props.formUtil.getData().guardrailConfigs, config]});
        }

        this.config = config;
    }
    handleEnableFilter = (e) => {
        this._vState.status = e.target.checked;
        this.config.status = +this._vState.status;
    }
    handleTabSelect = (index) => {
        this._vState.defaultState = index;
    }
    getSensitiveElementsConfig = () => {
        return this.config.configData.configs.filter(d => d.category);
    }
    getRegexConfig = () => {
        return this.config.configData.configs.filter(d => d.type === 'regex');
    }
    handleSensitiveElementsChange = (data=[]) => {
        let nonElements = this.config.configData.configs.filter(d => !d.category);
        this.config.configData.configs = [...nonElements, ...data];
    }
    handleRegexChange = (data=[]) => {
        let nonRegex = this.config.configData.configs.filter(d => d.type !== 'regex');
        this.config.configData.configs = [...nonRegex, ...data];
    }
    handleResponse = (response) => {
        this.config.responseMessage = response;
    }
    render() {
        const error = this.props.formUtil.getErrors();
        const provider = this.props.formUtil.getProvider();

        let description = ''
        if (!provider || provider !== GUARDRAIL_PROVIDER.PAIG.NAME) {
            description = 'This functionality consists of two components: elements and regex, working together to ensure comprehensive coverage.'
        }

        return (
            <Fragment>
                <VHeaderWithStatus
                    label="Sensitive Data Filters"
                    description={`Enable the detection and blocking of sensitive data. Configure actions such as masking or redacting detected data to suit your needs. ${description} This applies to both prompt and responses.`}
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
                            error.sensitiveDataFilters?.sensitiveData &&
                            <Grid container spacing={3}>
                                <Grid item xs={12} data-testid="sensitive-data-error-alert">
                                    <Alert severity="error">
                                        {error.sensitiveDataFilters.sensitiveData}
                                    </Alert>
                                </Grid>
                            </Grid>
                        }
                        <Tabs value={this._vState.defaultState} indicatorColor="primary"
                            textColor="primary" scrollButtons="auto" variant="scrollable"
                            className="tabs-view m-t-md"
                            data-testid="sensitive-data-tabs"
                        >
                            <Tab
                                label="ELEMENTS"
                                onClick={(e) => this.handleTabSelect(0)}
                                data-testid="elements-tab"
                            />
                            {
                                provider !== GUARDRAIL_PROVIDER.PAIG.NAME &&
                                <Tab
                                    label="REGEX"
                                    onClick={(e) => this.handleTabSelect(1)}
                                    data-testid="regex-tab"
                                />
                            }
                        </Tabs>
                        <TabPanel value={this._vState.defaultState} index={0} p={0} mt="10px">
                            <CSensitiveDataElements
                                onChange={this.handleSensitiveElementsChange}
                                getConfigs={this.getSensitiveElementsConfig}
                            />
                        </TabPanel>
                        <TabPanel value={this._vState.defaultState} index={1} p={0} mt="10px">
                            <CSensitiveDataRegex
                                onChange={this.handleRegexChange}
                                getConfigs={this.getRegexConfig}
                            />
                        </TabPanel>
                    </Box>
                }
            </Fragment>
        )
    }
}

export default CSensitiveDataCategories;