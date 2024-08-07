import BaseStore from './base_store';
import MJobDetail from '../models/m_job_detail';

class JobManagerStore extends BaseStore {
	constructor() {
        super({
            type: 'Job Manager Store',
            baseUrl: 'job-manager/api'
        });
    }
    getJobDetail(opts = {}) {
        opts.path = "job-details";
        opts.recordMapper = (json) => new MJobDetail(json);
        opts.deserialize = (resp) => {
          let { content, ...page } = resp;
          this.page = page;
          return content;
        };

        return this.fetchAll("", opts);
    }
}

const jobManagerStore = new JobManagerStore();
export default jobManagerStore;