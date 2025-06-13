import React, {Component, createRef, Fragment} from 'react';
import {inject} from 'mobx-react';
import {action} from 'mobx';

import {Grid} from '@material-ui/core';
import Alert from '@material-ui/lab/Alert';

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import FSModal from 'common-ui/lib/fs_modal';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';
import VEvaluationAppsTable from 'components/audits/evaluation/v_evaluation_table_applications';
import {VEvalTargetForm, eval_target_form_def} from "components/audits/evaluation/v_evalutaion_target_form";
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import { DEFAULTS } from "common-ui/utils/globals";


const CATEGORIES = {
    NAME: { multi: false, category: "Name", type: "text", key: 'name' }
}

@inject('evaluationStore', 'aiApplicationStore')
class CEvaluationAppsList extends Component {    
    modalRef = createRef();
    _vState = {
        searchFilterValue: [],
        showNextPage: null,
        prevNextValueList:[''],
        pageNumber: 0,
        new_target: {},
        aiApplications: []
    }
    constructor(props) {
        super(props);
        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.EVALUATION_CONFIG.PROPERTY);
        this.form = createFSForm(eval_target_form_def);
        this.cEvalAppsList = f.initCollection();
        this.cEvalAppsList.params = {
            size: this.props.appPageSize || DEFAULTS.DEFAULT_PAGE_SIZE,
            sort: 'create_time,desc'
        }
        this.cApplications = f.initCollection();
        this.cApplications.params = {
            size: 1000
        }
        this.applicationKeyMap = {};

        this.restoreState();
    }
    componentDidMount() {
        this.handleRefresh();
    }
    componentWillUnmount() {
        let {_vState} = this;
        let {params} = this.cEvalAppsList;
        let {vName} = this.props;
        let data = JSON.stringify({params, _vState});
        UiState.saveState(vName, data);
    }
    @action
    restoreState() {
        let data = UiState.getStateData(this.props.vName)
        if (!data) {
          return;
        }
        Object.assign(this, {
          _vState: data._vState
        });
        this.cEvalAppsList.params = data.params;
    }
    handleRefresh = () => {
        this.fetchEvaluationAppsList();
        this.fetchAIApplications();
    }

    fetchEvaluationAppsList = () => {
        f.beforeCollectionFetch(this.cEvalAppsList);
        this.props.evaluationStore.fetchEvaluationAppsList({
            params: this.cEvalAppsList.params
        }).then(res => {
            f.resetCollection(this.cEvalAppsList, res.models, res.pageState);            
        },  f.handleError(this.cEvalAppsList));
    }

    fetchAIApplications = async() => {
        f.beforeCollectionFetch(this.cApplications)
        try {
            const res = await this.props.aiApplicationStore.getAIApplications({
                params: this.cApplications.params
            });

            let models = res.models.filter(app => !app.default);

            f.resetCollection(this.cApplications, models);
        } catch(e) {
            f.handleError(this.cApplications)(e);
        }
    }
    handlePageChange = () => {
        this.fetchEvaluationAppsList();
    };

    handleSearchByField = (filter, event) => {
        this._vState.prevNextValueList = [''];
        this._vState.pageNumber = 0;
        let params = {
            page: undefined
        };
        Object.values(CATEGORIES).forEach(obj => {
            params['includeQuery.' + obj.key] = undefined;
            params['excludeQuery.' + obj.key] = undefined;
        })
        filter.forEach(({ category, operator, value }) => {
            const obj = Object.values(CATEGORIES).find(item => item.category === category);
            if (obj) {
            const prefix = operator === 'is' ? 'includeQuery' : 'excludeQuery';
            params[`${prefix}.${obj.key}`] = value;
            }
        });
        Object.assign(this.cEvalAppsList.params, params);

        this._vState.searchFilterValue = filter;
        this.fetchEvaluationAppsList();
    }

    handleDelete = (model) => {
        f._confirm.show({
            title: `Delete Application Config`,
            children: <Fragment>Are you sure you want to delete <b>{model.name}</b> application configs?</Fragment>,
            btnCancelText: 'Cancel',
            btnOkText: 'Delete',
            btnOkColor: 'secondary',
            btnOkVariant: 'text'
        })
        .then((confirm) => {
            this.props.evaluationStore.deleteAppTarget(model.target_id,{
            models: this.cEvalAppsList
            })
            .then(() => {
                confirm.hide();
                f.notifySuccess('Application Config Deleted');
                f.handlePagination(this.cEvalAppsList, this.cEvalAppsList.params);
                // Update the form fields to remove the deleted ID
                if (this.props.form && this.props.form.fields) {
                    const updatedApplicationIds = Array.isArray(this.props.form.fields.application_ids.value)
                    ? this.props.form.fields.application_ids.value.filter((id) => id !== model.target_id)
                    : [];
                    this.props.form.fields.application_ids.value = updatedApplicationIds;
                }
                this.fetchEvaluationAppsList();
            }, f.handleError(null, null, {confirm}));
        }, () => {});
    }

    handleEdit = async (model) => {
        this.form.clearForm();
        if (model?.status !== 'ACTIVE') {
            this.form.refresh(model);
            this.showEditModal();
            return;
        }
        this.form.refresh(model);
        try {
            const response = await this.props.evaluationStore.fetchTargetConfig(model);
            const { config, name, url, id } = response;
            this.form.refresh({
                ...response,
                method: config.method,
                headers: config.headers ? Object.entries(config.headers).map(([key, value]) => ({ key, value })) : [],
                body: JSON.stringify(config.body, null, 2),
                transformResponse: config.transformResponse,
                url: config.url || url
            });
        } catch (error) {
            console.error("Error fetching target config:", error);
            f.notifyError("Failed to load configuration.");
            return;
        }

        this.showEditModal();
    };

    showEditModal = () => {
        this.modalRef.current.show({
            title: "Edit Configuration"
        });
    };

    handleAddNew = () => {
        this.form.clearForm();
        if (this.modalRef.current) {
            this.modalRef.current.show({
              title: 'Add Configuration',
              btnOkText: 'Save',
              btnCancelText: 'Cancel'
            })
        }
    }

    resolveForm = async () => {
        await this.form.validate();
        if (!this.form.valid) {
          return;
        }
        let data = this.form.toJSON();
        data = Object.assign({}, this.form.model, data);

        // Transform headers array into an object
        if (Array.isArray(data.headers)) {
            data.headers = data.headers.reduce((acc, header) => {
                acc[header.key] = header.value;
                return acc;
            }, {});
        }

        this.modalRef.current.okBtnDisabled(true);
    
        if (data.status === 'ACTIVE') {
          try {
            await this.props.evaluationStore.updateConfig(data);
            this.modalRef.current.hide();
            f.notifySuccess("Configuration updated successfully");
            this.fetchEvaluationAppsList();
          } catch (e) {
            f.handleError(null, null, {modal: this.modalRef.current})(e);
            console.error("Error updating configuration:", e);
          }
        } else {
          delete data.id;
          try {
            await this.props.evaluationStore.addConfig(data);
            this.modalRef.current.hide();
            f.notifySuccess("Configuration added successfully");
            this.fetchEvaluationAppsList();
          } catch (e) {
            f.handleError(null, null, {modal: this.modalRef.current})(e);
            console.error("Error creating configuration:", e);
          }
        }
    }

    render() {
        const {_vState, tabsState} = this;
        return (
            <>
                {this.props.tabsState && (
                    <Grid container spacing={3}>
                    <Grid item xs={12}>
                        <Alert severity="info">
                        Create and configure an AI endpoint by providing its name, url and headers - you can then use it in an evaluation
                        </Alert>
                    </Grid>
                    </Grid>
                )}
                <Grid container spacing={3}>
                    <Grid item xs={6} sm={6} md={6} lg={6}>
                        <IncludeExcludeComponent
                            _vState={_vState}
                            categoriesOptions={Object.values(CATEGORIES)}
                            onChange={this.handleSearchByField}
                        />
                    </Grid>
                    <AddButtonWithPermission
                        colAttr={{
                            xs: 6,
                            sm: 6,
                            md: 6
                        }}
                        permission={this.permission}
                        label={this.props.tabsState?"Add New":"New Configuration"}
                        onClick={this.handleAddNew}
                    />
                </Grid>
                <VEvaluationAppsTable
                    permission={this.permission}
                    form={this.props.form}
                    data={this.cEvalAppsList}
                    pageChange={this.handlePageChange}
                    _vState={_vState}
                    applicationKeyMap={this.applicationKeyMap}
                    handleDelete={this.handleDelete}
                    handleEdit={this.handleEdit}
                    parent_vState={this.props._vState}
                    tabsState={this.props.tabsState}
                />
                <FSModal ref={this.modalRef} dataResolve={this.resolveForm}>
                    <VEvalTargetForm 
                        form={this.form} 
                        _vState={this.props._vState} 
                        cApplications={this.cApplications}
                        evaluationStore={this.props.evaluationStore}
                    />
                </FSModal>
            </>
        );
    }
}

CEvaluationAppsList.defaultProps = {
    vName: 'evaluationAppsList'
}

export default CEvaluationAppsList;