import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import {observable} from 'mobx';

import {Box, Paper} from '@material-ui/core';

import BaseContainer from 'containers/base_container';
import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import {VGuardrailInfo, Filters, VGuardrailListing} from 'components/guardrail/v_guardrail_listing';
import CGuardrailReview from 'containers/guardrail/forms/c_guardrail_review';

@inject('guardrailStore', 'aiApplicationStore')
class CGuardrailListing extends Component {
    @observable _vState = {
        searchValue: '',
        providers: '',
        applications: ''
    }
    constructor(props) {
        super(props);

        this.cGuardrailListing = f.initCollection();
        this.cGuardrailListing.params = {
            size: DEFAULTS.DEFAULT_PAGE_SIZE,
        }

        this.cApplications = f.initCollection();
        this.cApplications.params = {
            size: 100
        }

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.GUARDRAILS.PROPERTY);
    }
    componentDidMount() {
        this.handleRefresh();
    }
    handleRefresh = () => {
        //this.fetchApplications();
        this.fetchGuardrailListing();
    }
    fetchApplications = async() => {
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
    fetchGuardrailListing = () => {
        f.beforeCollectionFetch(this.cGuardrailListing);
        this.props.guardrailStore.searchGuardrail({
            params: this.cGuardrailListing.params
        }).then(f.handleSuccess(this.cGuardrailListing), f.handleError(this.cGuardrailListing));
    }
    handleDelete = (model) => {
        f._confirm.show({
            title: 'Confirm Delete',
            children: <Fragment>Are you sure you want to delete <b>{model.name}</b> guardrail?</Fragment>,
            btnCancelText: 'Cancel',
            btnOkText: 'Delete',
            btnOkColor: 'secondary',
            btnOkVariant: 'text'
        }).then((confirm) => {
            this.props.guardrailStore.deleteGuardrail(model.id, {
                models: this.cGuardrailListing
            }).then(() => {
                f.notifySuccess(`The Guardrail ${model.name} deleted successfully`);
                confirm.hide();
                f.handlePagination(this.cGuardrailListing, this.cGuardrailListing.params);
                this.handleRefresh();
            }, f.handleError());
        }, () => {});
    }
    handlePageChange = () => {
        this.handleRefresh();
    };
    handleOnChange = (e, val) => {
        this._vState.searchValue = val;
        this.cGuardrailListing.params.name = val || undefined;
    }
    handleSearch = () => {
        delete this.cGuardrailListing.params.page;
        this.fetchGuardrailListing();
    }
    handleGuardrailProviderChange = (val) => {
        this._vState.providers = val;
        Object.assign(this.cGuardrailListing.params, {
            page: 0,
            guardrailProvider: val || undefined
        })
        this.fetchGuardrailListing();
    }
    handleApplicationChange = async(val) => {
        this._vState.applications = val;
        Object.assign(this.cGuardrailListing.params, {
            page: 0,
            //application: val || undefined
        })
        this.fetchGuardrailListing();
    }
    handleCreate = () => {
        this.props.history.push('/guardrails/create');
    }
    handleEdit = (model) => {
        this.props.history.push('/guardrails/edit/' + model.id);
    }
    handlePreview = (model) => {
        this.reviewModal?.showModal(model);
    }
    render() {
        return (
            <BaseContainer
                handleRefresh={this.handleRefresh}
            >
                <VGuardrailInfo />
                <Box component={Paper} p={2} className="m-t-sm">
                    <Filters
                        _vState={this._vState}
                        handleOnChange={this.handleOnChange}
                        handleSearch={this.handleSearch}
                        permission={this.permission}
                        data={this.cGuardrailListing}
                        handleCreate={this.handleCreate}
                        cApplications={this.cApplications}
                        handleGuardrailProviderChange={this.handleGuardrailProviderChange}
                        handleApplicationChange={this.handleApplicationChange}
                    />
                    <VGuardrailListing
                        permission={this.permission}
                        data={this.cGuardrailListing}
                        handlePageChange={this.fetchGuardrailListing}
                        handleEdit={this.handleEdit}
                        handleDelete={this.handleDelete}
                        handlePreview={this.handlePreview}
                    />
                    <CGuardrailReview ref={ref => this.reviewModal = ref} />
                </Box>
            </BaseContainer>
        )
    }
}

export default CGuardrailListing;