import BaseStore from './base_store';
import VSecurityAudits from '../models/m_security_audits';

class SecurityAuditsStore extends BaseStore {
	constructor() {
        super({
            type: 'Security Audits',
            baseUrl: 'data-service'
        });
    }
    fetchSecurityAudits(opts = {}) {
        opts.path = 'api/shield_audits/search';
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            content.forEach((item, i) => {
                if (!item.id) {
                    item.id = item.eventId || i;
                }
            })
            this.page = page;
            return content;
        }
        opts.recordMapper = (json) => new VSecurityAudits(json);
        return this.fetchAll('', opts);
    }
}

const securityAuditsStore = new SecurityAuditsStore();
export default securityAuditsStore;