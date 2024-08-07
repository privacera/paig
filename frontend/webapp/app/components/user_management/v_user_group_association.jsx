import React, { Component, Fragment } from 'react';
import { observer } from 'mobx-react';

import { TableCell, Grid, Checkbox, Typography, IconButton } from '@material-ui/core';
import PeopleIcon from '@material-ui/icons/People';
import EditIcon from '@material-ui/icons/Edit';
import Button from '@material-ui/core/Button';

import Table from 'common-ui/components/table';
import { TagChip } from 'common-ui/lib/fs_select/fs_select';
import { SearchField } from 'common-ui/components/filters';

@observer
class VGroupAssociation extends Component{

  populateCheckboxes = (groups) => {
    const { importExportUtil } = this.props;
    groups?.forEach((group) => {
      importExportUtil.checked(true, group, false);
    });
  };

  toggleEditTagMode = () => {
    const { _vState } = this.props;
    _vState.showGroupsListing = true;
    this.populateCheckboxes(_vState.preSelectedGroups);
  }

  onCancel = () => {
    const { _vState, importExportUtil } = this.props;
    importExportUtil.reset();
    _vState.addedGroups = []
    _vState.removedGroups = []
    _vState.showGroupsListing = false;
    this.populateCheckboxes(_vState.preSelectedGroups);
  }
  
  getHeaders = () => {
    const { readOnly, importExportUtil } = this.props;
    let headers = ([
      <TableCell column="select" key="1" className='p-xxs'>
        <Checkbox 
          color='primary'
          checked={importExportUtil.data.length ? importExportUtil.isAllChecked : false}
          disabled={!importExportUtil.data.length || readOnly}
          onChange={(e) => {importExportUtil.checkboxClick(e, "", true);}}
        />
      </TableCell>,
      <TableCell key="2" className="table-search-156">Group Name</TableCell>,
      <TableCell key="3" className="table-search-156">Description</TableCell>
    ])

    return headers;
  }

  getRowData = (model) => {
    const {readOnly, importExportUtil} = this.props;
    let rows = [
      <TableCell column="select" key="1" className='p-xxs'>
        <Checkbox 
          color='primary'
          data-test="select-all"
          checked={importExportUtil.isSelected(model.name)}
          disabled={!importExportUtil.data.length || readOnly}
          onChange={(e) => importExportUtil.checkboxClick(e, model.name)}
        />
      </TableCell>,
      <TableCell key="2">{model.name || "--"}</TableCell>,
      <TableCell key="3">{model.description || "--"}</TableCell>
    ]

    return rows;
  }

  calculateCount = () => {
    const { _vState, importExportUtil } = this.props;
    const currentSelectedGroups = importExportUtil.getSelectIdList();
    const addedCount = currentSelectedGroups.filter(group => !_vState.preSelectedGroups.includes(group)).length;
    const removedCount = _vState.preSelectedGroups.filter(group => !currentSelectedGroups.includes(group)).length;
    return { addedCount, removedCount };
  }

  render(){
    const { _vState, pageChange, data, handleSearch, isEditMode } = this.props;
    const { addedCount, removedCount } = this.calculateCount();

    return (
      <Fragment>
        {
          isEditMode && !_vState.showGroupsListing ? (
            <Fragment>
              <Grid container spacing={3} alignItems="center">
                <Grid item className='m-b-md'>
                  <Typography variant="h6" component="h2">Groups<IconButton data-testid="edit-group" onClick={this.toggleEditTagMode}><EditIcon color="primary"/></IconButton></Typography>
                </Grid>
              </Grid>
              <Grid container justifyContent="flex-end">
                {
                  _vState.preSelectedGroups.map(group => (
                    <TagChip
                      data-testid="tag-chip"
                      key={group}
                      className="m-r-sm m-b-xs"
                      label={group}
                      icon={<PeopleIcon fontSize="small" color="action" />}
                    />
                  ))
                }
              </Grid>
            </Fragment>
          ) : (
          <Fragment>
            <Grid container spacing={3}>
              <SearchField
                value={_vState.searchValue}
                colAttr={{xs: 12, sm: 10, md: 6, lg: 6}}
                placeholder="Search group"
                onChange={(e, val) => _vState.searchValue = val}
                onEnter={handleSearch}
                data-testid="search-field"
              />
              {
                isEditMode && _vState.preSelectedGroups.length > 0 &&
                <Fragment>
                  <Grid item xs={12} sm={12} md={6} lg={6}>
                    <div className="text-right" data-testid="added-removed-counters">
                      <Typography variant="subtitle2" color="textSecondary" className="inline-block m-r-sm">Added: {addedCount}</Typography>
                      <Typography variant="subtitle2" color="textSecondary" className="inline-block m-r-md">Removed: {removedCount}</Typography>
                      <Button className="inline-block" color="primary" onClick={this.onCancel} data-testid="cancel-button">Cancel</Button>
                    </div>
                  </Grid>
                </Fragment>
              }
            </Grid>
            <Table
              data={data}
              getHeaders={this.getHeaders}
              getRowData={this.getRowData}
              pageChange={pageChange}
              hasElevation={false}
            />
          </Fragment>
          )
        }
      </Fragment>
    );
  }
}

export default VGroupAssociation;