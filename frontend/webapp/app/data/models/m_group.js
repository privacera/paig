import {observable} from 'mobx';
import FSBaseModel from 'common-ui/data/models/base_model';

class Group extends FSBaseModel {
	@observable name;
    @observable description;

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }
}

export default Group;