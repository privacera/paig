import {action} from 'mobx';
import {Utils} from 'common-ui/utils/utils';

class FSBaseModel {
  _afterReset() {}
  @action
  reset(props) {
    Object.assign(this, props);
    this._afterReset();
  }

  stringToArray(string, splitBy) {
    return Utils.stringToArray(string, splitBy);
  }
}

export default FSBaseModel;