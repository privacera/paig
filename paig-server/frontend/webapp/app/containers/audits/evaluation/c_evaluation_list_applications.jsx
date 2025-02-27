import React, {Component, createRef, Fragment} from 'react';
import {inject, observer} from 'mobx-react';
import {action} from 'mobx';

import {Grid} from '@material-ui/core';

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import FSModal from 'common-ui/lib/fs_modal';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';
import VEvaluationAppsTable from 'components/audits/evaluation/v_evaluation_table_applications';
import {VEvalTargetForm, eval_target_form_def} from "components/audits/evaluation/v_evalutaion_target_form";


const CATEGORIES = {
    NAME: { multi: false, category: "Name", type: "text", key: 'name' }
}

@inject('evaluationStore')
@observer
class CEvaluationAppsList extends Component {
    modalRef = createRef();
    _vState = {
        searchFilterValue: [],
        showNextPage: null,
        prevNextValueList:[''],
        pageNumber: 0,
        new_target: {}
    }
    constructor(props) {
        super(props);
        this.form = createFSForm(eval_target_form_def);
        this.cEvalAppsList = f.initCollection();
        this.cEvalAppsList.params = {
            size: 5,
            sort: 'create_time,desc'
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
    }

    fetchEvaluationAppsList = () => {
        f.beforeCollectionFetch(this.cEvalAppsList);
        this.props.evaluationStore.fetchEvaluationAppsList({
            params: this.cEvalAppsList.params
        }).then(res => {
            console.log('res', res);
            f.resetCollection(this.cEvalAppsList, res.models, res.pageState);            
        },  f.handleError(this.cEvalAppsList));
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
                // Update the form fields to remove the deleted ID
                const updatedApplicationIds = Array.isArray(this.props.form.fields.application_ids.value)
                    ? this.props.form.fields.application_ids.value.filter((id) => id !== model.target_id)
                    : [];
                this.props.form.fields.application_ids.value = updatedApplicationIds;
                this.fetchEvaluationAppsList();
            }, f.handleError(null, null, {confirm}));
        }, () => {});
    }

    handleEdit = async (model) => {
        this.form.clearForm();
        if (!model?.target_id) {
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

        if (!data.id) {
            data.ai_application_id = null;
        }
        // Transform headers array into an object
        if (Array.isArray(data.headers)) {
            data.headers = data.headers.reduce((acc, header) => {
                acc[header.key] = header.value;
                return acc;
            }, {});
        }

        this.modalRef.current.okBtnDisabled(true);
    
        if (data.target_id) {
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
        const {_vState} = this;
        
        return (
            <>
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
                        permission={this.props.permission}
                        label="New Configuration"
                        onClick={this.handleAddNew}
                    />
                </Grid>
                <VEvaluationAppsTable
                    form={this.props.form}
                    data={this.cEvalAppsList}
                    pageChange={this.handlePageChange}
                    _vState={_vState}
                    applicationKeyMap={this.applicationKeyMap}
                    handleDelete={this.handleDelete}
                    handleEdit={this.handleEdit}
                    parent_vState={this.props._vState}
                />
                <FSModal ref={this.modalRef} dataResolve={this.resolveForm}>
                    <VEvalTargetForm form={this.form} _vState={this.props._vState}/>
                </FSModal>
            </>
        );
    }
}

CEvaluationAppsList.defaultProps = {
    vName: 'evaluationAppsList'
}

export default CEvaluationAppsList;