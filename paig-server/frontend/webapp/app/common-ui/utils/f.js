import {fromPromise} from 'mobx-utils';
import hasIn from 'lodash/hasIn';
import Promise from 'bluebird';
import {observable, transaction} from 'mobx';

import Grow from '@material-ui/core/Grow';

import {ERROR_MESSAGE} from 'utils/globals';
import {Utils} from 'common-ui/utils/utils';
import UiState from 'common-ui/data/ui_state';

const f = {
  _notificationSystem : null,

  setNotificationSystem(n) {
    this._notificationSystem = n;
  },

  setConfirmBox(c) {
    this._confirm = c;
  },

  isPromise(promise) {
    if (!hasIn(promise, "constructor.name")) return false;
    return promise.constructor.name == "Promise";
  },

  isPending(promise) {
    if (!this.isPromise(promise)) return;
    if (!(promise && promise['state'])) throw new Error("promise.state undefined!!");
    return promise.state === "pending";
  },

  isFulfilled(promise){
    if (!this.isPromise(promise)) return;
    if (!(promise && promise['state'])) throw new Error("promise.state undefined!!");
    return promise.state === "fulfilled";
  },

  isRejected(promise){
    if (!this.isPromise(promise)) return;
    if (!(promise && promise['state'])) throw new Error("promise.state undefined!!");
    return promise.state === "rejected";
  },

  setPageState(promise, pageState){
    if (this.isPending(promise)) return;
    if (hasIn(promise,'value.pageState')){
      promise.value.pageState = pageState; 
      return;
    };
    throw new Error("f.pageState(), No value.pageState found in : ", promise);
  },

  pageState(promise){
    if (this.isPending(promise)) return {};
    if (hasIn(promise,'value.pageState'))  return promise.value.pageState;
    throw new Error("f.pageState(), No value.pageState found in : ", promise);
  },

  models(promise){
    if (this.isPending(promise)) return [];
    if (hasIn(promise,'value.models'))  return promise.value.models;
    throw new Error("f.models(), No value.models found in : ", promise);
  },

  isLoading(promise) {
    if (this.isPending(promise)) return true;
    if (hasIn(promise,'value.loading'))  return promise.value.loading;
    throw new Error("f.isLoading(), No value.loading found in : ", promise);
  },
  

  initCollection(options = { loading: true }, models = [], pageState = {}) {
    let obj = observable({
      models,
      pageState: pageState,
      loading: !!options.loading
    });
    return fromPromise(Promise.resolve(obj))
  },


  beforeCollectionFetch(coll) {
    if (coll && coll.value) {
      transaction(() => {
        coll.value.loading = true;
        if (Array.isArray(coll.value.models)) {
          coll.value.models.replace([])
        } else {
          coll.value.models = []
        }
      })
    }
  },

  resetCollection(coll, newList=[], pageState) {
    if (coll && coll.value) {
      transaction(() => {
        coll.value.models = newList;
        coll.value.loading = false;
        //clear erroCode set when its 500.
        coll.value.errorCode && delete coll.value.errorCode
        if (pageState) {
          coll.value.pageState = pageState;
        }
      })
    } else if (coll) {
      coll.then(() => {
        transaction(() => {
          coll.value.models = newList;
          coll.value.loading = false;
          coll.value.errorCode && delete coll.value.errorCode;
          if (pageState) {
            coll.value.pageState = pageState;
          }
        })
      })
    }
  },

  resetPaginationParams(coll, newParams = {page: 0}) {
    if (coll && coll.params) {
      coll.params = Object.assign(coll.params, newParams)
    }
  },

  handleSuccess(coll, callback) {
      return ((response) => {
          if (!coll) {
              return;
          }
          transaction(() => {
            coll.value.models = response.models;
            coll.value.pageState = response.pageState;
            coll.value.loading = false;
            //clear erroCode set when its 500.
            coll.value.errorCode && delete coll.value.errorCode
          })
          callback && callback(coll)
      })
  },

  handleError(coll, callback, opts={}) {
      return ((err={}) => {
          if (typeof err?.data === 'string') {
            err.data = Utils.parseJSON(err.data);
          }
          if (opts?.confirm?.hide) {
              opts.confirm.hide();
          }
          if (err && err.data && (err.data.msgDesc || err.data.message)) {
            let errMsg = err.data.msgDesc || err.data.message; 
            if (ERROR_MESSAGE[errMsg] && err.data.messageList && err.data.messageList.length && err.data.messageList[0].count) {
                const errorMessage = ERROR_MESSAGE[errMsg].value
                f.notifyError(errorMessage.replace('0', err.data.messageList[0].count));
            } else {
                f.notifyError(errMsg, opts);
            }
          }
          if (err && err.msgDesc) {
            f.notifyError(err.msgDesc, opts);
          }
          if (coll && coll.value) {
              transaction(() => {
                coll.value.loading = false;
                coll.value.pageState.totalPages = 0;

                if (err.errorCode) {
                  coll.value.errorCode = err.errorCode;
                }
              })
          }
          if (opts.modal && opts.modal.okBtnDisabled) {
            opts.modal.okBtnDisabled(false);
          }
          callback && callback()
      })
  },
  
  handleRangerError(coll, callback, opts={}) {
      const capitaliseFirstLetter = (string)=> {
    		return string.charAt(0).toUpperCase() + string.slice(1);
    	};
      const showErrorMsg = (respMsg)=>{
      	let respArr = respMsg.split(/\([0-9]*\)/);
      	respArr = respArr.filter(str => str);

      	respArr.forEach(str => {
          let matchFound = false;
          if (str.includes('error code[3006]')) {
            const pattern = /policy-id=\[(\d+)\]/;
            const policyId = str.match(pattern)?.[1];
            matchFound = !!policyId;
            policyId && f.notifyError(`Policy ${policyId} already exists with same name.`);
          } else if (str.includes('error code[3010]')) {
            const pattern = /.*policy-name=\[(.*?)\]/;
            const policyName = str.match(pattern)?.[1];
            matchFound = !!policyName;
            policyName && f.notifyError(`Policy "${policyName}" already exists with matching resource.`);
          }
          if (!matchFound) {
            let validationMsg = str.split(',');
            let erroCodeMsg = '';
        		//get code from string 
        		if (validationMsg.length && validationMsg[0].indexOf("error code") != -1) {
        			let tmp = validationMsg[0].split('error code');
        			let code = tmp[ tmp.length - 1 ];

        			erroCodeMsg = 'Error Code : '+ code.match(/\d/g).join('');
        		}
        		let reason = str.lastIndexOf("reason") != -1 ? (str.substring(str.lastIndexOf("reason")+7, str.indexOf("field[")-3 )) : str;
            erroCodeMsg = erroCodeMsg != "" ? erroCodeMsg +"   " : "";
        		const erroMsg = erroCodeMsg +""+ capitaliseFirstLetter(reason);
            f.notifyError(erroMsg);
          }
      	});
      };
      return ((err={}) => {
        if (opts.confirm && opts.confirm.hide) {
          opts.confirm.hide();
        }
        if (err?.data?.msgDesc) {
          showErrorMsg(err.data.msgDesc);
        } else if (err && err.msgDesc) {
          showErrorMsg(err.msgDesc);
        }
        if (coll && coll.value) {
          transaction(() => {
            coll.value.loading = false;
            coll.value.pageState.totalPages = 0;
          })
        }
        if (opts.modal && opts.modal.okBtnDisabled) {
          opts.modal.okBtnDisabled(false);
        }
        callback && callback()
      })
  },
  handlePagination(coll, params) {
    if (!coll) {
      return;
    }

    let pageState = f.pageState(coll);
    let models = f.models(coll);
    params = params || coll.params || {};
    if (models.length == 0 && params.page > 0) {
      params.page = params.page - 1 || undefined;
    }
  },

  notify (msg, opts={}){
    this._notificationSystem.enqueueSnackbar(msg, {
      preventDuplicate: true,
      key: msg,
      variant: 'success',
      anchorOrigin: {
        vertical: 'top',
        horizontal: 'right',
      },
      TransitionComponent: Grow,
      ...opts
    });
  },

  notifySuccess(message = '', opts={}){
    this.notify(message, {
      variant: 'success',
      ...opts
    });
  },

  notifyError(message = '', opts={}){
    if (UiState.isCloudEnv() && !opts.autoHideDuration) {
      opts.autoHideDuration = 1000*20;
    }
    this.notify(message, {
      variant: 'error',
      ...opts
    });
  },

  notifyInfo(message = '', opts={}){
    this.notify(message, {
      variant: 'info',
      ...opts
    });
  },
  notifyWarning(message = '', opts={}){
    this.notify(message, {
      variant: 'warning',
      ...opts
    });
  }
}

export default f;