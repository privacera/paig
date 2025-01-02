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
        opts.path = `/init`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }
}

const evaluationStore = new EvaluationStore();
export default evaluationStore;