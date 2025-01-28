import React, {Component, Fragment} from 'react';
import {inject, observer} from 'mobx-react';
import {observable} from 'mobx';

import {Grid, Typography, Button, Box, Paper} from '@material-ui/core';
import Alert from '@material-ui/lab/Alert';

import f from 'common-ui/utils/f';
import {FormHorizontal, FormGroupInput} from 'common-ui/components/form_fields';

@inject('shieldStore')
@observer
class CTestGuardrail extends Component {
    @observable _vState = {
        testText: '',
        testTextResult: '',
        loading: false
    }
    handleTestTextChange = (e) => {
        this._vState.testText = e.target.value;
    }
    handleTest = async() => {
        this._vState.loading = true;

        let d = this.props.formUtil.getData();

        let data = {
            guardrailId: d.id,
            message: this._vState.testText
        }

        try {
            let resp = await this.props.shieldStore.testGuardrail(data);
            this._vState.testTextResult = resp;
            this._vState.loading = false;
        } catch(e) {
            f.handleError()(e);
            this._vState.loading = false;
        }
    }
    render() {
        let data = this.props.formUtil.getData();
        let isDataChanged = this.props.formUtil.isDataChanged();

        return (
            <Box component={Paper} p="15px">
                <FormHorizontal spacing={1} style={{}}>
                    <Grid item xs={12}>
                        <Typography variant="h6" data-testid="header">
                            Test Guardrails
                        </Typography>
                    </Grid>
                    {
                        !data.id &&
                        <Grid item xs={12}>
                            <Alert severity="warning" data-testid="save-guardrail-alert">
                                Please save the guardrail on review step to test it.
                            </Alert>
                        </Grid>
                    }
                    {
                        data.id && isDataChanged &&
                        <Grid item xs={12}>
                            <Alert severity="warning" data-testid="save-guardrail-change-alert">
                                Please save the guardrail on review step to test the changes.
                            </Alert>
                        </Grid>
                    }
                    <FormGroupInput
                        showLabel={false}
                        as="textarea"
                        value={this._vState.testText}
                        disabled={!data.id}
                        inputProps={{'data-testid': 'test-text'}}
                        onChange={this.handleTestTextChange}
                    />
                    <Grid item xs={12}>
                        <Button
                            variant="contained"
                            color="primary"
                            disabled={!this._vState.testText.trim() || this._vState.loading}
                            onClick={this.handleTest}
                            data-testid="test-guardrail"
                        >
                            TEST INPUT
                        </Button>
                    </Grid>
                    {
                        this._vState.testTextResult &&
                        <Grid item xs={12} className="m-t-sm" data-testid="test-output">
                            <pre>
                                <div>
                                    <Typography variant="body1" className="m-b-md">Output:</Typography>
                                </div>
                                {
                                    ['deny', 'redact'].includes(this._vState.testTextResult?.action?.toLowerCase()) &&
                                    <Typography variant="inherit" component={Box} fontWeight="fontWeightBold" fontSize="14px">
                                        Action: <span className={this._vState.testTextResult?.action?.toLowerCase() === 'deny' ? 'text-danger' : 'text-warning' }>
                                                {this._vState.testTextResult.action}
                                            </span>
                                    </Typography>
                                }
                                <div className="m-t-xs">
                                    <Typography className="body2">
                                        {this._vState.testTextResult?.message}
                                    </Typography>
                                </div>
                            </pre>
                        </Grid>
                    }
                </FormHorizontal>
            </Box>
        )
    }
}

export default CTestGuardrail;