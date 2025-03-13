import React, {Component} from 'react';
import {inject} from 'mobx-react';

import {Box, Paper, Typography, Grid} from '@material-ui/core';
import {observable} from 'mobx';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import BaseContainer from 'containers/base_container';
import {FEATURE_PERMISSIONS, GUARDRAIL_PROVIDER} from 'utils/globals';
import {VConnectedGuardrail} from 'components/guardrail/v_guardrail_provider_connected_list';
import CGuardrailProviderForm from 'containers/guardrail/c_guardrail_provider_form';

@inject('guardrailConnectionProviderStore')
class CGuardrailProviderConnectedList extends Component {
    @observable _vState = {
        provider: null
    }
    constructor(props) {
        super(props);

        let provider = Object.values(GUARDRAIL_PROVIDER).find(provider => {
            return provider.NAME === this.props.match.params.provider;
        });

        this._vState.provider = provider;

        this.cGuardrailProviderConnectedList = f.initCollection();
        this.cGuardrailProviderConnectedList.params = {
            size: DEFAULTS.DEFAULT_PAGE_SIZE,
            guardrailsProvider: this.props.match.params.provider || ''
        }

        this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.GUARDRAILS.PROPERTY);
    }
    componentDidMount() {
        this.handleRefresh();
    }
    fetchGuardrailProviderConnectedList = () => {
        f.beforeCollectionFetch(this.cGuardrailProviderConnectedList);
        this.props.guardrailConnectionProviderStore.searchGuardrailConnectionProvider({
            params: this.cGuardrailProviderConnectedList.params
        })
        .then(f.handleSuccess(this.cGuardrailProviderConnectedList), f.handleError(this.cGuardrailProviderConnectedList));
    }
    handlePageChange = () => {
        this.fetchGuardrailProviderConnectedList();
    }
    handleRefresh = () => {
        this.fetchGuardrailProviderConnectedList();
    }
    handleEdit = (model) => {
        this.Modal?.handleEdit?.(model);
    }
    handleDelete = (model) => {
        this.Modal?.handleDelete?.(model, this.cGuardrailProviderConnectedList);
    }

    render() {
        return (
            <BaseContainer
                handleRefresh={this.handleRefresh}
                showBackButton={true}
            >
                <Box component={Paper} p={2}>
                    {
                        this._vState.provider &&
                        <Grid container spacing={3} className="m-b-sm">
                            <Grid item xs={12} sm={8}>
                                <Typography variant="h6" data-testid="connection-header">
                                    {this._vState.provider.LABEL}
                                </Typography>
                            </Grid>
                            <AddButtonWithPermission
                                colAttr={{
                                    xs: 12,
                                    sm: 4
                                }}
                                permission={this.permission}
                                label="ADD CONNECTION"
                                onClick={() => this.Modal?.handleCreate?.(this._vState.provider)}
                                data-testid="add-connection-btn"
                            />
                        </Grid>
                    }
                    <VConnectedGuardrail
                        permission={this.permission}
                        data={this.cGuardrailProviderConnectedList}
                        handlePageChange={this.handlePageChange}
                        handleEdit={this.handleEdit}
                        handleDelete={this.handleDelete}
                    />
                    <CGuardrailProviderForm
                        ref={ref => this.Modal = ref}
                        handlePostSave={this.handleRefresh}
                        handlePostDelete={this.handleRefresh}
                    />
                </Box>
            </BaseContainer>
        )
    }
}

export default CGuardrailProviderConnectedList;