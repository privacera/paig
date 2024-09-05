/* library imports */
import React, { Component } from "react";
import { observer } from "mobx-react";

import TableCell from "@material-ui/core/TableCell";

/* other project imports */
import { ActionButtonsWithPermission } from "common-ui/components/action_buttons";
import { SearchField } from "common-ui/components/filters";
import Table from "common-ui/components/table";
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import { Utils } from "common-ui/utils/utils";
import { TZ } from "common-ui/lib/timezone_worldmap/timezone_worldmap";
import { FEATURE_PERMISSIONS } from "utils/globals";
import { REPORTS_TYPE, findReportTypeFor, redirectToReport } from "containers/reports/c_reporting";

class VSavedReportTable extends Component {
  constructor(props) {
    super(props);
    this.permission = permissionCheckerUtil.getPermissions(
      FEATURE_PERMISSIONS.PORTAL.REPORTS.PROPERTY
    );

    this.reportTypes = Object.values(REPORTS_TYPE);
  }
  sortNameMap = {
    name: "name",
    owner: "addedByUserName",
    updatedBy: "updatedByUserName",
    updateTime: "updateTime",
  };
  handleViewReport = (model) => {
    let paramJson = Utils.parseJSON(model.paramJson);
    let reportType = findReportTypeFor(paramJson.reportType);
    if (reportType) {
      redirectToReport(reportType, model.id);
    }
  };
  getHeaders = () => {
    let list = [
      <TableCell align="left" key="name">
        Report Name
      </TableCell>,
      <TableCell align="left" key="type">
        Report Type
      </TableCell>,
      <TableCell align="left" key="desc">
        Description
      </TableCell>,
      <TableCell align="left" key="updateTime">
        Updated On {`(${TZ.zoneName})` || ""}
      </TableCell>,
      <TableCell
        key="actions"
        width="100px"
        className="text-center"
      >
        Actions
      </TableCell>
    ];

    return list;
  };
  getReportTypeLabel = (model) => {
    let paramJson = Utils.parseJSON(model.paramJson);
    let reportType = findReportTypeFor(paramJson.reportType);
    const obj = this.reportTypes.find((report) => report.name === reportType);
    return obj ? obj.label : 'Unknown';
  };
  getRows = (model) => {
    const { handleDelete } = this.props;
    let list = [
      <TableCell
        align="left"
        component="th"
        scope="row"
        key="name"
      >
        <a data-test="view" onClick={() => this.handleViewReport(model)}>
          {model.name}
        </a>
      </TableCell>,
      <TableCell align="left" key="reportType">
        {this.getReportTypeLabel(model)}
      </TableCell>,
      <TableCell align="left" key="desc">
        {model.description}
      </TableCell>,
      <TableCell align="left" key="updateTime" width="10%">
        {model.updateTime &&
          Utils.dateUtil.getTimeZone(
            Utils.dateUtil.getJSON(model.updateTime)
          )
        }
      </TableCell>,
      <TableCell key="actions">
        <div className="d-flex">
          <ActionButtonsWithPermission
            permission={this.permission}
            showPreview={false}
            onPreviewClick={() => this.handleViewReport(model)}
            //onEditClick={() => this.handleEdit(model)}
            onEditClick={() => this.handleViewReport(model)}
            onDeleteClick={() => {
              handleDelete(model);
            }}
          />
        </div>
      </TableCell>
    ];

    return list;
  };

  render() {
    const { cData, handlePageChange } = this.props;

    // let tableAttr = {
    //   columnToSort: ["name", "updateTime"],
    //   isSortingEnabled: true,
    //   defaultSort: { column: "updateTime", direction: "desc" },
    //   // onSort: this.handleSort
    // };

    return (
      <Table
        data={cData}
        getHeaders={this.getHeaders}
        getRowData={this.getRows}
        pageChange={handlePageChange}
        //tableAttr={tableAttr}
      />
    );
  }
}

const Search = observer(function Search({ _vState, handleSearch }) {
  return (
    <SearchField
      placeholder={`Input report name and press enter to search`}
      colAttr={{ xs: 12, sm: 4, md: 4 }}
      onChange={e => _vState.searchValue = e.target.value}
      value={_vState.searchValue}
      onEnter={val => handleSearch && handleSearch(val)}
    />
  );
});

export { VSavedReportTable, Search };