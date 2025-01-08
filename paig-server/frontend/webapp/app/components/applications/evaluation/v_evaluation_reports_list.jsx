import React, { Component } from 'react';
import {observer, inject} from 'mobx-react';
import { TableCell, Checkbox, Button } from '@material-ui/core';
import DoneIcon from '@material-ui/icons/Done';
import ClearIcon from '@material-ui/icons/Clear';
import GroupIcon from '@material-ui/icons/Group';

import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';
import Table from 'common-ui/components/table';
import  {STATUS } from 'common-ui/utils/globals';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import UiState from 'data/ui_state';


@inject('evaluationStore')
@observer
class VEvaluationReportTable extends Component{
    constructor(props) {
        super(props);
        this.state = {
            expandedRows: []
        };
    }

  getHeaders = () => {
    const {permission, importExportUtil} = this.props;
    
    let headers = ([
      <TableCell key="1">App Name</TableCell>,
      <TableCell key="2">Start Time</TableCell>,
      <TableCell key="3">Purpose</TableCell>,
      //- <TableCell key="4">Application Client</TableCell>,
      <TableCell key="5">Owner</TableCell>,
      <TableCell key="6">Status</TableCell>,
      <TableCell key="7">Pass Rate</TableCell>,
      <TableCell width="100px" key="9">Actions</TableCell>
    ])

    return headers;
  }

  formatPercentage = (value) => {
    const formattedValue = value % 1 === 0 ? value.toFixed(0) : value.toFixed(2);
    return `${formattedValue}%`;
  }


  getResult = (model) => {
      let total = model.passed + model.failed
      let percentage = model.passed / (total);
      percentage = percentage  ? this.formatPercentage(percentage * 100) : 0;
      return (percentage + " (" + model.passed + "/" + total + ")")
  }

  getRowData = (model) => {
    const {handleDelete, handleEdit, handleView, permission, importExportUtil, handleInvite} = this.props;
    let rows = [
      <TableCell key="1">{model.application_name || "--"}</TableCell>,
      <TableCell key="2">{model.create_time || "--"}</TableCell>,
      <TableCell key="3">{model.purpose || "--"}</TableCell>,
      //- <TableCell key="4">{model.application_client || "--"}</TableCell>,
      <TableCell key="5">{model.owner || "--"}</TableCell>,
      <TableCell key="6">{model.status || "--"}</TableCell>,
      <TableCell key="7">{  this.getResult(model) || "--"}</TableCell>,
      <TableCell key="9" column="actions">
          <div className="d-flex">
            <ActionButtonsWithPermission
              permission={permission}
              showPreview={model.status == 'COMPLETED'}
              hideDelete={false}
              onDeleteClick={() => handleDelete(model)}
              onPreviewClick={() => handleView(model)}
            />
          </div>
        </TableCell>
    ]
    return rows;
  }
  handleContextMenuSelection = () => {}

  render() {
    const { data, pageChange, _vState } = this.props;
    console.log('data', data);
    return (
        <Table
            data={data}
            getHeaders={this.getHeaders}
            getRowData={this.getRowData}
            pageChange={pageChange}
        />
    )
}
}

export default VEvaluationReportTable;
