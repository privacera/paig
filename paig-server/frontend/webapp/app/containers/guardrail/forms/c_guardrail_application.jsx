import React, {Component, Fragment} from 'react';
import {observer, inject} from 'mobx-react';
import {observable, extendObservable} from 'mobx';

import {Typography, Grid, Box, Paper} from '@material-ui/core';

import f from 'common-ui/utils/f';
import {VApplications} from 'components/guardrail/forms/v_guardrail_application';
import {ErrorLogo} from 'components/site/v_error_page_component';

@inject('aiApplicationStore')
@observer
class CGuardrailApplication extends Component {
    constructor(props) {
        super(props);

        this.cApplications = f.initCollection();
        this.cApplications.params = {
            size: 9999
        }
    }
    componentDidMount() {
        this.fetchApplications();
    }
    fetchApplications = async() => {
        f.beforeCollectionFetch(this.cApplications)

        try {
            const res = await this.props.aiApplicationStore.getAIApplications({
                params: this.cApplications.params
            });

            let applicationKeys = this.props.formUtil.getData().applicationKeys || [];

            let models = res.models.filter(app => {
                if (applicationKeys.includes(app.applicationKey)) {
                    extendObservable(app, {
                        selected: true
                    })
                }
                return !app.default;
            });

            f.resetCollection(this.cApplications, models);
        } catch(e) {
            f.handleError(this.cApplications)(e);
        }
    }
    handleAccountSelection = (model) => {
        let data = this.props.formUtil.getData();
        data.applicationKeys = f.models(this.cApplications).filter(m => m.selected).map(app => app.applicationKey);
    }
    render() {
        let models = []; f.models(this.cApplications);

        return (
            <Box component={Paper} elevation={0} p="15px" data-testid="ai-application-step">
                {
                    models.length > 0
                    ?
                        (
                            <Fragment>
                                <Grid container spacing={3} className="m-b-sm">
                                    <Grid item xs={12} data-testid="ai-application-header">
                                        <Typography variant="h6">Select AI Application</Typography>
                                    </Grid>
                                </Grid>
                                <VApplications
                                    data={this.cApplications}
                                    handleAccountSelection={this.handleAccountSelection}
                                />
                            </Fragment>
                        )
                    :
                        (
                            <Grid container spacing={2} className="align-items-center m-t-md justify-center">
                                <Grid item>
                                    <ErrorLogo errorCode="" imageProps={{width: 'auto', height: '100px'}} />
                                </Grid>
                                <Grid item xs={12} sm={7}>
                                    <Typography variant="h6" data-testid="no-ai-app-connected">No AI Application Connected</Typography>
                                    <Typography variant="body2" data-testid="no-ai-app-desc">
                                        Currently, no AI applications are connected. You may save the guardrail now and return to this step later to connect applications.
                                    </Typography>
                                </Grid>
                            </Grid>
                        )
                }
            </Box>
        )
    }
}

export default CGuardrailApplication;