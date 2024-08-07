import { isEmpty } from 'lodash';
import axios from 'axios';

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import stores from 'data/stores/all_stores';
import {DEFAULTS} from "common-ui/utils/globals";

const pageSize = DEFAULTS.DEFAULT_LOOKUP_PAGE_SIZE;

const cancelTokenMap = new Map();

const { userStore, groupStore, sensitiveDataStore, metaDataStore, metaDataValuesStore, vectorDBStore } = stores;

let sensitiveDataCancelToken = null;
function getAxiosSourceToken() {
  const CancelToken = axios.CancelToken;
  return CancelToken.source();
}

export function userGroupRolesLookups(searchString, callback, uniqKey="uniq", addKeyName="Everyone") {
  if (cancelTokenMap.has(uniqKey)) {
    const cancelTokens = cancelTokenMap.get(uniqKey);
    cancelTokens.forEach(source => {
      source.cancel();
    })
  }
  const headers = UiState.getHeaderWithTenantId();

  const userSource = getAxiosSourceToken();
  const groupSource = getAxiosSourceToken();
  const rolesSource = getAxiosSourceToken();

  cancelTokenMap.set(uniqKey, [userSource, groupSource, rolesSource]);
  
  const mergeOptions = [];
  if (Array.isArray(searchString)) {
    callback([])
    return;
  }
  searchString = searchString.trim();
  const params = {
    size: pageSize
  };

  const promiseArr = [
    userStore.getAllUsers({...headers, params: {...params, username: searchString}, cancelToken: userSource.token}),
    groupStore.searchGroups({params: {...params, name: searchString}, cancelToken: groupSource.token}),
  //   userStore.getAllRoles({params: {...params, roleNamePartial: searchString}, cancelToken: rolesSource.token})
  ]
  Promise.allSettled(promiseArr).then(results => {
    const [users, groups, roles ] = results;
    const usersOptions = users.status === 'fulfilled' ? f.models(users) : [];
    const groupsOptions = groups.status === 'fulfilled' ? f.models(groups) : [];
  //   const rolesOptions = roles.status === 'fulfilled' ? f.models(roles) : [];
    const prefix = "##__##";

    let opt = {};
    getFoundElementCount(users, opt, 'USERS')
    getFoundElementCount(groups, opt, 'GROUPS')
  //   getFoundElementCount(roles, opt, 'ROLES')

    if (!isEmpty(usersOptions)) {
      usersOptions.forEach(o => Object.assign(o, {value: `users${prefix}${o.username}`, label: o.username, type: 'USERS'}));
      mergeOptions.push(...usersOptions)
    }
    if (!isEmpty(groupsOptions)) {
      groupsOptions.forEach(o => Object.assign(o, {value: `groups${prefix}${o.name}`, label: o.name, type: "GROUPS"}));
      mergeOptions.push(...groupsOptions);
    }
  //   if (!isEmpty(rolesOptions)) {
  //     rolesOptions.forEach(r => Object.assign(r, {label: r.name,  value: `roles${prefix}${r.name}`, type: 'ROLES'}));
  //     mergeOptions.push(...rolesOptions)
  //   }
    if (!searchString || (searchString && addKeyName.startsWith(searchString))) {
      mergeOptions.unshift({label: addKeyName, value: `others${prefix}${addKeyName}`, type: "OTHERS"});
    }
    callback(mergeOptions, opt);
  })
}

export function sensitiveDataLookUps(searchString, callback) {
  if (sensitiveDataCancelToken) {
    sensitiveDataCancelToken.cancel();
    sensitiveDataCancelToken = null;
  }
  sensitiveDataCancelToken = getAxiosSourceToken();
  if (Array.isArray(searchString)) {
    callback([])
    return;
  }
  searchString = searchString.trim();
  const params = {
    size: pageSize
  }
  if (searchString) {
    params.name = searchString;
  }

  sensitiveDataStore.fetchSensitiveData({ params, cancelToken: sensitiveDataCancelToken.token})
  .then(resp => {
    let models = resp.models ?? [];
    models = models.map(d => ({label: d.name, value: d.name}))
    callback(models);
  }).catch(() => callback([]));
}

let metaDataCancelToken = null;
export function metaDataLookUps(searchString, callback, searchKey="name") {
  if (metaDataCancelToken) {
    metaDataCancelToken.cancel();
    metaDataCancelToken = null;
  }
  metaDataCancelToken = getAxiosSourceToken();
  if (Array.isArray(searchString)) {
    callback([])
    return;
  }
  searchString = searchString.trim();
  const params = {
    size: pageSize
  }
  if (searchString) {
    params.name = searchString;
  }

  metaDataStore.fetchMetaData({ params, cancelToken: metaDataCancelToken.token})
  .then(resp => {
    let models = resp.models ?? [];
    models = models.map(d => ({label: d.name, value: d.id}))
    callback(models);
  }).catch(() => callback([]));
}

let metaDataValueCancelToken = null;
export function metaDataValueLookUps(searchString, callback, searchKey="metadataValue", queryParam={}) {
  if (metaDataValueCancelToken) {
    metaDataValueCancelToken.cancel();
    metaDataValueCancelToken = null;
  }
  metaDataValueCancelToken = getAxiosSourceToken();
  if (Array.isArray(searchString)) {
    callback([])
    return;
  }
  searchString = searchString.trim();
  const params = {
    size: pageSize,
    ...queryParam
  }
  if (searchString) {
    params[searchKey] = searchString;
  }

  metaDataValuesStore.fetchMetaDataValues({ params, cancelToken: metaDataValueCancelToken.token})
  .then(resp => {
    let models = resp.models ?? [];
    models = models.map(d => ({label: d.metadataValue, value: d.id}))
    callback(models);
  }).catch(() => callback([]));
}

let vectorDBCancelToken = null;
export function vectorDBLookUps(searchString, callback) {
  if (vectorDBCancelToken) {
    vectorDBCancelToken.cancel();
    vectorDBCancelToken = null;
  }
  vectorDBCancelToken = getAxiosSourceToken();
  if (Array.isArray(searchString)) {
    callback([])
    return;
  }
  searchString = searchString.trim();
  const params = {
    size: pageSize
  }
  if (searchString) {
    params.name = searchString;
  }

  vectorDBStore.getVectorDBs({ params, cancelToken: vectorDBCancelToken.token})
  .then(resp => {
    let models = resp.models ?? [];
    models = models.map(d => ({label: d.name, value: d.name}))
    callback(models);
  }).catch(() => callback([]));
}

function getFoundElementCount(promise, obj, countFor) {
  if (promise.status === 'fulfilled') {
    obj[countFor] = f.pageState(promise).numberOfElements || f.models(promise).length;
  }
}

