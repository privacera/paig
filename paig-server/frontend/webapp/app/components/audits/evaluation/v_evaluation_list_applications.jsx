import React, {Component, createRef} from 'react';
import {inject, observer} from 'mobx-react';
import {action} from 'mobx';
import {Grid} from '@material-ui/core';
import BaseContainer from 'containers/base_container';
import UiState from 'data/ui_state';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';
import {AddButton} from 'common-ui/components/action_buttons';
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';
import VEvaluationAppsTable from 'components/audits/evaluation/v_evaluation_table_applications';
import FSModal,{Confirm} from 'common-ui/lib/fs_modal';
import { FormHorizontal, FormGroupInput, FormGroupSelect2, Form } from 'common-ui/components/form_fields';
import FormLabel from '@material-ui/core/FormLabel';
import FormGroup from '@material-ui/core/FormGroup';
import TextField from '@material-ui/core/TextField';
import VEvalTargetForm, {eval_target_form_def} from "./v_evalutaion_target_form"
import { createFSForm } from 'common-ui/lib/form/fs_form';


const CATEGORIES = {
    Name: { multi: false, category: "Name", type: "text", key: 'name' }
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
            size: 10,
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

    handlePageChange = (isPrevious) => {
        let page = this._vState.pageNumber;
        if (isPrevious) {
            page--;
            this._vState.prevNextValueList.pop()
        } else {
            page++;
            this._vState.prevNextValueList.push(page)
        }
        this._vState.pageNumber = page
        this.cEvalAppsList.params.page = page || undefined;
        this.fetchEvaluationAppsList();
    }

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

        filter.forEach((item) => {
            let obj = CATEGORIES[item.category];
            let prefix = item.operator == 'is' ? 'includeQuery' : 'excludeQuery';
            let value = item.value;
            if (obj) {
                if (obj.category && ['User', 'Application'].includes(obj.category)) {
                    if (!value.startsWith('*')) {
                        value = `*${value}`;
                    }
                    if (!value.endsWith('*')) {
                        value = `${value}*`;
                    }
                }
                if (obj.key === 'result') {
                    value = value.toLowerCase();
                }       
                params[`${prefix}.${obj.key}`] = value;
            }        
        });
        Object.assign(this.cEvalAppsList.params, params);

        this._vState.searchFilterValue = filter;
        this.fetchEvaluationAppsList();
    }

    handleDelete = (model) => {
        f._confirm.show({
          title: `Delete Report`,
          children: <div>Are you sure you want to delete report ?</div>,
          btnCancelText: 'Cancel',
          btnOkText: 'Delete',
          btnOkColor: 'secondary',
          btnOkVariant: 'text'
        })
        .then((confirm) => {
          this.props.evaluationStore.deleteAppTarget(model.id,{
            models: this.cEvalAppsList
          })
          .then(() => {
              confirm.hide();
              f.notifySuccess('Report Deleted');
              this.fetchEvaluationAppsList();
          }, f.handleError(null, null, {confirm}));
        }, () => {});
      }

    handleEdit = (model) => {
        console.log(model);
    };

    handleAddNew = () => {
        if (this.modalRef.current) {
            this.modalRef.current.show({
              title: 'Add Configuration',
              btnOkText: 'Confirm',
              btnCancelText: 'Cancel',
        })
    }
    }
    resolveForm = () => {
        console.log('hetr')
    }
    render() {
        const {_vState } = this;
        

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
                            <Grid item xs={6} sm={6} md={6} lg={6}>
                            <AddButton
                                data-track-id="add-new-eval"
                                colAttr={{
                                    xs: 12,
                                    sm: 12,
                                    md: 12
                                }}
                                label="New Configuration"
                                onClick={this.handleAddNew}
                            />
                            </Grid>
                        </Grid>
                        <VEvaluationAppsTable
                            data={this.cEvalAppsList}
                            pageChange={this.handlePageChange}
                            _vState={_vState}
                            applicationKeyMap={this.applicationKeyMap}
                            handleDelete={this.handleDelete}
                            handleEdit={this.handleEdit}
                        />
                        <FSModal ref={this.modalRef} dataResolve={this.resolveForm}>
                            <VEvalTargetForm form={this.form} />
                        </FSModal>
                    </>
        );
    }
}

CEvaluationAppsList.defaultProps = {
    vName: 'evaluationAppsList'
}

export default CEvaluationAppsList;