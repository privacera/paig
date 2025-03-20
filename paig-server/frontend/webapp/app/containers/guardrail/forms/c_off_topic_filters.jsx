import React, {Component, Fragment} from 'react';
import {observable} from 'mobx';
import {observer} from 'mobx-react';

import {Grid, Typography, Box, Paper} from '@material-ui/core';
import {Alert} from '@material-ui/lab';

import {FormGroupSwitch} from 'common-ui/components/form_fields';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import { SearchField } from 'common-ui/components/filters';
import { AddButtonWithPermission } from 'common-ui/components/action_buttons';
import f from 'common-ui/utils/f';
import FSModal from 'common-ui/lib/fs_modal';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {FEATURE_PERMISSIONS, GUARDRAIL_CONFIG_TYPE} from 'utils/globals';
import CResponse from 'containers/guardrail/forms/c_response';
import {VOffTopics} from 'components/guardrail/forms/v_off_topic_filters';
import {VOffTopicFilterForm, off_topic_filter_form_def} from 'components/guardrail/forms/v_off_topic_filter_form';
import {VHeaderWithStatus} from 'components/guardrail/forms/v_guardrail_form_component';

@observer
class COffTopicFilters extends Component {
    @observable _vState = {
        status: false,
        searchValue: ''
    }
    constructor(props) {
        super(props);

        let config = this.props.formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.OFF_TOPIC.NAME);
        if (config) {
            this._vState.status = Boolean(config.status);
        } else {
            config = {
                configType: GUARDRAIL_CONFIG_TYPE.OFF_TOPIC.NAME,
                status: 0,
                responseMessage: '',
                configData: {
                    configs: []
                }
            }

            this.props.formUtil.setData({guardrailConfigs: [...this.props.formUtil.getData().guardrailConfigs, config]});
        }

        this.config = config;

        let models = this.config.configData.configs || [];
        this.cOffTopics = f.initCollection({loading: false}, models);

        this.form = createFSForm(off_topic_filter_form_def);

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.GUARDRAILS.PROPERTY);
    }
    handleEnableFilter = (e) => {
        this._vState.status = e.target.checked;
        this.config.status = +this._vState.status;
    }
    handleOnChange = (e, val) => {
        this._vState.searchValue = val;

        //handle search
    }
    handleResponse = (response) => {
        this.config.responseMessage = response;
    }
    handleAdd = () => {
        this.form.clearForm();
        this.form.model = null;
        this.form.index = null;
        this.Modal.show({
            title: 'Add Off topic',
            btnOkText: 'Add'
        });
    }
    handleEdit = (model, i) => {
        this.form.clearForm();
        this.form.refresh({
            ...model,
            samplePhrases: model.samplePhrases?.join('\n') || ''
        });
        this.form.model = model;
        this.form.index = i;
        this.Modal.show({
            title: 'Edit Off topic',
            btnOkText: 'Save'
        });
    }
    handleRemove = (model) => {
        f._confirm.show({
            title: `Confirm Remove`,
            children: <Fragment>Are you sure want to remove <b>{model.topic}</b> off topic?</Fragment>,
            btnOkVariant: "contained",
            btnOkColor: 'primary'
        })
        .then(confirm => {
            confirm.hide();

            const models = f.models(this.cOffTopics).filter((m) => m.topic !== model.topic);
            f.resetCollection(this.cOffTopics, models);

            this.handleChange();
        }, () => {});
    }
    handleChange = () => {
        this.config.configData.configs = f.models(this.cOffTopics);
    }
    handleSave = async() => {
        let valid = await this.form.validate();
        if (!this.form.valid) return;

        let data = this.form.toJSON();

        data.samplePhrases = data.samplePhrases?.split('\n').map(p => p.trim()).filter(p => p);

        let models = f.models(this.cOffTopics);

        let index = models.findIndex((m, i) =>
            this.form.index !== i && (m.topic || '').toLowerCase() === (data.topic || '').toLowerCase()
        );

        if (index !== -1) {
            f.notifyError(`The topic ${data.topic} already exists`);
            return;
        }

        if (this.form.index != null) {
            Object.assign(models[this.form.index], data);
        } else {
            models.push(data);
        }

        f.resetCollection(this.cOffTopics, models);

        this.Modal.hide();

        this.handleChange();
    }
    render() {
        const error = this.props.formUtil.getErrors();

        return (
            <Fragment>
                <VHeaderWithStatus
                    label="Off Topic filters"
                    description="Utilize customizable filters with off-topics tags or regex patterns to enforce guardrails. Add unwanted topics to a deny list to automatically block associated keywords. This applies only to prompts."
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
                            error.offTopicFilters?.offTopic &&
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <Alert severity="error">
                                        {error.offTopicFilters.offTopic}
                                    </Alert>
                                </Grid>
                            </Grid>
                        }
                        <Grid container spacing={3} className="align-items-center">
                            {/* <SearchField
                                value={this._vState.searchValue}
                                colAttr={{xs: 12, sm: 6, 'data-track-id': 'search-off-topic'}}
                                data-testid="search-off-topic"
                                placeholder="Search Off Topic"
                                onChange={this.handleOnChange}
                            /> */}
                            <Grid item xs={6} sm={6}>
                                <Typography variant="subtitle1">Topics</Typography>
                            </Grid>
                            <AddButtonWithPermission
                                permission={this.permission}
                                colAttr={{xs: 6, sm: 6}}
                                label="Add Off topic"
                                onClick={this.handleAdd}
                            />
                        </Grid>
                        <VOffTopics
                            data={this.cOffTopics}
                            permission={this.permission}
                            handleEdit={this.handleEdit}
                            handleRemove={this.handleRemove}
                        />

                        <FSModal ref={ref => this.Modal = ref}
                            dataResolve={this.handleSave}
                            maxWidth="md"
                        >
                            <VOffTopicFilterForm
                                form={this.form}
                            />
                        </FSModal>
                    </Box>
                }
            </Fragment>
        );
    }
}

export default COffTopicFilters;