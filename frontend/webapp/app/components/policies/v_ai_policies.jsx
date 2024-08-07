import React, {Component} from 'react';
import { observer } from 'mobx-react';

import Grid from '@material-ui/core/Grid';
import TableCell from '@material-ui/core/TableCell';
import Switch from '@material-ui/core/Switch';

import Table from 'common-ui/components/table';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';

@observer
class VAIPolicies extends Component {
  getHeaders = () => {
    const { options } = this.props;
    const { permission } = options;
    const headers = [
      <TableCell key={1} column="name">Policy Summary</TableCell>,
      <TableCell key={2} column="status">Status</TableCell>
    ];
    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      headers.push(<TableCell key={3} column="actions">Actions</TableCell>)
    }
    return headers;
  }

  getRowData = (model) => {
    const { options, callbacks } = this.props;
    const { permission } = options;
    const { handlePolicyEdit, handlePolicyDelete, handleStatus } = callbacks;

    const rows = [
      <TableCell key={1} column="name"><a href="JavaScript:void(0);" onClick={() => handlePolicyEdit(model)}>{model.name}</a></TableCell>,
      <TableCell key={2} column="status" width={"80px"}>
        <Switch
          checked={!!model.status}
          onChange={({target}) => handleStatus(+target.checked, model)}
          color="primary"
        />
      </TableCell>
    ];
    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      rows.push(<TableCell key={3} column="actions" width={"80px"}>
        <ActionButtonsWithPermission
          permission={permission}
          onEditClick={() => handlePolicyEdit(model)}
          onDeleteClick={() => handlePolicyDelete(model)}
        />
      </TableCell>)
    }
    return rows;
  }

  render () {
    const { options, callbacks, showPagination } = this.props;
    const { cPolicies } = options;
    const { handlePageChange } = callbacks;

    return (
      <Grid item sm={12}>
        <Table data={cPolicies} 
          getHeaders={this.getHeaders} 
          getRowData={this.getRowData}
          hasElevation={false}
          pageChange={handlePageChange}
          pagination={showPagination}
        />
      </Grid>
    )
  }
}

export default VAIPolicies;