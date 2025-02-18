import React, {Component, Fragment} from 'react';
import {observer, inject} from 'mobx-react';

import {TableCell} from '@material-ui/core';
import CheckIcon from "@material-ui/icons/Check";
import CloseIcon from "@material-ui/icons/Close";
import {Tooltip, IconButton, LinearProgress} from "@material-ui/core";

import {Utils} from 'common-ui/utils/utils';
import Table from 'common-ui/components/table';
import RefreshIcon from '@material-ui/icons/Refresh';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

const moment = Utils.dateUtil.momentInstance();

@inject('evaluationStore')
@observer
class VEvaluationReportTable extends Component{
  constructor(props) {
    super(props);
    this.state = {
      expandedRows: []
    };
  }
    
  getStatus = (status) => {
    const normalizedStatus = status.toLowerCase(); // Convert to lowercase for comparison
  
    if (normalizedStatus === "completed") {
      return (
        <Tooltip arrow placement="top" title="Completed">
          <IconButton size="small" data-test="completed" aria-label="completed">
            <CheckIcon className="text-success" fontSize="inherit" />
          </IconButton>
        </Tooltip>
      );
    } else if (normalizedStatus === "failed") {
      return (
        <Tooltip arrow placement="top" title="Failed">
          <IconButton size="small" data-test="failed" aria-label="failed">
            <CloseIcon color="error" fontSize="inherit" />
          </IconButton>
        </Tooltip>
      );
    } else {
      return <LinearProgress style={{ width: "50%", margin: "auto" }} />;
    }
  };

  getHeaders = () => {
    let headers = ([
      <TableCell key="1">Report Name</TableCell>,
      <TableCell key="2">Configuration Used</TableCell>,
      <TableCell key="3">Applications Evaluated</TableCell>,
      <TableCell key="5" className="text-center">Report Status</TableCell>,
      <TableCell key="6">Score</TableCell>,
      <TableCell key="7">Created</TableCell>,
      <TableCell width="110px" key="9">Actions</TableCell>
    ])

    return headers; 
  }

  formatPercentage = (value) => {
    const formattedValue = value % 1 === 0 ? value.toFixed(0) : value.toFixed(2);
    return `${formattedValue}%`;
  }


  getResultCell = (model) => {
    if (!model.passed || !model.failed) return "--";
  
    // Convert `passed` and `failed` strings into arrays of numbers
    const passedArray = model.passed.split(",").map((value) => parseInt(value.trim(), 10));
    const failedArray = model.failed.split(",").map((value) => parseInt(value.trim(), 10));
  
    // Calculate percentages for corresponding indices
    return passedArray.map((passed, index) => {
      const failed = failedArray[index] || 0; // Default to 0 if no corresponding `failed` value
      const total = passed + failed;
      const percentage = total ? ((passed / total) * 100).toFixed(2) + "%" : "0%";
  
      return (
        <Fragment key={index}>
          <div>
            {percentage} ({passed}/{total})
          </div>
          {index !== passedArray.length - 1 && <hr />}
        </Fragment>
      );
    });
  };

  getApplicationNameCell = (applicationName) => {
    if (!applicationName) return "--";
    const names = applicationName.split(",").map((name, index) => (
      <Fragment key={index}>
        <div>{name.trim()}</div>
        {index !== applicationName.split(",").length - 1 && <hr />}
      </Fragment>
    ));
    return names;
  };

  getRowData = (model) => {
    const {handleReRun, handleView, permission, importExportUtil, handleDelete} = this.props;
    let rows = [
      <TableCell key="1">{model.name}</TableCell>,
      <TableCell key="2">{model.config_name || "--"}</TableCell>,
      <TableCell key="3">{this.getApplicationNameCell(model.application_names) || "--"}</TableCell>,
      //- <TableCell key="4">{model.application_client || "--"}</TableCell>,
      <TableCell key="5" className="text-center">{this.getStatus(model.status) || "--"}</TableCell>,
      <TableCell key="7">{this.getResultCell(model)}</TableCell>,
      <TableCell key="8">{model.create_time ? moment(model.create_time).format(DATE_TIME_FORMATS.DATE_TIME_FORMAT_SHORT) : '--'}</TableCell>,
      <TableCell key="9" column="actions">
        <ActionButtonsWithPermission
          permission={permission}
          showPreview={model.status == 'COMPLETED'}
          hideDelete={true}
          onPreviewClick={() => handleView(model)}
        />
        <CustomAnchorBtn
          disabled={model.status !== 'COMPLETED'}
          tooltipLabel="Re Run"
          color="primary"
          icon={<RefreshIcon fontSize="inherit"/>}
          onClick={() => handleReRun(model)}
        />
        <ActionButtonsWithPermission
          permission={permission}
          showPreview={false}
          hideDelete={false}
          onDeleteClick={() => handleDelete(model)}
        />
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

export default VEvaluationReportTable;
