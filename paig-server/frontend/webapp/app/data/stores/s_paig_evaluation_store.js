import BaseStore from './base_store';
import MEvaluation from '../models/m_evaluation';

class EvaluationStore extends BaseStore {
    constructor() {
        let baseUrl = 'evaluation-service/api';
        super({
            type: 'evaluation',
            baseUrl
        });
        this.baseUrl = baseUrl;
    }
    generateEvaluation(data, opts = {}) {
        opts.path = `/generate`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    createEvaluation(data, opts = {}) {
        opts.path = `/init`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    fetchEvaluationReports(opts = {}) {
        opts.path = '/search';
        opts.recordMapper = (json) => new MEvaluation(json);
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            console.log('content', content);
            return content;
        }
        console.log('opts', opts);
        return this.fetchAll('', opts);
    }

}

const evaluationStore = new EvaluationStore();
export default evaluationStore;