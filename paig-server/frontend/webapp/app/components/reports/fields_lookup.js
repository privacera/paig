import { isArray, isEmpty } from "lodash";
import axios from "axios";
import moment from "moment-timezone";

import f from "common-ui/utils/f";
import stores from "data/stores/all_stores";
import { DEFAULTS } from "common-ui/utils/globals";

const pageSize = DEFAULTS.DEFAULT_LOOKUP_PAGE_SIZE;

const cancelTokenMap = new Map();

const { dashboardStore } = stores;

export function usersLookup(searchString, callback, uniqKey = "uniq") {
  if (isArray(searchString)) {
    emptyOptions(callback);
    return;
  }
  const params = {groupBy: 'userId', size: pageSize };
  if (searchString) {
    params['includeQuery.userId'] = searchString +'*';
  }

  const userSource = getAxiosSourceToken();
  cancelTokenMap.set(uniqKey, userSource);

  dashboardStore
    .fetchUserIdCounts({ params, cancelToken: userSource.token })
    .then((resp) => {
      let models = [];
      if (!isEmpty(resp.userId)) {
        models = Object.keys(resp.userId).map(k => ({label: k, value: k}));
      }
      callback(models);
    })
    .catch((err) => emptyOptions(callback));
}

export function applicationLookup(searchString, callback, uniqKey = "uniq") {
  triggerCancelAPI(uniqKey);
  if (Array.isArray(searchString)) {
    emptyOptions(callback);
    return;
  }
  const params = { size: pageSize, groupBy: "applicationName" };
  if (searchString) {
    params['includeQuery.applicationName'] = searchString + "*";
  }

  const applicationSource = getAxiosSourceToken();
  cancelTokenMap.set(uniqKey, applicationSource);

  dashboardStore
    .fetchAppNameCounts({ params, cancelToken: applicationSource.token })
    .then((resp) => {
      let models = [];
      if (!isEmpty(resp.applicationName)) {
        models = Object.keys(resp.applicationName).map(k => ({label: k, value: k}));
      }
      callback(models);
    })
    .catch((err) => emptyOptions(callback));
}

function triggerCancelAPI(uniqKey) {
  if (cancelTokenMap.has(uniqKey)) {
    const cancelToken = cancelTokenMap.get(uniqKey);
    if (cancelToken) {
      cancelToken.cancel();
      cancelTokenMap.delete(uniqKey);
    }
  }
}

function getAxiosSourceToken() {
  const CancelToken = axios.CancelToken;
  return CancelToken.source();
}

function getFoundElementCount(promise, obj, countFor) {
  if (promise.status === "fulfilled") {
    obj[countFor] =
      f.pageState(promise).numberOfElements || f.models(promise).length;
  }
}

function emptyOptions(callback, labelKey = "label", valueKey = "value") {
  callback([]);
}

function getOptions(
  resp,
  searchString,
  labelKey = "label",
  valueKey = "value"
) {
  const options = resp.models.slice().map((m) => {
    if (m.options) {
      delete m.options; // it break select2 in nested options...
    }
    return m;
  });
  const totalCount = resp.raw.rawResponse.data.totalCount;
  if (totalCount > pageSize) {
    const labelValue = `+ ${totalCount - pageSize}`;
    options.push({
      [valueKey]: searchString + "-" + moment().unix(),
      [labelKey]: labelValue,
      disabled: true,
    });
  }
  return options;
}
