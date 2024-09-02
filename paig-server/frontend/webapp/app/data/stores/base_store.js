import UiState from 'data/ui_state';

import f from 'common-ui/utils/f';
import {STORE_CONFIG} from 'common-ui/utils/globals';
import FSStore from 'common-ui/lib/fs_store/fs_store';

class BaseStore extends FSStore {
	constructor(opts = {}, urlRoot=STORE_CONFIG.urlRoot) {
		super(Object.assign({
			urlRoot,
			...opts
	    }));
    	this.catchError();
	}

	catchError() {
	    let apiCatchError = this.api.catchError;
	    let handleException = this.handleException;
	    this.api.catchError = function(response) {
	      handleException(response);
	      return apiCatchError(response);
	    }
	}
	checkForCancelToken = (opts) => {
		if (!opts.hasOwnProperty('addCancelToken')) {
			opts.addCancelToken = true;
		}
	}

	  handleException(exception) {
	    if (!exception || !exception.response) {
	    	if (exception.code == 'ECONNABORTED') {
	    		return;
	    	}
	    	if (exception.message) {
	    		f.notifyError(exception.message);
	    	}
	    	return;
	    }
	    switch(parseInt(exception.response.status)) {
	    	case 401:
		        let message = '';
		        if (typeof exception.response.data == 'object') {
		          message = exception.response.data.message || '';
		        } else if (typeof exception.response.data == 'string') {
		          message = exception.response.data || '';
		        }
				UiState.logout();
				/*
		        if (message == 'Session Timeout' || !message) {
		          UiState.logout();
		        } else {
		          f.notifyError(message);
		        }
				*/
	        	break;
	      	case 500:
		        if (exception.response.data && exception.response.data.msgDesc) {
		            f.notifyError(exception.response.data.msgDesc);
		        }
		        if(exception.config && exception.config.params && exception.config.params.doAs){
		          f.notifyError('Not able to get details from Ranger, as it might be down. Contact the System Administrator to check the configurations. Once it is up, we need to refresh the browser.');
		        }
		        break;
	      	case 0:
		        //f.notifyError(exception.response.data.msgDesc);
		        break;
	    }
	}
}

export default BaseStore;