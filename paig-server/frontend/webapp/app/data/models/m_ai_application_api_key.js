import {observable} from 'mobx';

import FSBaseModel from 'common-ui/data/models/base_model';
import {Utils} from 'common-ui/utils/utils';

class AiApplicationApiKey extends FSBaseModel {
  @observable tokenExpiry;
  constructor(props = {}, opts = {}) {
    super(props, opts);
    Object.assign(this, props);
  }
  getTokenExpiryInDaysAndHour() {
    const moment = Utils.dateUtil.momentInstance();
    let date = moment(this.tokenExpiry);

    let duration = moment.duration(date.diff(moment()));
    let days = date.diff(moment(), 'days');
    let hours = duration.hours();
    let minutes = duration.minutes();
    let seconds = duration.seconds();

    let expiry = [];
    if (days > 0) {
      expiry.push(`${days} day${days > 1 ? 's' : ''}`);
    }
    if (hours > 0) {
      expiry.push(`${hours} hr${hours > 1 ? 's' : ''}`);
    } else if (minutes > 0) {
      expiry.push(`${minutes} min${minutes > 1 ? 's' : ''}`);
    } else if (seconds > 0) {
      expiry.push(`${seconds} sec${seconds > 1 ? 's' : ''}`);
    }
    if (expiry.length) {
      expiry = expiry.join(' ');
    } else {
      expiry = null;
    }
    return expiry;
  }
}

export default AiApplicationApiKey;