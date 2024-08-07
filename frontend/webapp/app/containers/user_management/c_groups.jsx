import React, {Component, Fragment} from 'react';
import {inject, observer} from 'mobx-react';
import { observable } from 'mobx';

import Grid from '@material-ui/core/Grid';

import f from 'common-ui/utils/f';
import FSModal from 'common-ui/lib/fs_modal';
import {DEFAULTS} from 'common-ui/utils/globals';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {AddButtonWithPermission} from "common-ui/components/action_buttons";
import { SearchField } from 'common-ui/components/filters';
import UiState from 'data/ui_state';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import VGroupForm, {group_form_def} from 'components/user_management/v_group_form';
import VGroups from 'components/user_management/v_groups';
import CGroupForm from 'containers/user_management/c_groups_form';
import ImportExportUtil from 'common-ui/utils/import_export_util';

@inject('groupStore')
@observer
class CGroups extends Component {
  @observable _vState = {
    defaultState: 0,
    searchValue: ''
  }
  constructor(props){
    super(props);
    
    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.ACCOUNT.GROUP.PROPERTY);
    this.form = createFSForm( group_form_def );

    this.cGroups.params = {
      page: 0,
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
      sort: "createTime,desc"
    }

    this.restoreState();
  }

  cGroups = f.initCollection();
  importExportUtil = new ImportExportUtil();

  componentDidMount() {
    this.fetchGroups();
  }

  restoreState() {
    let data = UiState.getStateData(this.props._vName)
    if(!data) {
      return;
    }
    if (data.params) {
      this.cGroups.params = data.params;
    }
    this._vState = data._vState || this._vState;
  }

  componentWillUnmount() {
    let {_vName, tabsState} = this.props;
    let {_vState} = this;
    let {params} = this.cGroups;
    let data = JSON.stringify({params, _vState});
    if (tabsState.clearStateOnUnmount) {
      data = "";
    }
    UiState.saveState(_vName, data);
  }

  fetchGroups = () => {
    f.beforeCollectionFetch(this.cGroups);
    this.props.groupStore.searchGroups({
        params: this.cGroups.params
    }).then(f.handleSuccess(this.cGroups, this._postFetch), f.handleError(this.cGroups));
  }

  _postFetch = res => {
    this.importExportUtil.setData(f.models(res));
  }

  pageChange = () => {
    this.fetchGroups();
  }

  handleRefresh = () => {
    this.fetchGroups();
  }

  handleDelete = (model) => {
    f._confirm.show({
      title: `Delete Group`,
      children: <Fragment>Are you sure you want to delete group: <b>{model.name}</b> ?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
    .then((confirm) => {
        this.props.groupStore.deleteGroup(model.id,{
            models: this.cGroups
        })
        .then(() => {
            confirm.hide();
            f.notifySuccess('Group Deleted');
            f.handlePagination(this.cGroups, this.cGroups.params);
            this.fetchGroups();
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
  
  handleSearch = (val) => {
    Object.assign(this.cGroups.params, {
      name: val || undefined,
      page: undefined
    });
    this.fetchGroups();
  }

  handleTabSelect = (key) => {
    this._vState.defaultState = key;
  }

  render () {
    const {permission, cGroups, handleSearch, pageChange, handleCreate, handleEdit, handleDelete, showPolicyViewModal, importExportUtil} = this;
    return (
      <Fragment>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={10}>
            <SearchField
              value={this._vState.searchValue}
              colAttr={{xs: 12, sm: 10, md: 6, lg: 6, 'data-track-id': 'search-group'}}
              placeholder="Search group"
              onChange={(e, val) => this._vState.searchValue = val}
              onEnter={handleSearch}
            />
          </Grid>
          <AddButtonWithPermission
            variant="contained"
            permission={permission}
            onClick={handleCreate}
            label="Add Group"
            colAttr={{
              xs: 12,
              sm: 2
            }}
            data-track-id="add-group"
            style={{whiteSpace: 'nowrap'}}
          />
        </Grid>
        <VGroups
          data={cGroups}
          pageChange={pageChange}
          handleDelete={handleDelete}
          handleEdit={handleEdit}
          showPolicyViewModal={showPolicyViewModal}
          permission={permission}
          importExportUtil={importExportUtil}
        />
        <CGroupForm
          ref={ref => this.modalForm = ref}
          postCreate={this.fetchGroups}
          postUpdate={this.fetchGroups}
        />
      </Fragment>
    );
  }
}

CGroups.defaultProps = {
  vName: 'c_groups'
};

export default CGroups;