import {observable} from 'mobx';
import FSBaseModel from 'common-ui/data/models/base_model';

class ReportConfig extends FSBaseModel {
	@observable reportName;
	@observable description;
	@observable paramJson;
	@observable emailTo;
	@observable emailMessage;
	@observable scheduleInfo;
	@observable status;

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }
}

export default ReportConfig;