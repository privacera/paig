import React, {Component, Fragment} from 'react';
import {observable} from 'mobx';
import {observer} from 'mobx-react';

import {Grid, Typography, Box, Paper} from '@material-ui/core';
import {Alert} from '@material-ui/lab';

import f from 'common-ui/utils/f';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {FEATURE_PERMISSIONS, GUARDRAIL_CONFIG_TYPE} from 'utils/globals';
import { SearchField } from 'common-ui/components/filters';
import { AddButtonWithPermission } from 'common-ui/components/action_buttons';
import FSModal from 'common-ui/lib/fs_modal';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {FormGroupCheckbox} from 'common-ui/components/form_fields';
import CResponse from 'containers/guardrail/forms/c_response';
import VDeniedTerms from 'components/guardrail/forms/v_denied_terms';
import {VDeniedTermsForm, denied_terms_form_def} from 'components/guardrail/forms/v_denied_terms_form';
import {VHeaderWithStatus} from 'components/guardrail/forms/v_guardrail_form_component';

@observer
class CDeniedTerms extends Component {
    @observable _vState = {
        status: false,
        searchValue: '',
        profanity: true
    }
    constructor(props) {
        super(props);

        let config = this.props.formUtil.getConfigForType(GUARDRAIL_CONFIG_TYPE.DENIED_TERMS.NAME);
        if (config) {
            this._vState.status = Boolean(config.status);
        } else {
            config = {
                configType: GUARDRAIL_CONFIG_TYPE.DENIED_TERMS.NAME,
                status: 0,
                responseMessage: '',
                configData: {
                    configs: [{
                        "type": "PROFANITY",
                        "value": this._vState.profanity
                    }]
                }
            }

            this.props.formUtil.setData({guardrailConfigs: [...this.props.formUtil.getData().guardrailConfigs, config]});
        }

        this.config = config;

        let models = this.config.configData.configs.filter(c => c.term);
        this.cDeniedTerms = f.initCollection({loading: false}, models);

        let profanity = this.config.configData.configs.find(c => c.type === 'PROFANITY');
        if (profanity) {
            this._vState.profanity = profanity.value;
        } else {
            this.config.configData.configs.push({
                "type": "PROFANITY",
                "value": this._vState.profanity
            });
        }

        this.form = createFSForm(denied_terms_form_def);

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
            title: 'Add Phrases and Keywords',
            btnOkText: 'Add'
        });
    }
    handleEdit = (model, i) => {
        this.form.clearForm();
        this.form.refresh({...model, keywords: model.keywords.join('##|##')});
        this.form.model = model;
        this.form.index = i;
        this.Modal.show({
            title: 'Edit Phrases and Keywords',
            btnOkText: 'Save'
        });
    }
    handleRemove = (model) => {
        f._confirm.show({
            title: `Confirm Remove`,
            children: <Fragment>Are you sure want to remove <b>{model.term}</b> terms?</Fragment>,
            btnOkVariant: "contained",
            btnOkColor: 'primary'
        })
        .then(confirm => {
            confirm.hide();

            const models = f.models(this.cDeniedTerms).filter((m) => m.term !== model.term);
            f.resetCollection(this.cDeniedTerms, models);

            this.handleTermsChange();
        }, () => {});
    }
    handleTermsChange = () => {
        let nonTerms = this.config.configData.configs.filter(c => !c.term);
        this.config.configData.configs = [...nonTerms, ...f.models(this.cDeniedTerms)];
    }
    handleSave = async() => {
        let valid = await this.form.validate();
        if (!this.form.valid) return;

        let data = this.form.toJSON();

        data.keywords = data.keywords.split('##|##').filter(k => k.trim());

        let models = f.models(this.cDeniedTerms);

        let duplicateKeywords = [];
        models.forEach((m, i) => {
            if (this.form.index !== i) {
                const existingKeywords = m.keywords || [];
                const newKeywords = data.keywords;
                const duplicates = newKeywords.filter(k => 
                    existingKeywords.some(ek => ek.toLowerCase() === k.toLowerCase())
                );
                if (duplicates.length > 0) {
                    duplicateKeywords.push(...duplicates);
                }
            }
        });

        if (duplicateKeywords.length > 0) {
            f.notifyError(`The keywords ${duplicateKeywords.join(', ')} already exists`);
            return;
        }

        if (this.form.index != null) {
            Object.assign(models[this.form.index], data);
        } else {
            models.push(data);
        }

        f.resetCollection(this.cDeniedTerms, models);
        this.Modal.hide();
        this.handleTermsChange();
    }
    handleProfanityChange = (e) => {
        this._vState.profanity = e.target.checked;
        let terms = this.config.configData.configs.filter(c => c.term);
        this.config.configData.configs = [...terms, {
            "type": "PROFANITY",
            "value": e.target.checked
        }];
    }
    render() {
        const error = this.props.formUtil.getErrors();

        return (
            <Fragment>
                <VHeaderWithStatus
                    label="Denied Terms"
                    description="Use customizable filters with specified terms or regex patterns to enforce guardrails. Add unwanted terms to a deny list to automatically block related keywords or phrases. This applies to both prompts and responses."
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
                            error.deniedTermsFilters?.deniedTerms &&
                            <Grid container spacing={3} className="m-b-xs">
                                <Grid item xs={12}>
                                    <Alert severity="error" data-testid="denied-terms-error-alert">
                                        {error.deniedTermsFilters.deniedTerms}
                                    </Alert>
                                </Grid>
                            </Grid>
                        }
                        <Grid container>
                            <Grid item xs={12}>
                                <Typography variant="subtitle1">Profanity Filter</Typography>
                            </Grid>
                            <Grid item xs={12}>
                                <Typography variant="body2" color="textSecondary">Detects and filters offensive language, prevents unsuitable content from being displayed.</Typography>
                            </Grid>
                            <FormGroupCheckbox
                                label="Block all profanity"
                                data-testid="profanity-filter"
                                checked={this._vState.profanity}
                                onChange={this.handleProfanityChange}
                            />
                        </Grid>
                        <Grid container spacing={3} className="align-items-center m-t-sm">
                            {/* <SearchField
                                value={this._vState.searchValue}
                                colAttr={{xs: 12, sm: 6, 'data-track-id': 'search-off-topic'}}
                                data-testid="search-off-topic"
                                placeholder="Search Off Topic"
                                onChange={this.handleOnChange}
                            /> */}
                            <Grid item xs={6} sm={6}>
                                <Typography variant="subtitle1">Terms</Typography>
                            </Grid>
                            <AddButtonWithPermission
                                permission={this.permission}
                                colAttr={{xs: 6, sm: 6}}
                                label="Add Terms"
                                onClick={this.handleAdd}
                            />
                        </Grid>
                        <VDeniedTerms
                            data={this.cDeniedTerms}
                            permission={this.permission}
                            handleEdit={this.handleEdit}
                            handleRemove={this.handleRemove}
                        />
                        <FSModal ref={ref => this.Modal = ref}
                            dataResolve={this.handleSave}
                            maxWidth="md"
                        >
                            <VDeniedTermsForm
                                form={this.form}
                            />
                        </FSModal>
                    </Box>
                }
            </Fragment>
        )
    }
}

export default CDeniedTerms;