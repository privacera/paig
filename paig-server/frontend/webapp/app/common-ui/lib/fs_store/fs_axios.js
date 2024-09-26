//external libs
import Promise from 'bluebird';
import axios from 'axios';
import isEmpty from 'lodash/isEmpty';
import {toJS} from 'mobx';
import p from 'es6-promise';
import moment from 'moment';

import UiState from 'data/ui_state';
import CommonUiState from 'common-ui/data/ui_state';
import {STORE_CONFIG} from 'common-ui/utils/globals';
import f from "common-ui/utils/f";
import {Utils} from 'common-ui/utils/utils';
import axiosState from 'common-ui/lib/fs_store/axios_state';

p.polyfill();

const defaults = {
  debug_mode: STORE_CONFIG.debug,
  urlRoot: '',
  enableURLCache: false
}

class FSAxios {

  isFunction (value) {
    return typeof value === 'function' || (value && toStr(value) === '[object Function]')
  }

  constructor( opts = {/*urlRoot, debug_mode, auth*/}) {

    Object.assign(this, defaults, opts);

    this.apiCache = new Map();

    this.$http = axios.create({
      headers: {
        'X-CSRF-TOKEN': this.getCSRFToken(),
        'X-XSRF-HEADER': "",
        'X-Requested-With': 'XMLHttpRequest',
        "Content-Type": "application/json"
      },
      auth: opts.auth,
    });

    this.setupInterceptors();
  }
  getCSRFToken() {
    const metas = document.getElementsByTagName('meta');
    for (let i = 0; i < metas.length; i++) {
      const meta = metas[i];
      if (meta.getAttribute('name') === '_csrf') {
        return meta.getAttribute('content');
      }
    }
    return null;
  }
  setupInterceptors(){
    //interceptors
    this.$http.interceptors.request.use(config => {
      if (this.urlRoot) {
        config.url = `${this.urlRoot}/${config.url}`;
      }
      return config;
    }, this.catchInterceptorError);

    this.$http.interceptors.response.use(response => {
      if(this.enableURLCache){
        console.log("Writing to cache. Key: ", this._getCacheKey(response.config, true));
        this.apiCache.set(this._getCacheKey(response.config, true), toJS(response.data));
      }
      return response;
    }, this.catchInterceptorError);
  }

  get(url, params = {}, opts = {}, gaEvent = axiosState.getGaEvent()) {
    return this._wrapAxios(url, null, params, opts, {
        method : 'GET'
    }, gaEvent);
  }

  put (url, data = {}, params = {}, opts = {}, gaEvent = axiosState.getGaEvent()) {
    return this._wrapAxios(url, data, params, opts, {
        method : 'PUT'
    }, gaEvent);
  }

  post (url, data = {}, params = {}, opts = {}, gaEvent = axiosState.getGaEvent()) {
    return this._wrapAxios(url, data, params, opts, {
        method : 'POST'
    }, gaEvent);
  }

  del(url, data, params = {}, opts = {}, gaEvent = axiosState.getGaEvent()) {
    return this._wrapAxios(url, data || null, params, opts, {
        method : 'DELETE'
    }, gaEvent);
  }

  beforeHTTP (...args ) {
    return Promise.resolve()
  }

  afterHTTP (...args) {
    return Promise.resolve()
  }

  _getCacheKey(c, baseUrl = false){
      return "" + (baseUrl ? c.url : `${this.urlRoot}/${c.url}`) + (c.params ? Object.keys(c.params).map((k) => `${k}=${c.params[k]}`).join('&') : "");
  }

  _axios (config = {}, opts = {}) {
    const start = new Date()
    config.method = config.method.toUpperCase()

    if( !CommonUiState.isCloudEnv() ) {
      if (config.params && config.params.resource && config.method == "GET" && !this.isEncoded(config.params.resource)) {
        config.params = {...config.params,
          resource: encodeURIComponent(config.params.resource)
        }
      }
      if (config.params && config.params.resources && config.method == "GET" && !this.isEncoded(config.params.resources)) {
        config.params = {...config.params,
          resources: encodeURIComponent(config.params.resources)
        }
      }
    }

    const logResponse = (data) => {
      const str = `${start.toUTCString()} :: ${config.method.toUpperCase()}: ${config.url} :: ${data.status} :: ${(new Date().getTime() - start.getTime())}ms`
      if(data && data.request && data.request.responseURL && data.request.responseURL.replace(window.location.origin, "") == '/login'){
        window.location.href = window.location.origin;
      }
      if (data.status >= 200 && data.status < 300) {
        this.debug(`SUCCESS: ${str} :: data: `, data);
        return data;
      } else {
        return Promise.reject(data);
      }
    }

    const makeCall = (_config) => {

        if (this.enableURLCache){
          const cachedObject = this.apiCache.get(this._getCacheKey(_config));
          //return data from cache
          if (!isEmpty(cachedObject)) {
            this.debug(`Cache Hit: ${_config.path} :: data: `, toJS(cachedObject));
            return Promise.resolve(toJS(cachedObject));
          }
        }

        axiosState.sessionInfo.lastSyncTime = new moment();
        axiosState.sessionInfo.apiObj = config;

        return this.$http(config).then(logResponse, logResponse)
          .then(res => res)
          .catch((err) => this.catchError(err));
    }

    return Promise.resolve(this.beforeHTTP(config, opts))
      .then((_config) => {
        return makeCall(_config || config);
      })
      .then((response) => {
        return Promise.resolve(this.afterHTTP(config, opts, response))
          .then((_response) => _response === undefined ? response : _response)
      })
  }

  _wrapAxios(url, data = {}, config = {}, opts = {}, wrap={}, gaEvent = axiosState.getGaEvent()) {
    config.url = url || config.url;
    let dummyFn = () => {};
    let method = config.method = wrap.method;
    let beforeFn = wrap.beforeFn || dummyFn;
    let afterFn = wrap.afterFn || dummyFn;
    config.data = data || config.data;
    if (opts.timeout != null) {
      config.timeout = opts.timeout;
    }
    if (opts.responseType != null) {
      config.responseType = opts.responseType;
    }

    if (gaEvent) {
      Utils.GAevent(axiosState.getReactGA(), wrap.method, url , data, config , opts); //google-analytics event 
    }
    // TODO remove data in case of GET
    let fnArgs = [url, data, config, opts];

    return Promise.resolve(beforeFn.apply(this, fnArgs))
      .then((_config) => {
          this.debug_mode && this.debug(`Request sent: ${method}, ${url}, config:`, config, `opts: `, opts);
          return this._axios(config,opts);
      })
      .then((resp) => {
        fnArgs.push(resp);
        return Promise.resolve(afterFn.apply(this,fnArgs))
          .then((_r) => _r === undefined ? resp: _r);

    })
  }

  debug = (...args) => {
    if (this.debug_mode) {
      console.debug('fetch :', ...args);
    }
  }

  catchError(response={}) {
    let err = null;
    if (response && response.message && response.message.includes('777')) {
      f.notifyError('PAIG support session has beed expired.');
      err = new Error();
      err.message = response.message;
      err.data = response.data;
      err.response = response;
      if (UiState?.setSwitchRoleProps) {
        setTimeout(() => {
          UiState.setSwitchRoleProps(true);
        }, 1000);
      }
    } else if (response.code != 'ECONNABORTED') {
      err = new Error();
      err.message = response.message;
      err.data = response.response && response.response.data;
      err.response = response.response;

      //fetch error code 500, for unified ui changes.
      if(response && response.message && response.message.includes('500')){
        err.errorCode = '500'
      }
    }
    return Promise.reject(err);
  }

  catchInterceptorError(error) {
    return Promise.reject(error);
  }
  isEncoded = (str = '') => {
    let isEncoded = false;
    try {
      isEncoded = (str !== decodeURIComponent(str));
    } catch(e) {
      console.log('Failed to check isEncoded');
    }
    return isEncoded;
  }
}

export default FSAxios;
