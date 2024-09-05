import BaseStore from './base_store';

class GeneralStore extends BaseStore {
	constructor() {
        super({
            type: 'General',
            baseUrl: 'api/general'
        });
    }

    getAllProperties(opts = {}) {
        opts.path = 'properties';
        opts.recordMapper = (json) => new Object(json);
        opts.deserialize = (resp) => {
            resp.forEach((res, i) => res.id = i);
            return resp;
        }
        return this.fetchAll('', opts);
    }
}

const generalStore = new GeneralStore();
export default generalStore;