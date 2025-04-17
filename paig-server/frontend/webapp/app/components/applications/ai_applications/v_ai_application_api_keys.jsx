import React, {Component} from 'react';

import {TableCell} from '@material-ui/core';
import Tooltip from '@material-ui/core/Tooltip';
import DeleteIcon from '@material-ui/icons/Delete';
import Typography from '@material-ui/core/Typography';
import HighlightOffIcon from '@material-ui/icons/HighlightOff';
import Visibility from '@material-ui/icons/Visibility';
import VisibilityOff from '@material-ui/icons/VisibilityOff';
import FileCopyIcon from '@material-ui/icons/FileCopy';

import {Utils} from 'common-ui/utils/utils';
import Table from 'common-ui/components/table';
import {API_KEY_STATUS} from 'utils/globals';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {CommandDisplay} from 'common-ui/components/action_buttons';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {CustomAnchorBtn, CanDelete} from 'common-ui/components/action_buttons';

class CommandVisibilityToggle extends CommandDisplay {
  state = {
    showCommand: false
  }

  toggleVisibility = () => {
    this.setState({ showCommand: !this.state.showCommand });
  }

  render() {
    const {command} = this.props;
    const {showCommand, copyState} = this.state;

    return (
      <pre className="break-word" style={{ display: 'flex'}} >
        <span style={{ flexGrow: 2, alignSelf: "center", paddingRight: "5px"}} data-testid="command-text">
          {showCommand ? command : '•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••'}
        </span>
        <div style={{minWidth: '60px'}}>
          <CustomAnchorBtn
            size="small"
            tooltipLabel={showCommand ? "Click to hide" : "Click to reveal"}
            className="toggle-visibility-button"
            onClick={this.toggleVisibility}
            icon={showCommand ? <VisibilityOff fontSize="small"/> : <Visibility fontSize="small"/>}
            data-testid="toggle-visibility-button"
          />
          <CustomAnchorBtn
            size="small"
            tooltipLabel={copyState ? "Copied!" : "Copy to Clipboard"}
            className="copy-button"
            onClick={(e) => {
              this.copyHiddenContent(command);
              this.handleClick && this.handleClick(e);
            }}
            icon={<FileCopyIcon fontSize="small" color="primary" />}
            data-testid="copy-button"
          />
        </div>
      </pre>
    );
  }
};

class VAIApplicationApiKeys extends Component{

  getHeaders = () => {
    const {permission} = this.props;
    let headers = [
      <TableCell key="1" column="keyName" width="14%">Key Name</TableCell>,
      <TableCell key="2" column="key" width="15%">Key</TableCell>,
      <TableCell key="3" column="description" width="30%">Description</TableCell>,
      <TableCell key="4" column="expiry" style={{ minWidth: '150px' }}>Expires</TableCell>,
      <TableCell key="5" column="status" width="10%">Status</TableCell>,
      // <TableCell column="createdBy">Created by</TableCell>
    ]
    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      headers.push(<TableCell width="100px" key="6" column="actions">Actions</TableCell>);
    }
    return headers;
  }

  getRowData = (model) => {
    const {handleDelete, handleRevoke, permission} = this.props;
    const moment = Utils.dateUtil.momentInstance();
    const formattedExpiryDate = moment(model.tokenExpiry).format(DATE_TIME_FORMATS.DATE_FORMAT_WITH_GMT);
    let apiKeyStatus = API_KEY_STATUS[model.keyStatus] || { LABEL: model.keyStatus, VALUE: model.keyStatus, bsStyle: "default", COLOR: "masked-color" };

    let remainingTime = null;
    let isExpired = false;
    if (!model.neverExpire) {
      remainingTime = model.getTokenExpiryInDaysAndHour();
      const durationInSeconds = moment(model.tokenExpiry).diff(moment(), 'seconds');
      if (durationInSeconds <= 0) {
        apiKeyStatus = API_KEY_STATUS.EXPIRED;
        isExpired = true;
      }
    }

    let rows = [
      <TableCell key="1" column="keyName" className='break-word'>{model.apiKeyName || "--"}</TableCell>,
      <TableCell key="2" column="key">{model.apiKeyMasked || "--"}</TableCell>,
      <TableCell key="3" column="description">{model.description || "--"}</TableCell>,
      <TableCell key="4" column="expiry">
        {
          model.neverExpire
          ?
          'Never Expires'
          : (
            <Tooltip key={'tooltip'} placement="top" arrow title={formattedExpiryDate}>
              <span className={isExpired ? API_KEY_STATUS.EXPIRED.COLOR : '' }>
                {remainingTime}
              </span>
            </Tooltip>
          )
        }
      </TableCell>,
      <TableCell key="5" column="status">
        <Typography variant="body2" className={apiKeyStatus.COLOR}>
          {apiKeyStatus.LABEL}
        </Typography>
      </TableCell>
      // <TableCell column="createdBy">{model.createdBy || "--"}</TableCell>,
    ]
    if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
      rows.push(
        <TableCell key="6" column="actions">
          <div className="d-flex">
            {permissionCheckerUtil.checkHasUpdatePermission(permission) &&
              <Tooltip 
                arrow 
                placement="top" 
                title={model.keyStatus == API_KEY_STATUS.DISABLED.VALUE ? "API key is already Revoked" : "Revoke"}
              >
                <span>
                  <CustomAnchorBtn
                    data-testid="revoke-api-key"
                    onClick={() => handleRevoke(model)}
                    disabled={model.keyStatus == API_KEY_STATUS.DISABLED.VALUE}
                    icon={<HighlightOffIcon color={model.keyStatus == API_KEY_STATUS.DISABLED.VALUE ? "disabled" : "primary"} fontSize="inherit" />}
                  />
                </span>
              </Tooltip>
            }
            <CanDelete permission={permission}>
              <Tooltip 
                arrow 
                placement="top" 
                title={model.keyStatus == API_KEY_STATUS.ACTIVE.VALUE ? "Delete feature will be available after the API key is Revoked" : "Delete"}
              >
                <span>
                  <CustomAnchorBtn
                    data-testid="delete-api-key"
                    onClick={() => handleDelete(model)}
                    disabled={model.keyStatus == API_KEY_STATUS.ACTIVE.VALUE}
                    icon={<DeleteIcon color={model.keyStatus == API_KEY_STATUS.ACTIVE.VALUE ? "disabled" : "primary"}  fontSize="inherit" />}
                  />
                </span>
              </Tooltip>
            </CanDelete>
          </div>
        </TableCell>
      );
    }
    return rows;
  }

  sortNameMap = {
    expiry: 'tokenExpiry'
  }

  setSortParams = (sortObj) => {
    if(sortObj){
      this.props.data.params.sort = `${this.sortNameMap[sortObj.column]},${sortObj.direction}`;
    }
    this.props.handleSorting()
  }

  render(){
    const {pageChange, data} = this.props;
    let tableAttr = {
      isSortingEnabled: true,
      sortDirection: 'desc',
      columnToSort: ['expiry'],
      onSort: this.setSortParams
    }
    return (
      <Table
        data={data}
        getHeaders={this.getHeaders}
        getRowData={this.getRowData}
        pageChange={pageChange}
        hasElevation={false}
        tableAttr={tableAttr}
      />
    );
  }
}

export {CommandVisibilityToggle};
export default VAIApplicationApiKeys;
