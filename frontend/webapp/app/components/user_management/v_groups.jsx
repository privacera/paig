import React, { Component } from 'react';

import { TableCell, Checkbox } from '@material-ui/core';
import PersonIcon from '@material-ui/icons/Person';

import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';
import Table from 'common-ui/components/table';
import {Utils} from 'common-ui/utils/utils';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';

class VGroup extends Component{

  getHeaders = () => {
    const {permission, importExportUtil} = this.props;

    let headers = ([
      // <TableCell key="1" className='p-xxs'>
      //   <Checkbox 
      //     color='primary'
      //     checked={importExportUtil.data.length ? importExportUtil.isAllChecked : false}
      //     disabled={!importExportUtil.data.length}
      //     onChange={(e) => {importExportUtil.checkboxClick(e, "", true);}}
      //   />
      // </TableCell>,
      <TableCell key="2" className="table-search-156">Group Name</TableCell>,
      <TableCell key="3" className="table-search-156">Description</TableCell>,
      <TableCell key="4" className="table-search-156">Users</TableCell>,
      <TableCell key="5" className="table-search-156">Created</TableCell>
    ])

    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      headers.push(<TableCell width="100px" key="8">Actions</TableCell>);
    }

    return headers;
  }

  getRowData = (model, idx) => {
    const {handleDelete, handleEdit, showPolicyViewModal, permission, importExportUtil} = this.props;

    let rows = [
      // <TableCell key="1" className='p-xxs'>
      //   <Checkbox 
      //     color='primary'
      //     data-test="select-all"
      //     checked={importExportUtil.isSelected(model.id)}
      //     disabled={!importExportUtil.data.length}
      //     onChange={(e) => importExportUtil.checkboxClick(e, model.id)}
      //   />
      // </TableCell>,
      <TableCell key="2">{model.name || "--"}</TableCell>,
      <TableCell key="3">{model.description || "--"}</TableCell>,
      <TableCell key="4">
        <PersonIcon fontSize="small" color="action" /> {model.usersCount || 0}
      </TableCell>,
      <TableCell key="5">{model.createTime ? Utils.dateUtil.getTimeZone(model.createTime, DATE_TIME_FORMATS.DATE_FORMAT) : "--"}</TableCell>
    ]

    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      rows.push(
        <TableCell key="8" column="actions" width='120px'>
          <div className="d-flex">
            <ActionButtonsWithPermission
              permission={permission}
              showPreview={true}
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

export default VGroup;
