import BaseStore from './base_store';
import VUser from 'data/models/m_user';
import VCurrentUser from 'data/models/m_current_user';

class UserStore extends BaseStore {
    constructor() {
        super({
            type: 'user',
            baseUrl: 'account-service/api/users',
        });
    }

    getLoggedInUser(opts={}) {
        opts.path = 'tenant';
        opts.recordMapper = (json) => new VCurrentUser(json);
        return this.fetch('', opts);
    }

    getAllUsers(opts = {}) {
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new VUser(json);
        return this.fetchAll(null, opts);
    }

    createUser(data , opts = {}) {
        opts.recordMapper = (json) => new VUser(json);
        opts.transformPayload = (data) => {
            data.id = undefined;
            return data
        }
        return this.create(data, opts);
    }

    saveUser(data, opts = {}) {
        opts.recordMapper = (json) => new VUser(json);
        const id = data.id;
        opts.transformPayload = (data) => {
            const existing = this.get(id);
            return Object.assign({}, existing, data);
        }
        return this.update(id, data, opts);
    }

    deleteUser(id, opts = {}) {
        return this.delete(id, opts);
    }
}

const userStore = new UserStore();
export default userStore;