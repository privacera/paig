import React, { Component } from 'react';

import { TableCell, Checkbox, Button } from '@material-ui/core';
import DoneIcon from '@material-ui/icons/Done';
import ClearIcon from '@material-ui/icons/Clear';
import GroupIcon from '@material-ui/icons/Group';

import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';
import Table from 'common-ui/components/table';
import  {STATUS } from 'common-ui/utils/globals';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import UiState from 'data/ui_state';

class VUserManagement extends Component{

  getHeaders = () => {
    const {permission, importExportUtil} = this.props;
    
    let headers = ([
      // <TableCell column="select" key="select-all" className='p-xxs'>
      //   <Checkbox 
      //     color='primary'
      //     checked={importExportUtil.data.length ? importExportUtil.isAllChecked : false}
      //     disabled={!importExportUtil.data.length}
      //     onChange={(e) => {importExportUtil.checkboxClick(e, "", true);}}
      //     />
      // </TableCell>,
      <TableCell key="1" className="table-search-156">User Name</TableCell>,
      <TableCell key="2" width="120px">First Name</TableCell>,
      <TableCell key="3" width="120px">Last Name</TableCell>,
      <TableCell key="4" >Groups</TableCell>,
      <TableCell key="5" className="table-search-156">Email</TableCell>,
      <TableCell key="6" >Roles</TableCell>,
      <TableCell key="7" className="text-center">Invite Status</TableCell>,
      <TableCell key="8" className="text-center">Enabled</TableCell>
    ])

    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      headers.push(<TableCell width="100px" key="9">Actions</TableCell>);
    }

    return headers;
  }

  getRowData = (model) => {
    const {handleDelete, handleEdit, showPolicyViewModal, permission, importExportUtil, handleInvite} = this.props;
    let roleNamesArr = Array.isArray(model.roles) ? model.roles : []; 
    let rows = [
      // <TableCell column="select" key="select-all" className='p-xxs'>
      //   <Checkbox 
      //     color='primary'
      //     data-test="select-all"
      //     checked={importExportUtil.isSelected(model.id)}
      //     disabled={!importExportUtil.data.length}
      //     onChange={(e) => importExportUtil.checkboxClick(e, model.id)}
      //   />
      // </TableCell>,
      <TableCell key="1">{model.username || "--"}</TableCell>,
      <TableCell key="2">{model.firstName || "--"}</TableCell>,
      <TableCell key="3">{model.lastName || "--"}</TableCell>,
      <TableCell key="4">
        <GroupIcon fontSize="small" color="action" /> {model.groups?.length || 0}
      </TableCell>,
      <TableCell key="5">{model.email || "--"}</TableCell>,
      <TableCell key="6">{roleNamesArr.join(", ") || "--"}</TableCell>,
      <TableCell key="7" className="text-center">
        {
          model.userInvited 
          ? <DoneIcon data-testid="user-invited" className="text-success" /> 
          : (
              permissionCheckerUtil.checkHasUpdatePermission(permission) 
              ? <Button data-testid="user-invite-btn" variant="outlined" color="primary" onClick={() => handleInvite(model)}>Invite</Button>
              : <ClearIcon data-testid="user-not-invited" color="secondary"/>  
            )
        }
      </TableCell>,    
      <TableCell key="8" className="text-center">
        {
          model.status == STATUS.enabled.value
          ? <DoneIcon data-testid="account-enabled" className="text-success" />
          : <ClearIcon data-testid="account-disabled" color="secondary" />
        }
      </TableCell>
    ]

    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      rows.push(
        <TableCell key="9" column="actions">
          <div className="d-flex">
            <ActionButtonsWithPermission
              permission={permission}
              showPreview={true}
              hideDelete={UiState.user.username === model.username}
              onEditClick={() => handleEdit(model)}
              onDeleteClick={() => handleDelete(model)}
              onPreviewClick={() => showPolicyViewModal(model)}
            />
          </div>
        </TableCell>
      );
    }

    return rows;
  }

  render(){
    const { pageChange, data} = this.props;

    return (
      <Table
        data={data}
        getHeaders={this.getHeaders}
        getRowData={this.getRowData}
        pageChange={pageChange}
        hasElevation={false}
      />
    );
  }
}

export default VUserManagement;
