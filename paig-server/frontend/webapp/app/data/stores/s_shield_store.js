import BaseStore from './base_store';
import MGuardrailTest from '../models/m_guardrail_test';

class ShieldStore extends BaseStore {
    constructor() {
        super({
            type: 'user',
            baseUrl: 'shield',
        });
    }

    testGuardrail(data, opts = {}) {
        opts.path = 'guardrail/test';
        opts.recordMapper = (json) => new MGuardrailTest(json);
        return this.create(data, opts);
    }
}

const shieldStore = new ShieldStore();
export default shieldStore;