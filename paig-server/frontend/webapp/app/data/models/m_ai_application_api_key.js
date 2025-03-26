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
    const isFuture = duration.asSeconds() > 0;

    if (!isFuture) {
      duration = moment.duration(moment().diff(date));
    }

    const units = [
      { unit: 'year', value: duration.years() },
      { unit: 'month', value: duration.months() },
      { unit: 'day', value: duration.days() },
      { unit: 'hour', value: duration.hours() },
      { unit: 'minute', value: duration.minutes() },
      { unit: 'second', value: duration.seconds() }
    ];

    for (const { unit, value } of units) {
      if (value > 0) {
        return isFuture
          ? `in ${value} ${unit}${value > 1 ? 's' : ''}`
          : `${value} ${unit}${value > 1 ? 's' : ''} ago`;
      }
    }

    return 'just now';
  }
}

export default AiApplicationApiKey;