import BaseStore from './base_store';
import VEncryptDecrypt from '../models/m_encrypt_decrypt';

class EncryptDecryptStore extends BaseStore {
	constructor() {
        super({
            type: 'Encrypt Decrypt',
            baseUrl: 'account-service/api'
        });
    }
    decrypt(data, opts = {}) {
        opts.path = 'data-protect/decrypt';
        opts.recordMapper = (json) => new VEncryptDecrypt(json);
        return this.create(data, opts);
    }
}

const encryptDecryptStore = new EncryptDecryptStore();
export default encryptDecryptStore;