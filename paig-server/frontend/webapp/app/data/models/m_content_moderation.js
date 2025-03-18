import { observable } from 'mobx';
import FSBaseModel from 'common-ui/data/models/base_model';

class ContentModeration extends FSBaseModel {
    @observable customReply = false;
    @observable filterSelected = false;
    @observable filterStrengthPrompt;
    @observable filterStrengthResponse;

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }
}

export default ContentModeration;