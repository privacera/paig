import React, { Component, Fragment } from 'react';
import {observer} from 'mobx-react';

import { TableCell, Grid, Checkbox } from '@material-ui/core';
import DoneIcon from '@material-ui/icons/Done';
import ClearIcon from '@material-ui/icons/Clear';

import f from 'common-ui/utils/f';
import Table from 'common-ui/components/table';
import { SearchField } from 'common-ui/components/filters';
import {STATUS} from 'common-ui/utils/globals';

@observer
class VUserAssociation extends Component{
  getHeaders = () => {
    const {importExportUtil, readOnly} = this.props;
    let headers = ([
        <TableCell key="1" className='p-xxs'>
          <Checkbox 
            color='primary'
            checked={importExportUtil.data.length ? importExportUtil.isAllChecked : false}
            disabled={!importExportUtil.data.length || readOnly}
            onChange={this.handleSelectAllCheckbox}
          />
        </TableCell>,
        <TableCell key="2" className="table-search-156">User Name</TableCell>,
        <TableCell key="3" className="table-search-156">First Name</TableCell>,
        <TableCell key="4" className="table-search-156">Last Name</TableCell>,
        <TableCell key="5" className="table-search-156">Email</TableCell>,
        <TableCell key="6" className="text-center table-search-156">Enabled</TableCell>
    ])

    return headers;
  }
  handleSelectAllCheckbox = (e) => {
    const {data} = this.props;
    f.models(data).forEach(model => {
      this.handleCheckboxChange(e, model);
    })
  }
  // isCheckboxSelected = (model) => {
  //   const {_vState} = this.props;
  //   if (_vState.removedUsers.has(model.username)) {
  //     return false;
  //   } else if (_vState.addedUsers.has(model.username) || model.groups.includes(_vState.selectedGroup?.name)) {
  //     return true;
  //   }
  //   return false;
  // }
  handleCheckboxChange = (e, model) => {
    // 1. manuall added and removed
    // check first if present in model.groups, if not then
    // add in _vState.addedUser
    // remove from _vState.addedUser

    // 2. already added and removed
    // check first if present in model.groups, if yes then
    // add username in _vState.removedUser
    // and remove from _vState.removedUser
    const {_vState, importExportUtil} = this.props;
    if (e.target.checked) {
      if (model.groups?.includes(_vState.selectedGroup?.name)) {
        _vState.removedUsers.delete(model.username);
      } else {
        _vState.addedUsers.add(model.username);
      }
    } else {
      if (model.groups?.includes(_vState.selectedGroup?.name)) {
        _vState.removedUsers.add(model.username);
      } else {
        _vState.addedUsers.delete(model.username);
      }
    }
    importExportUtil.checkboxClick(e, model.username)
  }
  getRowData = (model) => {
    const {importExportUtil, readOnly} = this.props;
    let rows = [
      <TableCell key="1" className='p-xxs'>
        <Checkbox 
          color='primary'
          // checked={this.isCheckboxSelected(model)}
          checked={importExportUtil.isSelected(model.username)}
          disabled={!importExportUtil.data.length|| readOnly}
          onChange={(e) => this.handleCheckboxChange(e, model)}
        />
      </TableCell>,
      <TableCell key="2">{model.username || "--"}</TableCell>,
      <TableCell key="3">{model.firstName || "--"}</TableCell>,
      <TableCell key="4">{model.lastName || "--"}</TableCell>,
      <TableCell key="5">{model.email || "--"}</TableCell>,
      <TableCell key="6" className="text-center">
        {
          model.status == STATUS.enabled.value
          ? <DoneIcon data-testid="account-enabled" className="text-success" />
          : <ClearIcon data-testid="account-disabled" color="secondary" />
        }
      </TableCell>
    ]

    return rows;
  }

  render(){
    const { _vState, pageChange, data, handleSearch} = this.props;

    return (
      <Fragment>
        <Grid container spacing={3}>
          <SearchField
            value={_vState.searchValue}
            colAttr={{xs: 12, sm: 10, md: 6, lg: 6}}
            placeholder="Search user"
            onChange={(e, val) => _vState.searchValue = val}
            onEnter={handleSearch}
          />
        </Grid>
        <Table
          data={data}
          getHeaders={this.getHeaders}
          getRowData={this.getRowData}
          pageChange={pageChange}
          hasElevation={false}
        />
      </Fragment>
    );
  }
}

export default VUserAssociation;