import BaseStore from './base_store';
import MPublicData from '../models/m_public';
import {FEATURE_PROPERTIES_MAPPING} from 'utils/globals';

class PublicStore extends BaseStore {
	constructor() {
        super({
            type: 'Public',
            baseUrl: 'account-service/public/api'
        });
    }

    modifyResponse(resp=[]) {
        return resp.map((item, i) => ({
            id: i,
            name: FEATURE_PROPERTIES_MAPPING[item.feature] || item.feature,
            value: ''+(item.status == 1)
        }));
    }

    getFeatureFlags(opts = {}) {
        opts.path = 'feature';
        opts.recordMapper = (json) => new MPublicData(json);
        opts.deserialize = (resp) => {
            return this.modifyResponse(resp);
        }
        return this.fetchAll('', opts);
    }
}

const publicStore = new PublicStore();
export default publicStore;