import BaseStore from './base_store';
import MEvaluation from '../models/m_evaluation';

class EvaluationStore extends BaseStore {
    constructor() {
        let baseUrl = 'eval-service/api';
        super({
            type: 'evaluation',
            baseUrl
        });
        this.baseUrl = baseUrl;
    }

    addConfig(data, opts = {}) {
        opts.path = '/target/application';
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    updateConfig(data, opts = {}) {
        opts.path = `/target/application`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.update(data.target_id, data, opts);
    }

    fetchTargetConfig(data, opts = {}) {
        opts.path = `/target/application`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.fetch(data.target_id, opts);
    }

    
    addCategories(data, opts = {}) {
        opts.path = `/eval/categories`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    saveEvaluationConfig(data, opts = {}) {
        opts.path = '/config/save';
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    saveAndRunEvaluationConfig(data, opts = {}) {
        opts.path = '/eval/save_and_run';
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    evaluateConfig(data, opts = {}) {
        opts.path= `/eval/${data.id}/run`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    reRunReport(data, opts = {}) {
        opts.path= `/eval/${data.id}/rerun`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.create(data, opts);
    }

    fetchEvaluationConfigs(opts = {}) {
        opts.path = '/config/list';
        opts.recordMapper = (json) => new MEvaluation(json);
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        return this.fetchAll('', opts);
    }

    fetchEvaluationReports(opts = {}) {
        opts.path = '/eval/report/list';
        opts.recordMapper = (json) => new MEvaluation(json);
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        return this.fetchAll('', opts);
    }

    fetchEvaluationAppsList(opts = {}) {
        opts.path = '/target/application/list';
        opts.recordMapper = (json) => new MEvaluation(json);
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        return this.fetchAll('', opts);
    }

    deleteAppTarget(id, opts = {}) {
        opts.path= `/target/application`;
        return this.delete(id, opts);
    }
    
    deleteReport(id, opts = {}) {
        opts.path= `/eval/report`;
        return this.delete(id, opts);
    }

    deleteEvalConfig(id, opts = {}) {
        opts.path= `/config`;
        return this.delete(id, opts);
    }

    fetchReportCumulative(eval_uuid, opts = {}) {
        opts.path = `/eval/report/${eval_uuid}/cumulative`;
        opts.recordMapper = (json) => new MEvaluation(json);
        return this.fetch("", opts);
    }

    fetchReportDetailed(eval_uuid, opts = {}) {
        opts.path = `/eval/report/${eval_uuid}/detailed`;
        opts.recordMapper = (json) => new MEvaluation(json);
        opts.deserialize = (resp) => {
            let {content, ...page} = resp
            this.page = page;
            return content;
        }
        return this.fetchAll('', opts);
    }

}

const evaluationStore = new EvaluationStore();
export default evaluationStore;