import React, {Component} from 'react';
import {inject} from 'mobx-react';
import {observable} from 'mobx';

import BaseContainer from 'containers/base_container';
import f from 'common-ui/utils/f';
import {ConnectedProvider, AvailableProviders} from 'components/guardrail/v_guardrail_connection_provider';
import CGuardrailProviderForm from 'containers/guardrail/c_guardrail_provider_form';

@inject('guardrailConnectionProviderStore')
class CGuardrailConnectionProvider extends Component {
    @observable _vState = {
        connectedProvider: []
    }
    constructor(props) {
        super(props);
    }
    componentDidMount() {
        this.handleRefresh();
    }
    handleRefresh = () => {
        this.getConnectedProviders();
    }
    getConnectedProviders = () => {
        this.props.guardrailConnectionProviderStore.getConnectedGuardrailProvider()
        .then((res) => {
            this._vState.connectedProvider = res.raw.raw;
        }, f.handleError());
    }
    handleConnectedProviderClick = (provider) => {
        this.props.history.push('/guardrail_connection_provider/' + provider.NAME);
    }
    handleProviderClick = (provider) => {
        this.Modal?.handleCreate?.(provider);
    }
    render() {
        return (
            <BaseContainer
                handleRefresh={this.handleRefresh}
            >
                <ConnectedProvider
                    _vState={this._vState}
                    handleConnectedProviderClick={this.handleConnectedProviderClick}
                />
                <AvailableProviders
                    _vState={this._vState}
                    handleProviderClick={this.handleProviderClick}
                />
                <CGuardrailProviderForm
                    ref={ref => this.Modal = ref}
                    handlePostSave={this.handleRefresh}
                />
            </BaseContainer>
        )
    }
}

export default CGuardrailConnectionProvider;