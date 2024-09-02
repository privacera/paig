import {observable} from 'mobx';
import FSBaseModel from 'common-ui/data/models/base_model';

class ScanSchedule extends FSBaseModel {
	@observable name;
	@observable startTime;
	@observable scheduleType;
	@observable day;
	@observable month;
	@observable duration;
	@observable isAll;
	@observable objectId;
	@observable objectClassType;
	@observable lastScheduled;
	@observable scheduledFor;

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }
}

export default ScanSchedule;