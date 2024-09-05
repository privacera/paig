import React, { Component } from "react";

import { TableCell } from "@material-ui/core";

import Table from "common-ui/components/table";

class VSensitiveData extends Component {
  constructor(props) {
    super(props);
  }

  getHeaders = () => {
    let headers = [
      <TableCell key="1">
        Name
      </TableCell>,
      <TableCell key="2">
        Description
      </TableCell>
    ];
    return headers;
  };

  getRowData = (model) => {
    return [
      <TableCell key="1">
        {model.name || "--"}
      </TableCell>,
      <TableCell key="2">
        {model.description || "--"}
      </TableCell>
    ];
  };

  handleContextMenuSelection = () => {};

  render() {
    const { pageChange, data } = this.props;

    return (
      <Table
        data={data}
        getHeaders={this.getHeaders}
        getRowData={this.getRowData}
        pageChange={pageChange}
        showContextMenu={false}
        onContextMenuSelection={this.handleContextMenuSelection}
        resizable={false}
        tableId="sensitive_data"
      />
    );
  }
}

export default VSensitiveData;
