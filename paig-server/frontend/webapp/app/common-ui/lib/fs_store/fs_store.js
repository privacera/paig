import {observable, action } from 'mobx';
import {fromPromise} from 'mobx-utils';
import mergeItems from 'merge-items';
import { v5 as uuidv5 } from 'uuid';
import axios from 'axios';
import {result, isFunction, map, forEach, filter, find, uniq, hasIn, remove, cloneDeep} from 'lodash';

import FSAxios from './fs_axios';
import requestHandler from 'common-ui/lib/fs_store/cancelRequestMapper';
import {Utils} from 'common-ui/utils/utils';
import axiosState from 'common-ui/lib/fs_store/axios_state';

//TODO make this into an npm library!
export default class FSStore {
  @observable apiInProgress = true;

  models = [];
  recordMapperMap = new Map();

  paginatedCollections = [];

  idAttribute = 'id';

  constructor(opts = {/*type, baseUrl, urlRoot, auth*/}) {

    Object.assign(this, {urlRoot : opts.urlRoot},  opts);
    let option = {
      urlRoot : opts.urlRoot,
      auth: opts.auth
    }
    this.api = new FSAxios(option);

  }
  _m(param = ''){
    throw new Error(`Missing parameter: ${param}`);
  }

  urlError(){
    throw new Error("No valid URL specified!!");
  }

  // Derived classes should override this if required
  makeUrl (id , opts = {}){
    let url = result(opts, 'baseUrl') || result(this,'baseUrl') || this.urlError();
    // TODO use some standard way here. For eg. what if baseUrl has trailing slash and path has beginning slash?
    url = (opts.path) ? `${url}/${opts.path}` : url;
    return url.replace(/([^:]\/)\/+/g, '$1') + (id ? `/${encodeURIComponent(id)}` : '');
  }

  @action
  _beforeApi (opts, path){
    this.apiInProgress = true;
    if (opts.addCancelToken && !opts.cancelToken) {
      const { cancelRequest } = requestHandler;
      const uuid = uuidv5(Utils.getUniquePath(path, opts.params), uuidv5.URL);
      if (opts.params && opts.params.uniqueIdForCancel) {
        delete opts.params.uniqueIdForCancel;
      }
      if (cancelRequest.get(uuid)) {
        const api = cancelRequest.get(uuid);
        if (isFunction(api?.cancel)){
          api.cancel();
        }
        if (opts.afterCancelCallback) {
          setTimeout(opts.afterCancelCallback, 0)
        }
        cancelRequest.delete(uuid)
      }
      const source = axios.CancelToken.source()
      cancelRequest.set(uuid,source);
      opts.cancelToken = source.token;
      delete opts.addCancelToken;
      delete opts.afterCancelCallback;
    }
  }

  create ( data , opts = {}) {
    const payload = opts.transformPayload ? opts.transformPayload(data) : data;
    const  path = this.makeUrl('', opts);
    this._beforeApi(opts, path);
    return this.api.post(path, payload, opts)
      .then((_resp) => {
        if (opts.rawResponse) {
          return _resp;
        }
        return this._after(_resp, opts, path);
      });
  }

  update ( id, data, opts = {}) {
    const payload = opts.transformPayload ? opts.transformPayload(data) : data;
    const path = this.makeUrl(id, opts);
    this._beforeApi(opts, path);
    return this.api.put(this.makeUrl(id, opts), payload, opts)
      .then((_resp) => this._after(_resp, opts, path));
  }

  fetch ( id, opts = {}) {
    if (!opts.noCache){
      try{
        const existing = this.get(id, opts);
        if (existing !== undefined) {
          return fromPromise(Promise.resolve(existing));
        }
      }
      catch(err){
        console.error("get failed!", err);
      }
    }
    const path = this.makeUrl(id, opts)
    this._beforeApi(opts, path);
    return fromPromise(this.api.get(path, opts )
      .then((_resp) => this._after(_resp, opts, path)));
  }

  //TODO: How to solve the problem of caching fetchAll calls?
  // Eg. if store have 4 records and user make call for [1..8],
  // How to make call call only for remaining 4 records??
  fetchAll ( query, opts = {}, id) {
    /*
    if (!opts.noCache){
      try{
        const existing = this.filter(query);
        if (existing !== undefined) {
          return Promise.resolve(existing);
        }
      }
      catch(err){
        console.log("get failed!", err);
      }
    }*/

    // Need raw = true for setting page state
    Object.assign(opts, {raw: true, type : 'fetchAll'});
    const path =  this.makeUrl(id || '', opts);
    this._beforeApi(opts, path);
    return fromPromise(this.api.get(path, opts )
      .then((_resp) => this._after(_resp, opts, path))
      .then((_resp) => this._toCollection(_resp, opts)));
  }

  _fetch (opts, id = '') {
    Object.assign(opts, {raw: true, type : 'fetchAll'});
    return this.api.get( this.makeUrl(id, opts), opts);
  }

  delete ( id , opts = {}, data) {
    const path = this.makeUrl(id || '', opts);
    this._beforeApi(opts, path);
    return fromPromise(this.api.del(path, data, opts)
      .then((_resp) => this._afterDel(id, _resp, opts, path)));
  }

  _deserialize (response, opts = {}) {
    if (isFunction(opts.deserialize)) {
      return opts.deserialize.call(this, response, opts)
    }

    return response;
  }

  @action
  _after (response, opts, path){
    const {cancelRequest} = requestHandler;
    const uuid = uuidv5(Utils.getUniquePath(path, opts.params), uuidv5.URL)
    if (cancelRequest.has(uuid)) {
      cancelRequest.delete(uuid);
    }
   
    let rawResponse = cloneDeep(response);
    response = response ? response.data: response;
    let des = this._deserialize(response, opts);
    // In case deserialize does not return valid data, set it to empty array for _inject
    des = des != undefined ? des : [];
    this._handleMapperModels(opts);
    if (typeof des == "object") {
      let injected = this._inject(des, opts);
      let _models = Array.isArray(response) ? response : [response];
      if (injected) {
        _models = this.get(this.getInjectOrderList(injected, des));
        if (opts.type !== 'fetchAll'){
            _models = (_models.length == 1) ? _models[0] : _models;
        }
      }
      return (opts.raw) ?  {models:_models, raw:response, rawResponse} : _models;
    }
    return response;
  }
  _handleMapperModels(opts={}) {
    if(!opts.recordMapper) {
      return;
    }
    let recordMapperName = opts.recordMapper().constructor.name;
    let recordMapperModels =  this.recordMapperMap.get(recordMapperName)
    if (recordMapperModels) {
      this.models = recordMapperModels;
    } else {
      delete this.models;
      this.models = [];
      this.recordMapperMap.set(recordMapperName, this.models);
    }
  }
  getInjectOrderList = (injected, models=[]) => {
    let orderList;
    try {
      orderList = models.map(m => m[this.idAttribute]);
    } catch(e) {
      orderList = uniq([...injected.updated, ...injected.inserted]);
    }

    return orderList;
  }

  @action
  _afterDel (id, response, opts, path){
    const {cancelRequest} = requestHandler;
    const uuid = uuidv5(Utils.getUniquePath(path, opts.params), uuidv5.URL)
    if (cancelRequest.has(uuid)) {
      cancelRequest.delete(uuid);
    }
    /* TODO FIXME how to handle return if multiple ids are given
    const _ids = ids instanceof Array ? ids : [ids];
    _ids.forEach( i => _remove(i));
    */
    this._remove(id || opts.id, opts);
    return response.data;

  }

  @action _remove(id, opts={}) {
    if (opts.models){
      if (hasIn(opts.models, 'value.models')){
        let models = opts.models.value.models;
        remove(models, model => {
          return model[this.idAttribute] === id;
        });
        //opts.models.value.models.remove(id);
      }

    }
    return remove(this.models, model => {
      return model[this.idAttribute] === id;
    });
  }

  _toCollection (response, opts){
    let _models = observable([]);
    let pageState = {};
    if (response.raw && response.raw.hasOwnProperty('totalCount')) {
      const {pageSize, queryTimeMS, resultSize, sortBy, sortType, startIndex, totalCount} = response.raw;
      pageState = {
        queryTimeMS,
        sortBy,
        sortType,
        startIndex,
        numberOfElements: resultSize,
        size: pageSize,
        sort: null,
        totalElements: totalCount,
        totalPages: Math.ceil(totalCount/pageSize),
      };
      if(this.rangerRemote){
        pageState.number = parseInt(pageState.startIndex/pageState.size);
        if(pageState.number == 0){
          pageState.first = pageState.last = true;
        }else{
          pageState.first = false;
          pageState.last = (pageState.totalPages > pageState.number ) ? false : true;
        }
      }

    } else {
      const {content, ...ps} = response.raw;
      pageState = ps;
    }
    //pageState.currentPage = parseInt(pageState.startIndex/pageState.pageSize);
    _models = response.models;
    return {models:_models, pageState, raw:response};
  }

  @action _inject(items, opts = {}) {
    //TODO merge the passed opts
    this.apiInProgress = false;
    const mapper = isFunction(opts.recordMapper) ? opts.recordMapper : this.recordMapper;
    if (!mapper) {
      return;
    }
    const _opts = {
      primaryKey: this.idAttribute,
      mapper : mapper
    };
    //TODO: need better solution, remove all this.models, _handleMapperModels methods from store and keep it simple
    this.models = [];

    try {
      let res = {
        inserted: [],
        updated: []
      }

      if (typeof items == 'object' && !Array.isArray(items)) {
        items = [items];
      }

      items.forEach((item, i) => {
        item = _opts.mapper(item);
        if (axiosState.shouldGenerateRandomId() && !item.id) {
          item.id = i;
        }
        res.inserted.push(item.id);
        this.models.push(item);
      });

      return res;
    } catch (e) {
      return mergeItems(this.models, items, _opts);
    }
  }

  /* Functions that will just work on the observable. i.e local store */

  get(id, opts={}) {
      if (id instanceof Array) {
          let modelIdList = map(this.models, 'id');
          let models = [];
          forEach(id, i => {
              let index = modelIdList.indexOf(i);
              if (index > -1) {
                models.push(this.models[index]);
              }
          });
          return models;
      } else {
          let models = this.models;
          if (opts.recordMapper && this.recordMapperMap.size) {
            let recordMapper = opts.recordMapper || this.recordMapper;
            models = recordMapper ? this.recordMapperMap.get(recordMapper().constructor.name) || [] : this.models;;
          }
          if (!models) {
            models = this.models;
          }
          return models.find(record => record[this.idAttribute] == id);
          //const fnd_ret = find(this.models.slice(), {[this.idAttribute]: id});
          //return fnd_ret;
      }
 }

 /* Just wrap the lodash function */
 filter(predicate) {
   return filter(this.models, predicate);
 }

 /* Just wrap the lodash function */
 find(predicate) {
   return find(this.models, predicate);
 }

}
