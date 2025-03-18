import React, {Component, Fragment} from 'react';
import {inject, observer} from 'mobx-react';
import {observable} from 'mobx';

import {Grid, Typography} from '@material-ui/core';

import {Select2} from 'common-ui/components/generic_components';
import f from 'common-ui/utils/f';
import {FormHorizontal, FormGroupSelect2} from 'common-ui/components/form_fields';

@inject('guardrailResponseTemplateStore')
@observer
class Response extends Component {
    @observable _vState = {
        responseTemplate: ''
    }
    constructor(props) {
        super(props);

        this._vState.responseTemplate = this.props.value || '';

        this.cResponseTemplate = f.initCollection();
        this.cResponseTemplate.params = {
            size: 9999
        }
    }
    componentDidMount() {
        this.fetchResponseTemplate();
    }
    fetchResponseTemplate = () => {
        f.beforeCollectionFetch(this.cResponseTemplate);
        this.props.guardrailResponseTemplateStore.searchResponseTemplate({
            params: this.cResponseTemplate.params
        }).then(res => {
            if (res.models.length && !this._vState.responseTemplate) {
                this.handleOnChange(res.models[0].response);
            }
            f.handleSuccess(this.cResponseTemplate)(res);
        }, f.handleError(this.cResponseTemplate));
    }
    handleOnChange = (val) => {
        const {config} = this.props;
        this._vState.responseTemplate = val;

        if (config) {
            config.responseMessage = val;
        }
        this.props.onChange?.(val);
    }
    render() {
        return (
            <Fragment>
                <FormHorizontal spacing={1} className="m-b-md" style={{}}>
                    <Grid item xs={12}>
                        <Typography variant="subtitle1">
                            Response
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                            A default response is selected for this guardrail, triggered when the guardrail is activated. You can choose a different response or add a custom response on the Template page.
                        </Typography>
                    </Grid>

                    <FormGroupSelect2
                        value={this._vState.responseTemplate}
                        data={f.models(this.cResponseTemplate)}
                        placeholder="Select Response Template"
                        disableClearable={true}
                        onChange={this.handleOnChange}
                        multiple={false}
                        labelKey="response"
                        valueKey="response"
                        data-testid="response-template"
                    />
                </FormHorizontal>
            </Fragment>
        )
    }
}

export default Response;