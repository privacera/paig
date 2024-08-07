import {observable} from 'mobx';
import FSBaseModel from 'common-ui/data/models/base_model';

class User extends FSBaseModel {
	@observable firstName;
    @observable lastName;
    @observable email;

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }

    get fullName() {
        return `${this.firstName} ${this.lastName}`
    }
}

export default User;