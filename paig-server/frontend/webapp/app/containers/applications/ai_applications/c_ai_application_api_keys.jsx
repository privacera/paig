import React, {Component, Fragment, createRef} from 'react';
import {inject, observer} from 'mobx-react';
import {withRouter} from 'react-router';
import {observable} from 'mobx';

import {Grid, Paper, Box}  from "@material-ui/core";

import f from 'common-ui/utils/f';
import UiState from 'data/ui_state';
import {Utils} from 'common-ui/utils/utils';
import FSModal from 'common-ui/lib/fs_modal';
import {DEFAULTS} from 'common-ui/utils/globals';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {FEATURE_PERMISSIONS, API_KEY_STATUS} from 'utils/globals';
import {IncludeComponent} from 'common-ui/components/v_search_component';
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import VAIApplicationApiKeys from 'components/applications/ai_applications/v_ai_application_api_keys';
import VAIApplicationApiKeysForm, {ai_application_api_keys_form_def} from 'components/applications/ai_applications/v_ai_application_api_key_form';

const moment = Utils.dateUtil.momentInstance();

@inject('aiApplicationApiKeyStore')
@observer
class CAIApplicationApiKeys extends Component {
  @observable _vState = {
    searchValue: '',
    apiKeyMasked: '',
    searchFilterValue: []
  }
  constructor(props){
    super(props);
    
    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.AI_API_KEYS.PROPERTY);
    this.form = createFSForm(ai_application_api_keys_form_def);
    this.appId = props.match.params.id;

    this.cApiKeys.params = {
      page: 0,
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
      sort: 'tokenExpiry,DESC',
      keyStatus: `${API_KEY_STATUS.ACTIVE.VALUE},${API_KEY_STATUS.DISABLED.VALUE},${API_KEY_STATUS.EXPIRED.VALUE}`
    }

    this.datePicker = createRef();
  }

  cApiKeys = f.initCollection();

  componentDidMount() {
    this.fetchApiKeys();
  }

  fetchApiKeys = async () => {
    try {
      f.beforeCollectionFetch(this.cApiKeys);
      let {models, pageState} = await this.props.aiApplicationApiKeyStore.getApiKey({
        params: this.cApiKeys.params,
        headers: {
          "x-app-id": this.appId, 
          "x-user-role": "OWNER",
          "x-tenant-id": UiState.getTenantId() 
        }
      });
      f.resetCollection(this.cApiKeys, models, pageState);
    } catch (e) {
      f.handleError(this.cApiKeys)(e);
    }
  }

  pageChange = () => {
    this.fetchApiKeys();
  }

  handleRefresh = () => {
    this.fetchApiKeys();
  }

  handleRevoke = (model) => {
    f._confirm.show({
      title: `Revoke API Key`,
      children: <Fragment>Are you sure you want to revoke <b>{model.apiKeyName}</b> API Key? <br /> This action cannot be reversed.</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Revoke',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
    .then((confirm) => {
      this.props.aiApplicationApiKeyStore.revokeApiKey(model.id,{
        models: this.cApiKeys
      })
      .then(() => {
        confirm.hide();
        f.notifySuccess('API Key Revoked Successfully');
        f.handlePagination(this.cApiKeys, this.cApiKeys.params);
        this.fetchApiKeys();
      }, f.handleError(null, null, {confirm}));
    }, () => {});
  }

  handleDelete = (model) => {
    f._confirm.show({
      title: `Delete API Key`,
      children: <Fragment>Are you sure you want to delete <b>{model.apiKeyName}</b> API Key?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
    .then((confirm) => {
      this.props.aiApplicationApiKeyStore.deleteApiKey(model.id,{
        models: this.cApiKeys
      })
      .then(() => {
        confirm.hide();
        f.notifySuccess('API Key Deleted Successfully');
        f.handlePagination(this.cApiKeys, this.cApiKeys.params);
        this.fetchApiKeys();
      }, f.handleError(null, null, {confirm}));
    }, () => {});
  }

  handleSave = async () => {
    await this.form.validate();
    const form = this.form;
    if (!form.valid) {
      return;
    }
    if (this.Modal) {
      this.Modal.setOkButtonTxt('Generating...');
      this.Modal.okBtnDisabled(true);
    }
    let data = form.toJSON();
    if (this.form.model) {
      data = Object.assign({}, this.form.model, data);
    }
    if (data.neverExpire) {
      data.tokenExpiry = moment().add(1, 'year').set({ hour: 0, minute: 0, second: 0 }).utc().toISOString();
    }
    delete data.neverExpire;
    data.applicationId = this.props._vState.application.id;
    data.userId = UiState.getLoggedInUser().id;
    data.addedById = UiState.getLoggedInUser().id;
    data.updatedById = UiState.getLoggedInUser().id;
    this.props.aiApplicationApiKeyStore.generateApiKey( data, {
      headers: {
        "x-app-id": this.props._vState.application.id, 
        "x-user-role": "OWNER",
        "x-tenant-id": UiState.getTenantId() 
      }
    })
    .then((response) => {
      this._vState.apiKeyMasked = response.apiKeyMasked;
      this.Modal.showHideOkButton(false);
      f.notifySuccess('API Key generated');
      this.fetchApiKeys();
    }, (error) => {
      if (this.Modal) {
        this.Modal.setOkButtonTxt("Generate Key");
      }
      f.handleError(null, null, {modal : this.Modal})(error);
    });
  }

  handleModalClose = () => {
    this._vState.apiKeyMasked = '';
    this.Modal?.hide?.();
  }

  handleCreate = () => {
    this.form.clearForm();
    this.Modal?.show?.({
      btnOkText: "Generate Key",
      title: 'Generate API Key'
    });
  }

  handleSorting = () => {
    this.fetchApiKeys();
  }

  handleSearchByField = (val) => {
    this.cApiKeys.params.page = undefined;
    let params = {
      apiKeyName: undefined,
      description: undefined
    };
    val && val.map(item => {
      let value = item.value.trim();
      switch (item.category) {
        case "Key Name":
          params.apiKeyName = value;
          break;
        case "Description":
          params.description = value;
          break
        default:
          params[item.category] = value;
      }
    })
    Object.assign(this.cApiKeys.params, params);
    this._vState.searchFilterValue = val;
    this.fetchApiKeys();
  }

  render () {
    const {_vState, permission, cApiKeys, pageChange, handleCreate, handleDelete, handleRevoke, handleSorting, handleSearchByField} = this;
    const {application} = this.props._vState;
    return (
      <Fragment>
        <Loader isLoading={this._vState.loading} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
          {
            application
            ? (
              <Box component={Paper} className={"m-t-sm m-b-sm"}>
                <Grid container spacing={3} style={{padding: '5px 15px'}}>
                  <Grid item xs={12} sm={12} md={8} data-testid="api-key-search">
                    <IncludeComponent
                      _vState={_vState}
                      noOperator={true}
                      categoriesOptions={[
                        { multi: false, category: "Key Name", type: "text" },
                        { multi: false, category: "Description", type: "text" }]}
                      onChange={handleSearchByField}
                    />
                  </Grid>
                  <AddButtonWithPermission
                    variant="contained"
                    permission={permission}
                    onClick={handleCreate}
                    label="Generate API Key"
                    colAttr={{xs: 12, sm: 12, md: 4}}
                    data-track-id="generate-api-key"
                    data-testid="generate-api-key"
                    style={{whiteSpace: 'nowrap'}}
                  />
                </Grid>
                <VAIApplicationApiKeys
                  data={cApiKeys}
                  permission={permission}
                  pageChange={pageChange}
                  handleDelete={handleDelete}
                  handleRevoke={handleRevoke}
                  handleSorting={handleSorting}
                />
                <FSModal ref={ref => this.Modal = ref} dataResolve={this.handleSave} reject={this.handleModalClose}>
                  <VAIApplicationApiKeysForm
                    form={this.form}
                    _vState={_vState}
                  />
                </FSModal>
              </Box>
              )
            : (
              <Grid containers spacing={3}>
                <Grid item xs={12}>
                  Application not found
                </Grid>
              </Grid>
            )  
          }
        </Loader>
      </Fragment>
    );
  }
}

export default withRouter(CAIApplicationApiKeys);
