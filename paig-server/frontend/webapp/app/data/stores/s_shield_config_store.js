import BaseStore from './base_store';
import MShieldConfig from '../models/m_shield_config';

class ShieldConfigStore extends BaseStore {
	constructor() {
        super({
            type: 'Shield Config',
            baseUrl: 'governance-service/api/shield/'
        });
    }

    getConfigUrl(opts = {}) {
        opts.path = 'configs/get';
        opts.recordMapper = (json) => new MShieldConfig(json);
        opts.deserialize = (resp) => {
            return resp;
        }
        return this.fetch('', opts);
    }

    saveConfigUrl( opts = {}) {
        opts.path = 'configs/save';
        opts.recordMapper = (json) => new MShieldConfig(json);
        return this.update(null, null, opts);
    }
}

const shieldConfigStore = new ShieldConfigStore();
export default shieldConfigStore;