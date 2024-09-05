import React, {Component, createRef, Fragment} from 'react';
import { observer } from 'mobx-react';
import { capitalize } from "lodash";
import { action, observable } from "mobx";

import Link from '@material-ui/core/Link';
import {TableCell, Typography} from '@material-ui/core';

import {Utils} from 'common-ui/utils/utils';
import FSModal from 'common-ui/lib/fs_modal';
import Table from 'common-ui/components/table';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {ACTION_TYPE, OBJECT_TYPE_MAPPING} from 'utils/globals';
import CAdminAuditsOperationDetail from 'containers/compliance/c_admin_audits_operation_detail';

@observer
class VAdminAudits extends Component {
  @observable _vState = {
    currentModel: {}
  }
  constructor(props) {
    super(props);
    this.operationDetail = createRef();
  }
  @action
  onTableRowClick = (model) => {
    
    this._vState.currentModel = model;
    this.operationDetail.current?.show({
      showOkButton: false
    })
  }
  getDerivedSentence = (obj) => {
    const actionSentence = ACTION_TYPE[obj.action]?.LABEL || obj.action.toLowerCase();
    const objectTypeSentence = OBJECT_TYPE_MAPPING[obj.objectType]?.LABEL || Utils.toTitleCase(obj.objectType);

    if (obj.objectType === OBJECT_TYPE_MAPPING.SHIELD_AUDIT.VALUE && obj.action === ACTION_TYPE.REVIEW.VALUE ) {
      return (
        <Link onClick={() => this.onTableRowClick(obj)}>
          {`User ${actionSentence} ${objectTypeSentence}`} <b>{obj.objectId}</b>
        </Link>
      );
    }
    if (actionSentence && objectTypeSentence) {
      return (
        <Link onClick={() => this.onTableRowClick(obj)}>
          {`${objectTypeSentence} ${actionSentence}`} <b>{obj.objectName || obj.objectId}</b>
        </Link>
      );
    }

    return null;
  }
  getHeaders = () => {
    let headers = [
      <TableCell key="evtTime">Event Time</TableCell>,
      <TableCell key="operation">Operation</TableCell>,
      <TableCell key="action">Action</TableCell>,
      <TableCell key="actedByUsername">Acted by User</TableCell>
    ];

    return headers;
  }
  getRowData = (model, index) => {
    let actionContent = model.action;
    let actionColor = '';
    if (model.action === ACTION_TYPE.CREATE.VALUE) {
      actionContent = model.action;
      actionColor = 'green'; 
    } else if (model.action === ACTION_TYPE.DELETE.VALUE) {
      actionContent = model.action;
      actionColor = '#f44336';
    } 
    let rows = [
      <TableCell key="evtTime">
        {model.logTime ? Utils.dateUtil.getTimeZone(model.logTime, DATE_TIME_FORMATS.DATE_FORMAT) : '--'}
      </TableCell>,
      <TableCell key="operation">
        {<div>{this.getDerivedSentence(model)}</div>}
      </TableCell>,
      <TableCell key="action">
        {actionContent && (
          <Typography variant="body2" style={{ color: actionColor }}>
            {capitalize(actionContent.toLowerCase())}
          </Typography>
        )}
      </TableCell>,
      <TableCell key="actedByUsername">
        {model.actedByUsername || '--'}
      </TableCell>
    ];

    return rows;
  }    
  handleContextMenuSelection = () => {}

  render() {
    const {data, pageChange} = this.props;

    return (
      <Fragment>
        <Table
          data={data}
          getHeaders={this.getHeaders}
          getRowData={this.getRowData}
          pageChange={pageChange}
          showContextMenu={false}
          onContextMenuSelection={this.handleContextMenuSelection}
          resizable={false}
          tableId="admin_audit"
        />
        <FSModal ref={this.operationDetail} maxWidth="lg" dataTitle={`Operation : ${Utils.toTitleCase(this._vState.currentModel.action)}`}>
          <CAdminAuditsOperationDetail operationDetailObj={this._vState.currentModel} />
        </FSModal>
      </Fragment>
    )
  }
}

export default VAdminAudits;