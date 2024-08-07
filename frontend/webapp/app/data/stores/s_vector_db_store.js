import BaseStore from './base_store';
import MVectorDB from '../models/m_vector_db';

class VectorDBStore extends BaseStore {
    constructor() {
        let baseUrl = 'governance-service/api/ai/vectordb';
        super({
            type: 'vector_db',
            baseUrl
        });
        this.baseUrl = baseUrl;
    }
    getVectorDBById(id, opts = {}) {
        opts.recordMapper = (json) => new MVectorDB(json);
        return this.fetch(id, opts);
    }
    getVectorDBs(opts = {}) {
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new MVectorDB(json);
        return this.fetchAll('', opts);
    }
    createVectorDB(data, opts = {}) {
        opts.recordMapper = (json) => new MVectorDB(json);
        return this.create(data, opts);
    }
    updateVectorDB(data, opts = {}) {
        opts.recordMapper = (json) => new MVectorDB(json);
        return this.update(data.id, data, opts);
    }
    deleteVectorDB(id, opts = {}) {
        opts.recordMapper = (json) => new MVectorDB(json);
        return this.delete(id, opts);
    }
}

const vectorDBStore = new VectorDBStore();
export default vectorDBStore;