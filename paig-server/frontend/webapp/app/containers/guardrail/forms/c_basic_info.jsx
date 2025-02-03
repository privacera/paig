import React, {Component} from 'react';
import {observer, inject} from 'mobx-react';
import {observable, action} from 'mobx';

import {Grid, Typography, Box, Paper, Switch, Chip} from '@material-ui/core';
import {Alert} from '@material-ui/lab';

import f from 'common-ui/utils/f';
import history from 'common-ui/routers/history'
import {FormHorizontal, FormGroupInput, FormGroupSelect2} from 'common-ui/components/form_fields';
import {GUARDRAIL_PROVIDER} from 'utils/globals';

@inject('guardrailConnectionProviderStore')
@observer
class CBasicInfo extends Component {
    @observable _vState = {
        name: '',
        description: '',
        guardrailProvider: '',
        connectionName: '',
        providers: [GUARDRAIL_PROVIDER.PAIG]
    }
    constructor(props) {
        super(props);

        const data = this.props.formUtil.getData() || {};

        Object.assign(this._vState, {
            name: data.name,
            description: data.description,
        });

        if (data.guardrailProvider) {
            this._vState.guardrailProvider = data.guardrailProvider;
        }
        if (data.guardrailConnectionName) {
            this._vState.connectionName = data.guardrailConnectionName;
        }
    }
    componentDidMount() {
         this.props.guardrailConnectionProviderStore.getConnectedGuardrailProvider()
        .then((res) => {
            let providers = Object.values(GUARDRAIL_PROVIDER).reduce((acc, provider) => {
                acc[provider.NAME] = provider;
                return acc;
            }, {});

            res.raw.raw?.reduce((acc, p) => {
                if (providers[p]) {
                    this._vState.providers.push(providers[p]);
                }
                return acc;
            }, []);
        }, f.handleError());
    }
    handleChange = (key, value) => {
        this._vState[key] = value;
        this.props.formUtil.setData({[key]: value});
        this.props.formUtil.validateField(key, value, 'basicInfo');
    }
    handleProviderEnable = (status, provider) => {
        if (this._vState.guardrailProvider && status) {
            f.notifyInfo('Only one Guardrail Provider can be enabled at a time');
            return;
        }
        if (status) {
            this._vState.guardrailProvider = provider.NAME;
        } else {
            this._vState.guardrailProvider = '';
            this._vState.connectionName = '';
        }

        this.props.formUtil.setData({guardrailProvider: this._vState.guardrailProvider, guardrailConnectionName: ''});

        this.props.handleProviderChange?.(this._vState.guardrailProvider);
    }
    handleAccountChange = (val, provider) => {
        this._vState.connectionName = val;
        this.props.formUtil.setData({guardrailConnectionName: val});
    }
    handleGuardrailConnection = () => {
        history.push('/guardrail_connection_provider');
    }
    render() {
        const error = this.props.formUtil.getErrors();

        let nonDefaultProviders = this._vState.providers.filter(p => !p.DEFAULT);

        return (
            <Box component={Paper} p="15px">
                <FormHorizontal style={{}} data-testid="basic-form">
                    <Grid item xs={12}>
                        <Typography data-testid="basic-form-title">
                            Enter Guardrail Details
                        </Typography>
                    </Grid>
                    <FormGroupInput
                        required={true}
                        value={this._vState.name}
                        label="Name"
                        placeholder="Enter guardrail name"
                        onChange={({target}) => this.handleChange('name', target.value)}
                        errMsg={error.basicInfo?.name}
                        data-testid="name"
                    />
                    <FormGroupInput
                        as="textarea"
                        value={this._vState.description}
                        label="Description"
                        placeholder="Enter guardrail description"
                        rows={1}
                        rowsMax={5}
                        onChange={({target}) => this.handleChange('description', target.value)}
                        errMsg={error.basicInfo?.description}
                        data-testid="description"
                    />
                </FormHorizontal>
                <FormHorizontal className="m-b-sm" style={{}}>
                    <Grid item xs={12}>
                        <Typography variant="subtitle1" data-testid="default-guardrail-title">
                            Default Guardrails
                        </Typography>
                    </Grid>
                </FormHorizontal>
                <FormHorizontal className="m-b-sm" style={{}} data-testid="default-guardrail">
                    {
                        this._vState.providers.filter(p => p.DEFAULT).map((provider, i) => {
                            return (
                                <DefaultProvider
                                    key={i}
                                    provider={provider}
                                />
                            )
                        })
                    }
                </FormHorizontal>
                <FormHorizontal className="m-b-sm" style={{}}>
                    <Grid item xs={12}>
                        <Typography variant="subtitle1">Select an Optional Guardrail Provider {/* (Single Choice Only) */}</Typography>
                    </Grid>
                </FormHorizontal>
                <FormHorizontal className="m-b-sm" style={{}}>
                    {
                        error.basicInfo?.guardrailConnections &&
                        <Grid item xs={12}>
                            <Alert severity="error">
                                {error.basicInfo.guardrailConnections}
                            </Alert>
                        </Grid>
                    }
                    {
                        nonDefaultProviders.length === 0
                        ?
                            (
                                <Grid item xs={12} className="text-center">
                                    <Typography variant="body2">
                                        You don't have any connected accounts yet. Add an account in <a onClick={this.handleGuardrailConnection}>Guardrails Connections</a> page.
                                    </Typography>
                                </Grid>
                            )
                        :
                            nonDefaultProviders.map((provider, i) => {
                                return (
                                    <GuardrailProvider
                                        key={i}
                                        _vState={this._vState}
                                        provider={provider}
                                        formUtil={this.props.formUtil}
                                        handleProviderEnable={this.handleProviderEnable}
                                        handleAccountChange={this.handleAccountChange}
                                    />
                                )
                            })
                    }
                </FormHorizontal>
            </Box>
        )
    }
}

const DefaultProvider = ({provider}) => {
    return (
        <Grid item xs={12} md={6} className="border-radius-5 card-border grey-bg m-l-sm m-r-sm" data-testid={provider.NAME}>
            <Box>
                <Grid container justify="space-between" data-testid="default-guardrail-info">
                    <Grid item>
                        <Grid container>
                            {
                                provider.IMG_URL &&
                                <Grid item className="m-r-sm">
                                    <div style={{
                                             width: '40px',
                                             height: '40px',
                                             backgroundColor: '#eaf3fa',
                                             display: 'flex',
                                             justifyContent: 'center',
                                             alignItems: 'center'
                                        }}>
                                        <img
                                            className={"services-logo " + provider.NAME}
                                            src={provider.IMG_URL}
                                            alt="service-logo"
                                            style={{
                                                width: 'auto',
                                                height: '30px'
                                            }}
                                        />
                                    </div>
                                </Grid>
                            }
                            <Grid item>
                                <Typography variant="subtitle2">{provider.LABEL}</Typography>
                                <Typography variant="caption" color="textSecondary">
                                    Default
                                </Typography>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item>
                        <Chip
                            size="small"
                            label="Always Enabled"
                        />
                    </Grid>
                </Grid>
            </Box>
            <Box className="m-t-sm">
                <Typography variant="body2">{provider.DESCRIPTION || '--'}</Typography>
            </Box>
        </Grid>
    )
}

@inject('guardrailConnectionProviderStore')
@observer
class GuardrailProvider extends Component {
    constructor(props) {
        super(props);

        const {provider} = this.props;

        this.cProviderConnections = f.initCollection();
        this.cProviderConnections.params = {
            size: 9999,
            guardrailsProvider: provider.NAME
        }
    }
    componentDidMount() {
        if (!this.props.provider.DEFAULT) {
            this.fetchGuardrailConnections();
        }
    }
    handleAccountChange = (val) => {
        this.props.handleAccountChange?.(val, this.props.provider);
    }
    fetchGuardrailConnections = () => {
        f.beforeCollectionFetch(this.cProviderConnections);
        this.props.guardrailConnectionProviderStore.searchGuardrailConnectionProvider({
            params: this.cProviderConnections.params
        })
        .then(f.handleSuccess(this.cProviderConnections), f.handleError(this.cProviderConnections));
    }
    handleProviderEnable = (checked, provider) => {
        this.props.handleProviderEnable(checked, provider)
    }
    render() {
        const {_vState, provider} = this.props;
        return (
            <Grid item xs={12} md={6} className="border-radius-5 card-border-grey m-l-sm m-r-sm" data-testid={provider.NAME}>
                <Box>
                    <Grid container justify="space-between">
                        <Grid item>
                            <Grid container>
                                {
                                    provider.IMG_URL &&
                                    <Grid item className="m-r-sm">
                                        <div style={{
                                             width: '40px',
                                             height: '40px',
                                             backgroundColor: '#eaf3fa',
                                             display: 'flex',
                                             justifyContent: 'center',
                                             alignItems: 'center'
                                        }}>
                                        <img
                                            className={"services-logo " + provider.NAME}
                                            src={provider.IMG_URL}
                                            alt="service-logo"
                                            style={{
                                                width: 'auto',
                                                height: '30px'
                                            }}
                                        />
                                    </div>
                                    </Grid>
                                }
                                <Grid item>
                                    <Typography component="span" variant="subtitle2">{provider.LABEL}</Typography>
                                    <Typography component="div" variant="caption" color="textSecondary">
                                        Configured
                                    </Typography>
                                </Grid>
                            </Grid>
                        </Grid>
                        <Grid item>
                            <Switch
                                data-track-id={`${provider.LABEL.toLowerCase()}-guardrail-provider-switch`}
                                data-testid="guardrail-provider-switch"
                                checked={_vState.guardrailProvider === provider.NAME}
                                onChange={({target}) => this.handleProviderEnable(+target.checked, provider)}
                                className="pull-right"
                                disabled={!provider.EDITABLE}
                                color="primary"
                            />
                        </Grid>
                    </Grid>
                </Box>
                <Box className="m-t-sm m-b-sm">
                    <Typography variant="body2">{provider.DESCRIPTION || '--'}</Typography>
                </Box>
                <FormGroupSelect2
                    data={f.models(this.cProviderConnections)}
                    showLabel={false}
                    disableClearable={true}
                    disabled={_vState.guardrailProvider !== provider.NAME}
                    placeholder="Select connection"
                    labelKey="name"
                    valueKey="name"
                    value={_vState.connectionName}
                    onChange={val => this.handleAccountChange(val)}
                    data-testid={provider.NAME + '-connected-accounts'}
                />
            </Grid>
        )
    }
}

export default CBasicInfo;