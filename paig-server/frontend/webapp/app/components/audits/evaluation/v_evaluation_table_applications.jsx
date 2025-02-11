import React, { Component, Fragment, useRef } from 'react';
import {observer, inject} from 'mobx-react';
import { TableCell, Checkbox, Button, Snackbar } from '@material-ui/core';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';
import Table from 'common-ui/components/table';
import  {STATUS } from 'common-ui/utils/globals';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import UiState from 'data/ui_state';

import PlayCircleOutlineIcon from '@material-ui/icons/PlayCircleOutline';

@inject('evaluationStore')
@observer
class VEvaluationAppsTable extends Component{
  constructor(props) {
    super(props);
    this.state = {
      selectedRows: [],
      showAlert: false
    };
  }

  handleSelectRow = (id) => {
    this.setState((prevState) => {
      let selectedRows = [...prevState.selectedRows];
      
      if (selectedRows.includes(id)) {
        selectedRows = selectedRows.filter(rowId => rowId !== id);
      } else if (selectedRows.length < 2) {
        selectedRows.push(id);
      } else {
        return { showAlert: true };
      }
      
      if (this.props.onSelectionChange) {
        this.props.onSelectionChange(selectedRows);
      }
      
      return { selectedRows };
    });
  }
  
  handleCloseAlert = () => {
    this.setState({ showAlert: false });
  }

  getHeaders = () => {
    const {permission, importExportUtil} = this.props;
    
    let headers = ([
      <TableCell key="1">Select</TableCell>,
      <TableCell key="2">Name</TableCell>,
      <TableCell key="3">Details</TableCell>,
      <TableCell width="100px" key="9">Actions</TableCell>
    ])

    return headers;
  }

  getRowData = (model) => {
    const {handleDelete, handleEdit, permission, importExportUtil} = this.props;
    
    let rows = [
      <TableCell column="select" key="1" className='p-xxs'>
        <Checkbox 
          color='primary'
          data-test="select-all"
          checked={this.state.selectedRows.includes(model.id)}
          onChange={() => this.handleSelectRow(model.id)}
          disabled={!model.target_id}
        />
      </TableCell>,
      <TableCell key="2">{model.name || "--"}</TableCell>,
      <TableCell key="3">{model.url || "--"}</TableCell>,
      <TableCell key="9" column="actions">
          <div className="d-flex">
            <ActionButtonsWithPermission
              permission={permission}
              hideEdit={false}
              hideDelete={false}
              onDeleteClick={() => handleDelete(model)}
              onEditClick={() => handleEdit(model)}
            />
          </div>
        </TableCell>
    ]
    return rows;
  }
  handleContextMenuSelection = () => {}

  render() {
    const { data, pageChange, _vState } = this.props;
    return (
      <>
        <Table
          data={data}
          getHeaders={this.getHeaders}
          getRowData={this.getRowData}
          pageChange={pageChange}
        />
        <Snackbar
          open={this.state.showAlert}
          autoHideDuration={3000}
          onClose={this.handleCloseAlert}
          message="Only 2 selections allowed"
        />
      </>
    )
}
}

export default VEvaluationAppsTable;
