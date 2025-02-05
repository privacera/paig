import React, { Component, Fragment } from 'react';
import {observer, inject} from 'mobx-react';
import { TableCell, Checkbox, Button } from '@material-ui/core';
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
class VEvaluationConfigTable extends Component{
    constructor(props) {
        super(props);
        this.state = {
            expandedRows: []
        };
    }

  getHeaders = () => {
    const {permission, importExportUtil} = this.props;
    
    let headers = ([
      <TableCell key="1">Name</TableCell>,
      <TableCell key="2">Applications</TableCell>,
      <TableCell key="3">Evaluation Purpose</TableCell>,
      //- <TableCell key="4">Application Client</TableCell>,
      <TableCell key="5">Created</TableCell>,
      <TableCell key="6">Created By</TableCell>,
      <TableCell key="7">Runs</TableCell>,
      <TableCell width="100px" key="9">Actions</TableCell>
    ])

    return headers;
  }

  getRowData = (model) => {
    const {handleDelete, handleRun, handleEdit, permission} = this.props;
    let rows = [
      <TableCell key="1">{model.name}</TableCell>,
      <TableCell key="2">{model.application_names || "--"}</TableCell>,
      <TableCell key="3">{model.purpose || "--"}</TableCell>,
      //- <TableCell key="4">{model.application_client || "--"}</TableCell>,
      <TableCell key="5">{model.createTime || "--"}</TableCell>,
      <TableCell key="6">{model.owner || "--"}</TableCell>,
      <TableCell key="7">{model.eval_run_count}</TableCell>,
      <TableCell key="9" column="actions">
          <div className="d-flex">
            <Tooltip arrow placement="top" title="Run" aria-label="Run">
            <IconButton  onClick={() => handleRun(model)}>
              <PlayCircleOutlineIcon fontSize="small" />
            </IconButton>
            </Tooltip>
            <ActionButtonsWithPermission
              permission={permission}
              hideEdit={true}
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
        <Table
            data={data}
            getHeaders={this.getHeaders}
            getRowData={this.getRowData}
            pageChange={pageChange}
        />
    )
}
}

export default VEvaluationConfigTable;
