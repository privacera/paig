import {observable} from 'mobx';
import FSBaseModel from './base_model';

class Property extends FSBaseModel {
    @observable name="";
    @observable value="";
    @observable objectId;
    @observable objectClassType;
    @observable status;
    @observable disabled;

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }

    toJSON() {
        return {
            id: this.id || undefined,
            name: this.name,
            value: this.value,
            objectId: this.objectId,
            objectClassType: this.objectClassType,
            status: this.status,
            disabled: this.disabled
        }
    }
}

export default Property;