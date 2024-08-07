import BaseStore from './base_store';
import MShieldAuditsReport from '../models/m_shield_audits_report';

class ShieldAuditsReportsStore extends BaseStore {
    constructor() {
        super({
            type: 'Shield Audits Reports',
            baseUrl: 'data-service/api/shield_audits/reports'
        });
    }

    searchReports(opts = {}) {
        opts.deserialize = (resp) => {
            let {content, ...page} = resp;
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new MShieldAuditsReport(json);
        return this.fetchAll('', opts);
    }

    getReport(id, opts={}) {
        opts.recordMapper = (json) => new MShieldAuditsReport(json);
        return this.fetch(id, opts);
    }

    createReport(data, opts={}) {
        opts.recordMapper = (json) => new MShieldAuditsReport(json);
        opts.transformPayload = (data) => {
            return data
        }
        return this.create(data, opts);
    }

    updateReport(data, opts = {}) {
        opts.recordMapper = (json) => new MShieldAuditsReport(json);
        return this.update(data.id, data, opts);
    }

    deleteReport(id, opts = {}) {
        return this.delete(id, opts);
    }
}

const shieldAuditsReportsStore = new ShieldAuditsReportsStore();
export default shieldAuditsReportsStore;