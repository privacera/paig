import React, {Component, Fragment} from 'react';
import {inject} from 'mobx-react';
import {capitalize} from "lodash";

import {TableCell} from '@material-ui/core';
import CheckIcon from "@material-ui/icons/Check";
import CloseIcon from "@material-ui/icons/Close";
import {Tooltip, LinearProgress} from "@material-ui/core";

import {Utils} from 'common-ui/utils/utils';
import Table from 'common-ui/components/table';
import RefreshIcon from '@material-ui/icons/Refresh';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

const moment = Utils.dateUtil.momentInstance();

@inject('evaluationStore')
class VEvaluationReportTable extends Component{
  constructor(props) {
    super(props);
    this.state = {
      expandedRows: []
    };
  }

  getStatus = (status) => {
    if (!status) return null;
    const normalizedStatus = status.toLowerCase();
    const formattedStatus = capitalize(normalizedStatus);

    if (normalizedStatus === "completed") {
      return (
        <CustomAnchorBtn
          size="small"
          tooltipLabel="Completed"
          data-testid="completed"
          icon={<CheckIcon className="text-success" fontSize="inherit"/>}
        />
      );
    } else if (normalizedStatus === "failed") {
      return (
        <CustomAnchorBtn
          size="small"
          tooltipLabel="Failed"
          data-testid="failed"
          icon={<CloseIcon className="error" fontSize="inherit"/>}
        />
      );
    } else {
      return (
        <Tooltip arrow placement="top" title={formattedStatus}>
          <div 
            style={{ 
              width: "100%", 
              margin: "auto", 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "center" 
            }}
            className="pointer"
          >
            <LinearProgress style={{ width: "50%", margin: "auto" }} />
          </div>
        </Tooltip>
      );
    }
  };

  getHeaders = () => {
    let headers = ([
      <TableCell key="1">Report Name</TableCell>,
      <TableCell key="2">Eval</TableCell>,
      <TableCell key="3">Applications</TableCell>,
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
    const {handleReRun, handleView, permission, handleDelete} = this.props;
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
    const { data, pageChange } = this.props;
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
