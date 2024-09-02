import BaseStore from './base_store';
import MGroup from 'data/models/m_group';

class GroupStore extends BaseStore {
    constructor() {
        super({
            type: 'user',
            baseUrl: 'account-service/api/groups',
        });
    }

    searchGroups(opts = {}) {
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new MGroup(json);
        return this.fetchAll(null, opts);
    }

    createGroup(data , opts = {}) {
        opts.recordMapper = (json) => new MGroup(json);
        opts.transformPayload = (data) => {
            data.id = undefined;
            return data
        }
        return this.create(data, opts);
    }

    updateGroupUsers(data, opts = {}) {
        opts.recordMapper = (json) => new MGroup(json);
        const id = data.id;
        opts.path = `/${id}/users`;
        opts.transformPayload = (data) => {
            const existing = this.get(id);
            return Object.assign({}, existing, data);
        }
        return this.update('', data, opts);
    }

    updateGroupForm(data, opts = {}) {
        opts.recordMapper = (json) => new MGroup(json);
        const id = data.id;
        opts.transformPayload = (data) => {
            const existing = this.get(id);
            return Object.assign({}, existing, data);
        }
        return this.update(id, data, opts);
    }

    deleteGroup(id, opts = {}) {
        return this.delete(id, opts);
    }
}

const groupStore = new GroupStore();
export default groupStore;