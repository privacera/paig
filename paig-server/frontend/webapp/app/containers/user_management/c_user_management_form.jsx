import React, {Component, Fragment} from 'react';
import {action, observable} from 'mobx';
import {inject, observer} from 'mobx-react';

import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Chip from '@material-ui/core/Chip';
import GroupIcon from '@material-ui/icons/Group';
import Typography from '@material-ui/core/Typography';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import FSModal from 'common-ui/lib/fs_modal';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {TabPanel} from 'common-ui/components/generic_components';
import UiState from 'data/ui_state';
import {user_form_def} from 'components/user_management/user_form_def';
import VUserManagementForm from 'components/user_management/v_user_management_form'
import {FEATURE_PERMISSIONS} from 'utils/globals';
import VUserGroupsAssociation from 'components/user_management/v_user_group_association';
import {importExportByAttrUtil} from 'common-ui/utils/import_export_util';

@inject('userStore', 'groupStore')
@observer
class CUserManagementForm extends Component {
    @observable _vState = {
		defaultState: 0,
    searchValue: '',
    addedGroups: [],
    removedGroups: [],
    preSelectedGroups: [],
    showGroupsListing: false
	}
  @observable isReadOnly = false;
  @observable isEditMode = false;
    constructor(props){
    super(props);

    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.ACCOUNT.USER.PROPERTY);
    this.form = createFSForm(user_form_def);

    this.cGroups.params = {
      page: 0,
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
      sort: "createTime,desc"
    }
  }
  
  cGroups = f.initCollection();
  importExportUtil = new importExportByAttrUtil('name');

  fetch = () => {
    f.beforeCollectionFetch(this.cGroups);
    this.props.groupStore.searchGroups({
      params: this.cGroups.params
    }).then(f.handleSuccess(this.cGroups, this._postFetch), f.handleError(this.cGroups));
  }

  _postFetch = () => {
    this.importExportUtil.setData(f.models(this.cGroups));
  }

  pageChange = () => {
    this.fetch();
  }

  handleRefresh = () => {
    this.fetch();
  }

  handleCreate = () => {
    this.resetState();
    this.form.clearForm();
    this.Modal?.show({
      title: 'Create User'
    });
    this.fetch();
  }

  handleEdit = (model) => {
    this.resetState();
    this.form.model = model;
    this._vState.preSelectedGroups = model.groups || [];
    this._vState.showGroupsListing = this._vState.preSelectedGroups.length == 0;
    model.groups?.forEach((group) => {
      this.importExportUtil.checked(true, group, false);
    })
    this.fetch();
    this.form.clearForm();
    this.form.refresh(model);
    this.isEditMode = true;
    this.Modal?.show({
      title: `Edit User: ${model.firstName}`,
      btnOkText: 'Proceed',
      showOkButton: true
    });
  }

  showPolicyViewModal = (model) => {
    this.resetState();
    this.form.model = model;
    this._vState.preSelectedGroups = model.groups || [];
    model.groups?.forEach((group) => {
      this.importExportUtil.checked(true, group, false);
    })    
    this.fetch();    
    this.form.clearForm();
    this.form.refresh(model);
    this.isReadOnly = true;
    this.Modal?.show({
      title: `User: ${model.firstName}`,
      showOkButton: false
    });
  }

  @action
  resetState = () => {
    Object.assign(this._vState, {
      defaultState: 0,
      searchValue: ''
    });
    delete this.cGroups.params.name;
    delete this.cGroups.params.page;
  }
  
  getAddedGroups = (selectedData) => {
    return selectedData.filter((current) => {
      return !this._vState.preSelectedGroups.includes(current);
    });
  }

  getRemovedGroups = (selectedData) => {
    return this._vState.preSelectedGroups.filter((current) => {
      return !selectedData.includes(current);
    });
  }

  @action
  validate = async () => {
    await this.form.validate();
    this._vState.defaultState = this.form.valid ? this._vState.defaultState : 0;
    return this.form.valid;
  }

  handleSave = async () => {
    const isValid = await this.validate();
    if (!isValid) {
      return;
    }
    let data = this.form.toJSON();
    data.roles = Array.isArray(data.roles) ? data.roles : [data.roles];

    //Set userInvited to false if email is not present
    if (!data.email) {
      data.userInvited = false;
    }
    if (data.username) {
      data.username = data.username.toLowerCase();
    }
    let importeExportData = this.importExportUtil.getSelectIdList();
    this._vState.addedGroups = this.getAddedGroups(importeExportData);
    this._vState.removedGroups = this.getRemovedGroups(importeExportData);

    data.groups = importeExportData;

    if (this.Modal) {
      this.Modal.okBtnDisabled(true);
    }
    if (!data.id) {
      this.props.userStore.createUser(data).then(() => {
        f.notifySuccess(`User "${data.firstName}" created successfully`);
        this.Modal?.hide?.(); 
        this.props.postCreate?.();
        this.importExportUtil.reset();
        this._vState.preSelectedGroups = []
      }, f.handleError(null, null, {modal: this.Modal}));
    } else {
      this.Modal?.hide?.();
      this.confirmChangesModal();
    }
  }
  
  confirmChangesModal = () => {
    this.ConfirmModal?.show?.({
      title: 'Confirm Changes',
      btnCancelText: 'Back'
    });
  }

  handleProceedSave = async () => {
    await this.form.validate();
    const form = this.form;
    if (!form.valid) {
      return;
    }
    let data = form.toJSON();

    const wasAlreadyInvited = data.userInvited;
    //Set userInvited to true if email is present during edit
    if (data.email) {
      data.userInvited = true;
    }

    let importeExportData = this.importExportUtil.getSelectIdList();
    data.groups = importeExportData;
    data.roles = Array.isArray(data.roles) ? data.roles : [data.roles];
    if (this.ConfirmModal) {
      this.ConfirmModal.okBtnDisabled(true);
    }
    this.props.userStore.saveUser(data).then(() => {
      f.notifySuccess(`User "${data.firstName}" updated successfully`);
      if (!wasAlreadyInvited && data.userInvited) {
        f.notifySuccess(`User "${data.firstName}" invited successfully`);
      }
      this.ConfirmModal?.hide?.();
      this.props.postUpdate?.();
      this.importExportUtil.reset();
      this._vState.preSelectedGroups = []
    }, f.handleError(null, null, {modal: this.ConfirmModal}))
  }

  handleSearch = (val) => {
    Object.assign(this.cGroups.params, {
      name: val || undefined,
      page: undefined
    });
    this.fetch();
  }

  handleTabSelect = (key) => {
    this._vState.defaultState = key;
  }

  handleModalClose = () => {
    this.isReadOnly = false;
    this.isEditMode = false;
    this.importExportUtil.reset();
    this._vState.preSelectedGroups = [];
    this._vState.addedGroups = [];
    this._vState.removedGroups = [];
    this._vState.showGroupsListing = false;
    this.Modal?.hide?.();
  }
  
  handleConfirmModalClose = () => {
    this._vState.showGroupsListing = this._vState.addedGroups.length > 0 || this._vState.removedGroups.length > 0;
    this.ConfirmModal?.hide?.(); 
    this.Modal?.show({
      title: `Edit User: ${this.form?.model?.firstName}`,
      btnOkText: 'Proceed',
      showOkButton: !(UiState.user && UiState.user.id == this.form?.model?.id)
    });
  }

  render () {
    const {_vState, handleTabSelect, permission, cGroups, pageChange, handleSearch, importExportUtil} = this;
    return (
      <Fragment>
        <FSModal ref={ref => this.Modal = ref} maxWidth="lg" dataResolve={this.handleSave} reject={this.handleModalClose}>
          <Tabs className="tabs-view" aria-label="user-management-tabs" value={_vState.defaultState} >
            <Tab
              label="INFO"
              onClick={() => handleTabSelect(0)}
              data-testid="info-tab"
            />
            <Tab
              label="GROUPS"
              onClick={() => handleTabSelect(1)}
              data-testid="groups-tab"
            />
          </Tabs>
          <Fragment>
            <TabPanel value={_vState.defaultState} index={0} p={0} mt="10px">
              <VUserManagementForm form={this.form} readOnly={this.isReadOnly}/>
            </TabPanel>
            <TabPanel value={_vState.defaultState} index={1} p={0} mt="10px">
              <VUserGroupsAssociation
                _vState={_vState}
                data={cGroups}
                pageChange={pageChange}
                permission={permission}
                handleSearch={handleSearch}
                readOnly={this.isReadOnly}
                isEditMode={this.isEditMode}
                importExportUtil={importExportUtil}
              />
            </TabPanel>
          </Fragment>
        </FSModal>
        <FSModal 
          ref={ref => this.ConfirmModal = ref} 
          maxWidth={this._vState.addedGroups.length > 0 || this._vState.removedGroups.length > 0 ? "lg" : "sm"} 
          dataResolve={this.handleProceedSave}
          reject={this.handleConfirmModalClose}
          data-testid="confirm-modal"
        >
          <div className='m-b-lg'>
            <div className='m-b-lg m-t-sm' data-testid="confirm-modal-message">
              Are you sure you want to update the user <strong>{this.form?.model?.firstName}</strong>
            </div>
            {
              this._vState.addedGroups.length > 0 && 
              <div className='m-b-lg' data-testid="added-groups-section">
                <Typography className='m-b-md' variant="subtitle1">
                  Groups to be <span className="text-success">Added</span>
                </Typography>
                {this._vState.addedGroups.map(group => (
                  <Chip 
                    key={group}
                    size='small'
                    className="m-r-xs m-t-xs" 
                    icon={<GroupIcon fontSize='small'/>}
                    label={group}
                  />
                ))}
              </div>
            }
            {
              this._vState.removedGroups.length > 0 && 
              <div className='m-b-lg' data-testid="removed-groups-section">
                <Typography className='m-b-md' variant="subtitle1">
                  Groups to be <span className="text-danger">Removed</span>
                </Typography>
                {this._vState.removedGroups.map(group => (
                  <Chip 
                    key={group}
                    size='small'
                    className="m-r-xs m-t-xs" 
                    icon={<GroupIcon fontSize='small'/>}
                    label={group}
                  />
                ))}
              </div>
            }
            </div>
        </FSModal>
      </Fragment>
    );
  }
}

CUserManagementForm.defaultProps = {
  vName: 'c_user_management_form'
};

export default CUserManagementForm;