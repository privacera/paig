import {observable} from 'mobx';

import FSBaseModel from 'common-ui/data/models/base_model';

class EncryptDecrypt extends FSBaseModel {
    @observable encryptionKeyId;
    @observable encryptedData;
    @observable decryptedData;

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }
}

export default EncryptDecrypt;