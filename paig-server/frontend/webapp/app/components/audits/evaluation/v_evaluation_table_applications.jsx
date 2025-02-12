import React, { Component } from 'react';
import {observer, inject} from 'mobx-react';
import { Grid, TableCell, Checkbox } from '@material-ui/core';
import Alert from '@material-ui/lab/Alert';

import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';
import Table from 'common-ui/components/table';

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

  handleSelectRow = (id, target_id) => {
    this.props.parent_vState.errorMsg = '';
    this.setState((prevState) => {
      let selectedRows = [...prevState.selectedRows];
      let selectedTargetIds = this.props.form.fields.application_ids.value;
      if (selectedTargetIds === '') {
        selectedTargetIds = [];
      }
      if (selectedRows.includes(id)) {
        selectedRows = selectedRows.filter(rowId => rowId !== id);
        selectedTargetIds = selectedTargetIds.filter(tid => tid !== target_id);
      } else if (selectedRows.length < 2) {
        selectedRows.push(id);
        selectedTargetIds.push(target_id);
      } else {
        return { showAlert: true };
      }

      this.props.form.fields.application_ids.value = selectedTargetIds;
      
      if (this.props.onSelectionChange) {
        this.props.onSelectionChange(selectedRows);
      }
      return { selectedRows, showAlert: false };
    });
  }
  
  handleCloseAlert = () => {
    this.setState({ showAlert: false });
  }

  getHeaders = () => {
    let headers = ([
      <TableCell key="1">Select</TableCell>,
      <TableCell key="2">Name</TableCell>,
      <TableCell key="3">Details</TableCell>,
      <TableCell width="100px" key="9">Actions</TableCell>
    ])

    return headers;
  }

  getRowData = (model) => {
    const {handleDelete, handleEdit, permission} = this.props;
    
    let rows = [
      <TableCell column="select" key="1" className='p-xxs'>
        <Checkbox 
          color='primary'
          data-test="select-all"
          checked={this.state.selectedRows.includes(model.id)}
          onChange={() => this.handleSelectRow(model.id, model.target_id)}
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
    const { data, pageChange, parent_vState} = this.props;
    return (
      <>
        {this.state.showAlert && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Alert severity="error">
                Only two applications can be selected
              </Alert>
            </Grid>
          </Grid>
        )}
        {parent_vState.errorMsg && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Alert severity="error">
                {parent_vState.errorMsg}
              </Alert>
            </Grid>
          </Grid>
        )}
        <Table
          hasElevation={false}
          data={data}
          getHeaders={this.getHeaders}
          getRowData={this.getRowData}
          pageChange={pageChange}
        />
      </>
    )
}
}

export default VEvaluationAppsTable;
