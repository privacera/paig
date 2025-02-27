import React, {Component} from 'react';
import {observer, inject} from 'mobx-react';

import {TableCell} from '@material-ui/core';
import PlayCircleOutlineIcon from '@material-ui/icons/PlayCircleOutline';

import {Utils} from 'common-ui/utils/utils';
import Table from 'common-ui/components/table';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {CustomAnchorBtn} from 'common-ui/components/action_buttons';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

const moment = Utils.dateUtil.momentInstance();

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
      <TableCell key="5">{model.createTime ? moment(model.createTime).format(DATE_TIME_FORMATS.DATE_TIME_FORMAT_SHORT) : '--'}</TableCell>,
      <TableCell key="6">{model.owner || "--"}</TableCell>,
      <TableCell key="7">{model.eval_run_count}</TableCell>,
      <TableCell key="9" column="actions">
        <CustomAnchorBtn
          tooltipLabel="Run"
          color="primary"
          icon={<PlayCircleOutlineIcon fontSize="small" />}
          onClick={() => handleRun(model)}
        />
        <ActionButtonsWithPermission
          permission={permission}
          hideEdit={true}
          hideDelete={false}
          onDeleteClick={() => handleDelete(model)}
          onEditClick={() => handleEdit(model)}
        />
      </TableCell>
    ]
    return rows;
  }

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

export default VEvaluationConfigTable;
