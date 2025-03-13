import React, {Component} from 'react';
import {observer, inject} from 'mobx-react';
import {observable} from 'mobx'

import FSModal from 'common-ui/lib/fs_modal';
import f from 'common-ui/utils/f';
import { Loader, getSkeleton } from 'common-ui/components/generic_components'
import {GuardrailFormUtil, initialData} from 'components/guardrail/forms/guardrail_form_util';
import VReview from 'components/guardrail/forms/v_review';
import {getStepsForProvider} from 'components/guardrail/forms/v_guardrail_stepper';

@inject('guardrailStore')
@observer
class CGuardrailReview extends Component {
    @observable _vState = {
        loading: true
    }
    constructor(props) {
        super(props);

        this.formUtil = new GuardrailFormUtil(initialData);
    }
    showModal = (model) => {
        this.Modal?.show({
            title: 'Guardrail Preview',
            showOkButton: false
        });
        if (model) {
            this.fetchGuardrail(model.id);
        }
    }
    fetchGuardrail = async(id) => {
        try {
            this.formUtil.resetData(initialData);
            this._vState.loading = true;
            const guardrail = await this.props.guardrailStore.getGuardrail(id);
            guardrail.guardrailConfigs?.forEach(c => {
                c.status = 1;
            })
            this.formUtil.setData(guardrail);

            let stepper = getStepsForProvider(this.formUtil.getProvider());
            this.formUtil.setSteps(stepper);

            this._vState.loading = false;
        } catch(e) {
            this._vState.loading = false;
            f.handleError()(e);
        }
    }
    render() {
        return (
            <FSModal ref={ref => this.Modal = ref} maxWidth="md" bodyProps={{
                    className: 'background-color'
                }}>
                <Loader isLoading={this._vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
                    <VReview formUtil={this.formUtil} />
                </Loader>
            </FSModal>
        );
    }
}

export default CGuardrailReview
