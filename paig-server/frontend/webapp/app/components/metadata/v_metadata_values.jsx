import React, { Component } from "react";

import { TableCell } from "@material-ui/core";

import Table from "common-ui/components/table";
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';

class VMetaDataValues extends Component {
  constructor(props) {
    super(props);
  }

  getHeaders = () => {
    const { permission } = this.props;

    let headers = [
      <TableCell key="value">
        Value
      </TableCell>
    ];

    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      headers.push(<TableCell key="actions">Actions</TableCell>);
    }

    return headers;
  };

  getRowData = (model) => {
    const { permission, handleEdit, handleDelete } = this.props;

    // let dataType = this.metaDataTypes[model.valueDataType]?.LABEL || model.valueDataType;

    let rows = [
      <TableCell key="value" data-testid="metadata-value">
        {model.metadataValue || "--"}
      </TableCell>
    ];

    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      rows.push(
        <TableCell key="actions" width="80px">
          <ActionButtonsWithPermission
            permission={permission}
            onEditClick={() => handleEdit(model)}
            onDeleteClick={() => handleDelete(model)}
          />
        </TableCell>
      )
    }

    return rows;
  };

  handleContextMenuSelection = () => {};

  render() {
    const { pageChange, data } = this.props;

    return (
      <Table
        tableRowAttr={{className: "p-l-15 p-r-15"}}
        data={data}
        getHeaders={this.getHeaders}
        getRowData={this.getRowData}
        pageChange={pageChange}
        showContextMenu={false}
        onContextMenuSelection={this.handleContextMenuSelection}
        resizable={false}
        hasElevation={false}
        tableId="meta_data"
      />
    );
  }
}

export default VMetaDataValues;