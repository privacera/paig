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
// import {user_form_def} from 'components/user_management/user_form_def';
import VGroupForm, {group_form_def} from 'components/user_management/v_group_form';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import VGroupsUsersAssociation from 'components/user_management/v_group_user_association';
import {importExportByAttrUtil} from 'common-ui/utils/import_export_util';

@inject('userStore', 'groupStore')
@observer
class CGroupForm extends Component {
  @observable _vState = {
		defaultState: 0,
    searchValue: '',
    addedUsers: new Set(),
    removedUsers: new Set(),
    selectedGroup: null
	}
  @observable isReadOnly = false;
  constructor(props){
    super(props);

    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.ACCOUNT.USER.PROPERTY);
    this.form = createFSForm(group_form_def);

    this.cUsers.params = {
      page: 0,
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
      sort: "createTime,desc"
    }
  }

  cUsers = f.initCollection();
  importExportUtil = new importExportByAttrUtil('username');

  fetch = () => {
    f.beforeCollectionFetch(this.cUsers);
    this.props.userStore.getAllUsers({
      params: this.cUsers.params
    }).then(f.handleSuccess(this.cUsers, this._postFetch), f.handleError(this.cUsers));
  }

  isCheckboxSelected = (model) => {
    const {_vState} = this;
    if (_vState.removedUsers.has(model.username)) {
      return false;
    } else if (_vState.addedUsers.has(model.username) || model.groups.includes(_vState.selectedGroup?.name)) {
      return true;
    }
    return false;
  }

  _postFetch = coll => {
    this.importExportUtil.setData(f.models(coll));

    f.models(coll).forEach(model => {
      const isSelected = this.isCheckboxSelected(model);
      if (isSelected) {
        this.importExportUtil.checked(isSelected, model.username, false);
      } else {
        this.importExportUtil.unChecked(isSelected, model.username, false);
      }
    });
  };

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
      title: 'Create Group'
    });
    this.fetch();
  }

  handleEdit = (model) => {
    this.resetState();
    this.form.model = model;
    this._vState.selectedGroup = model;
    this.fetch();
    this.form.clearForm();
    this.form.refresh(model);
    this.Modal?.show({
      title: `Edit Group: ${model.name}`,
      btnOkText: 'Proceed',
      showOkButton:  model.id
    });
  }

  showPolicyViewModal = (model) => {
    this.resetState();
    this.form.model = model;
    this._vState.selectedGroup = model;
    this.isReadOnly = true;
    this.fetch();
    this.form.clearForm();
    this.form.refresh(model);
    this.Modal?.show({
      title: `Group: ${model.name}`,
      btnOkText: 'Proceed',
      showOkButton: false
    });
  }

  @action
  resetState = () => {
    Object.assign(this._vState, {
      defaultState: 0,
      searchValue: ''
    });
    delete this.cUsers.params.username;
    delete this.cUsers.params.page;
  }

  resetVState = () => {
    this.importExportUtil.reset();
    this._vState.selectedGroup = null
    this._vState.addedUsers.clear();
    this._vState.removedUsers.clear();
  }

  handleSave = async () => {
    await this.form.validate();
    const form = this.form;
    if (!form.valid) {
      return;
    }
    let data = form.toJSON();
    data.delUsers = Array.from(this._vState.removedUsers);
    data.addUsers = Array.from(this._vState.addedUsers);
    data.groupName = data.name;
    if (this.form.model) {
      data = Object.assign({}, this.form.model, data);
    }
    if (this.Modal) {
      this.Modal.okBtnDisabled(true);
    }
    if (data.id) {
      this.Modal?.hide?.();
      this.confirmChangesModal();
    } else {
      this.props.groupStore.createGroup(data)
      .then(() => {
        f.notifySuccess(`Group "${data.name}" created successfully`);
        this.Modal?.hide?.();
        this.props.postCreate?.();
        this.resetVState();
        return;
      }, f.handleError(null, null, {modal: this.Modal}));
    }
  }

  confirmChangesModal = () => {
    this.ConfirmModal?.show?.({
      title: 'Confirm Changes',
      btnCancelText: 'Back'
    });
  }

  handleProceedSave = async () => {
    try {
      await this.form.validate();
      const form = this.form;
      if (!form.valid) {
        return;
      }
      let data = form.toJSON();
      data.delUsers = Array.from(this._vState.removedUsers);
      data.addUsers = Array.from(this._vState.addedUsers);
      data.groupName = data.name;    
      if (this.form.model) {
        data = Object.assign({}, this.form.model, data);
      } 
      if (this.ConfirmModal) {
        this.ConfirmModal.okBtnDisabled(true);
      }
      await this.props.groupStore.updateGroupForm(data);
      await this.props.groupStore.updateGroupUsers(data); 
      f.notifySuccess(`Group "${data.name}" updated successfully`);
      this.ConfirmModal?.hide?.();
      this.props.postUpdate?.();
      this.resetVState();
    } catch (e) {
      f.handleError(null, null, {modal: this.ConfirmModal})(e);    
    }
  };

  handleSearch = (val) => {
    Object.assign(this.cUsers.params, {
      username: val || undefined,
      page: undefined
    });
    this.fetch();
  }

  handleTabSelect = (key) => {
    this._vState.defaultState = key;
  }

  handleModalClose = () => {
    this.isReadOnly = false;
    this.resetVState();
    this.Modal?.hide?.();
  }

  handleConfirmModalClose = () => {
    this.ConfirmModal?.hide?.();
    this.Modal?.show({
      title: `Edit Group: ${this.form?.model?.name}`,
      btnOkText: 'Proceed',
      showOkButton: !(UiState.user && UiState.user.id == this.form?.model?.id)
    });
  }

  render () {
    const {_vState, handleTabSelect, permission, cUsers, pageChange, handleSearch, importExportUtil} = this;

    return (
        <Fragment>
          <FSModal ref={ref => this.Modal = ref} maxWidth="lg" dataResolve={this.handleSave} reject={this.handleModalClose}>
            <Tabs className="tabs-view" aria-label="user-management-tabs" value={_vState.defaultState} >
              <Tab
                label="INFO"
                onClick={() => handleTabSelect(0)}
                data-testid="info-tab"
              />
              {this.form.fields.id.value && 
                <Tab
                  label="USERS"
                  onClick={() => handleTabSelect(1)}
                  data-testid="users-tab"
                />
              }
            </Tabs>
            <Fragment>
              <TabPanel value={_vState.defaultState} index={0} p={0} mt="10px">
                <VGroupForm form={this.form} readOnly={this.isReadOnly}/>
              </TabPanel>
              <TabPanel value={_vState.defaultState} index={1} p={0} mt="10px">
                <VGroupsUsersAssociation
                  importExportUtil={importExportUtil}
                  _vState={_vState}
                  data={cUsers}
                  pageChange={pageChange}
                  permission={permission}
                  handleSearch={handleSearch}
                  readOnly={this.isReadOnly}
                />
              </TabPanel>
            </Fragment>
          </FSModal>
          <FSModal 
            ref={ref => this.ConfirmModal = ref} 
            maxWidth={this._vState.addedUsers.size > 0 || this._vState.removedUsers.size > 0 ? "lg" : "sm"}             
            dataResolve={this.handleProceedSave}   
            reject={this.handleConfirmModalClose}
            data-testid="confirm-modal"
          >
            <div className='m-b-lg'>
              <div className='m-b-lg m-t-sm' data-testid="confirm-modal-message">
                Are you sure you want to update the group <strong>{this.form.model?.name}</strong>
              </div>
              {
                this._vState.addedUsers.size > 0 && 
                <div className='m-b-lg' data-testid="added-users-section">
                  <Typography className='m-b-md' variant="subtitle1">
                    Users to be <span className="text-success">Added</span>
                  </Typography>
                  {Array.from(this._vState.addedUsers).map(user => (
                    <Chip 
                      key={user}
                      size='small'
                      className="m-r-xs m-t-xs" 
                      icon={<GroupIcon fontSize='small'/>}
                      label={user}
                    />
                  ))}
                </div>
              }
              {
                this._vState.removedUsers.size > 0 && 
                <div className='m-b-lg' data-testid="removed-users-section">
                  <Typography className='m-b-md' variant="subtitle1">
                    Users to be <span className="text-danger">Removed</span>
                  </Typography>
                  {Array.from(this._vState.removedUsers).map(user => (
                    <Chip 
                      key={user}
                      size='small'
                      className="m-r-xs m-t-xs" 
                      icon={<GroupIcon fontSize='small'/>}
                      label={user}
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

CGroupForm.defaultProps = {
  vName: 'c_groups_form'
};

export default CGroupForm;