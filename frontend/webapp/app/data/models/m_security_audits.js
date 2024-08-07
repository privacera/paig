import {observable} from 'mobx';
import FSBaseModel from 'common-ui/data/models/base_model';

class SecurityAudits extends FSBaseModel {
    @observable showText = false;
    @observable askConfirmation = true;
    constructor(props = {}, opts = {}) {
        super(props, opts);

        if (props.result === 'allowed') {
            props.isAllowed = true;
        } else if (props.result === 'masked') {
            props.isMasked = true;
        }

        Object.assign(this, props);
    }
}

export default SecurityAudits;