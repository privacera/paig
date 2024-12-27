import BaseStore from './base_store';

class EvaluationStore extends BaseStore {
    constructor() {
        let baseUrl = 'governance-service/api/ai/evaluation';
        super({
            type: 'vector_db',
            baseUrl
        });
        this.baseUrl = baseUrl;
    }
}

const evaluationStore = new EvaluationStore();
export default evaluationStore;