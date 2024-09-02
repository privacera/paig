import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import { observable } from 'mobx';

import Grid from '@material-ui/core/Grid';

import f from 'common-ui/utils/f';
import {DEFAULTS} from 'common-ui/utils/globals';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {AddButtonWithPermission} from "common-ui/components/action_buttons";
import { IncludeComponent } from 'common-ui/components/v_search_component';
import UiState from 'data/ui_state';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import VUserManagement from 'components/user_management/v_user_management'
import CUserManagementForm from './c_user_management_form';
import ImportExportUtil from 'common-ui/utils/import_export_util';

@inject('userStore')
class CUserManagement extends Component {
  @observable _vState = {
    selectedGroups: {},
    searchFilterValue: []
  }
  constructor(props){
    super(props);

    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.ACCOUNT.USER.PROPERTY);

    this.cUsers.params = {
      page: 0,
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
      sort: "createTime,desc"
    }

    this.restoreState();
  }

  cUsers = f.initCollection();
  importExportUtil = new ImportExportUtil();

  componentDidMount() {
    this.fetchUsers();
  }

  restoreState() {
    let data = UiState.getStateData(this.props._vName)
    if(!data || !data.params) {
      return;
    }
    Object.assign(this, {
      _vState: data._vState
    });
    this.cUsers.params = data.params;
  }

  componentWillUnmount() {
    let {_vState} = this;
    let {_vName, tabsState} = this.props;
    let {params} = this.cUsers;
    let data = JSON.stringify({params, _vState});
    if (tabsState.clearStateOnUnmount) {
      data = "";
    }
    UiState.saveState(_vName, data);
  }

  fetchUsers = () => {
    f.beforeCollectionFetch(this.cUsers);
    this.props.userStore.getAllUsers({
      params: this.cUsers.params
    }).then(f.handleSuccess(this.cUsers, this._postFetch), f.handleError(this.cUsers));
  }

  _postFetch = res => {
    this.importExportUtil.setData(f.models(res));
  }

  pageChange = () => {
    this.fetchUsers();
  }

  handleRefresh = () => {
    this.fetchUsers();
  }

  handleDelete = (userModel) => {
    f._confirm.show({
      title: `Delete User`,
      children: <Fragment>Are you sure you want to delete user: <b>{userModel.username}</b> ?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
    .then((confirm) => {
      this.props.userStore.deleteUser(userModel.id,{
        models: this.cUsers
      })
      .then(() => {
          confirm.hide();
          f.notifySuccess('User Deleted');
          f.handlePagination(this.cUsers, this.cUsers.params);
          this.fetchUsers();
      }, f.handleError(null, null, {confirm}));
    }, () => {});
  }

  handleCreate = () => {
    this.modalForm?.handleCreate?.();
  }

  handleEdit = (obj) => {
    this.modalForm?.handleEdit?.(obj);
  }

  showPolicyViewModal = (obj) => {
    this.modalForm?.showPolicyViewModal?.(obj);
  }

  handleSearchByField = (val) => {
    this.cUsers.params.page = undefined;
    let params = {
      username: undefined,
      firstName: undefined,
      lastName: undefined,
      email: undefined,
      roles : undefined
    };
    val && val.map(item => {
      let value = item.value.trim();
      switch (item.category) {
        case "User Name":
          params.username = value;
          break;
        case "First Name":
          params.firstName = value;
          break;
        case "Last Name":
          params.lastName = value;
          break;
        case "Email":
          params.email = value;
          break;
        case "Roles":
          params.roles = value;
          break;
        default:
          params[item.category] = value;
      }
    })
    Object.assign(this.cUsers.params, params);
    this._vState.searchFilterValue = val;
    this.fetchUsers();
  }

  handleInvite = (model) => {
    if (!model.email) {
      return f.notifyWarning("Please update email field in user information to send invite");
    } 
    f._confirm.show({
      title: `Invite User`,
      children: <Fragment>Are you sure you want to invite user: <b>{model.username}</b> ?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Invite',
      btnOkColor: 'primary',
      btnOkVariant: 'contained'
    })
    .then((confirm) => {
      model.userInvited = true;
      this.props.userStore.saveUser(model)
      .then(() => {
          confirm.hide();
          f.notifySuccess(`User "${model.firstName}" invited successfully`);
          this.fetchUsers();
      }, f.handleError(null, null, {confirm}));
    }, () => {});
  }

  render () {
    const {_vState, permission, cUsers, pageChange, handleSearchByField, handleCreate, handleEdit, handleDelete, showPolicyViewModal, handleInvite, importExportUtil} = this;    
    return (
      <Fragment>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={10} data-track-id="user-management-search">
            <IncludeComponent
              _vState={_vState}
              noOperator={true}
              categoriesOptions={[
                { multi: false, category: "User Name", type: "text" },
                { multi: false, category: "First Name", type: "text" },
                { multi: false, category: "Last Name", type: "text" },
                { multi: false, category: "Email", type: "text" },
                // { multi: false, category: "Roles", type: "text", options: () => Object.keys(ROLES)}
              ]}
              onChange={handleSearchByField}
            />
          </Grid>
          <AddButtonWithPermission
            variant="contained"
            permission={permission}
            onClick={handleCreate}
            label="Add User"
            colAttr={{
              xs: 12,
              sm: 2
            }}
            data-track-id="add-user"
            style={{whiteSpace: 'nowrap'}}
          />
        </Grid>
        <VUserManagement
          data={cUsers}
          pageChange={pageChange}
          handleDelete={handleDelete}
          handleEdit={handleEdit}
          showPolicyViewModal={showPolicyViewModal}
          permission={permission}
          importExportUtil={importExportUtil}
          handleInvite={handleInvite}
        />
        <CUserManagementForm
          ref={ref => this.modalForm = ref}
          postCreate={this.fetchUsers}
          postUpdate={this.fetchUsers}
          selectedGroups={this._vState.selectedGroups}
          importExportUtil={importExportUtil}
        />
      </Fragment>
    );
  }
}

CUserManagement.defaultProps = {
  vName: 'c_user_management'
};

export default CUserManagement;