import BaseStore from './base_store';
import AdminAudits from '../models/m_admin_audits';

class AdminAuditsStore extends BaseStore {
	constructor() {
    super({
      type: "Admin Audits",
      baseUrl: 'data-service/api/admin_audits'
    });
  }
  fetchComplianceAudits(opts = {}) {
    opts.path = "search";
    opts.deserialize = (resp) => {
      let {content, ...page} = resp
      content.forEach((item, i) => {
        if (!item.id) {
          item.id = item.logId || i;
        }
      })
      this.page = page;
      return content;
    }
    opts.recordMapper = (json) => new AdminAudits(json);
    return this.fetchAll("", opts);
  }
  fetchAdminContentComplianceCounts(opts = {}) {
    opts.path = "count";
    opts.recordMapper = (json) => new AdminAudits(json);
    
    return this.fetch("", opts);
  }
}

const adminAuditsStore = new AdminAuditsStore();
export default adminAuditsStore;