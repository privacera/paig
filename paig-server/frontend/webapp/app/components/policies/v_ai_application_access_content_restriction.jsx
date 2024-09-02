import React, {Component} from 'react';
// import { observer } from 'mobx-react';

import {TableBody, TableRow, TableCell, Switch, Chip} from '@material-ui/core';
import MaterialTable from '@material-ui/core/Table';
import Tooltip from '@material-ui/core/Tooltip';
import PersonIcon from '@material-ui/icons/Person';
import PeopleIcon from '@material-ui/icons/People';

import {MESSAGE_RESULT_TYPE, PROMPT_REPLY_ACTION_TYPE} from 'utils/globals';
import Table from 'common-ui/components/table';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';
import f from 'common-ui/utils/f';

class VAIApplicationAccessContentRestriction extends Component {
    getValueAndColorForRestriction = (restriction) => {
        let value = 'Allow';
        let color = MESSAGE_RESULT_TYPE.ALLOWED.COLOR;
        if (restriction === PROMPT_REPLY_ACTION_TYPE.DENY.VALUE) {
            value = 'Deny';
            color = MESSAGE_RESULT_TYPE.DENIED.COLOR;
        } else if (restriction === PROMPT_REPLY_ACTION_TYPE.REDACT.VALUE) {
            value = 'Redact';
            color = MESSAGE_RESULT_TYPE.MASKED.COLOR;
        }
        return {value, color};
    }
    getSensitiveDataDescription = (name) => {
        const {cSensitiveData} = this.props;
        const foundData = cSensitiveData && f.models(cSensitiveData).find(
            data => data.name === name
        );
    
        return foundData ? foundData.description : '';
    };
    getHeaders = () => {
        const {permission, showStatusColumn} = this.props;
        const headers = [
            <TableCell key="description" width="200px">Description</TableCell>,
            <TableCell key="userGroup" width="300px">Users / Groups</TableCell>,
            <TableCell key="tags">Content Having Tags</TableCell>,
            <TableCell key="restrictions" width="120px">Restrictions</TableCell>
        ]

        if (showStatusColumn) {
            headers.push(<TableCell key="status" width="70px">Status</TableCell>);
        }

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            headers.push(<TableCell key="action">Actions</TableCell>)
        }
        return headers;
    }
    getRowData = (model, i) => {
        const {permission, handleStatusUpdate, handlePolicyEdit, handlePolicyDelete, cSensitiveData, showStatusColumn} = this.props;

        let userGroups = [];
        if (model.users) {
            userGroups.push({
                label: 'users',
                value: model.users
            });
        }
        if (model.groups?.length) {
            if (!model.users.length && model.groups.length === 1 && model.groups[0] === 'public') {
                userGroups.push({
                    label: 'groups',
                    value: ['Everyone']
                });
            } else {
                userGroups.push({
                    label: 'groups',
                    value: model.groups
                });
            }
        }

        let prompt = this.getValueAndColorForRestriction(model.prompt);
        let reply = this.getValueAndColorForRestriction(model.reply);

        let inActiveClass = model.status ? '' : 'inactive';

        return (
            <TableRow
                key={model.id || i}
                hover
                data-testid="table-row"
                className="restriction-row"
            >
                <TableCell key="description" className={inActiveClass}>{model.description || model.name}</TableCell>
                <TableCell key="userGroup" className={inActiveClass}>
                    {
                        userGroups.map((userGroup) => {
                            return userGroup.value.map((value, index) => {
                                return (
                                    <Chip
                                        key={value + index}
                                        className="table-container-chips m-r-xs m-b-xs"
                                        size="small"
                                        label={<span>{userGroup.label == 'users' ? <PersonIcon fontSize="small" color="action" /> : <PeopleIcon fontSize="small" color="action" />} {value}</span>}
                                        data-testid={`user-group-chip-${index}`}
                                    />
                                )
                            })
                        })
                    }
                </TableCell>
                <TableCell key="tags" className={inActiveClass}>
                {
                    model.tags?.map((value, index) => {
                        const description = this.getSensitiveDataDescription(value);
                        return (
                            <Tooltip
                                key={value + index}
                                title={description}
                                placement="top"
                                arrow
                            >
                                <Chip
                                    className="table-container-chips m-r-xs m-b-xs"
                                    size="small"
                                    label={value}
                                    data-testid={`sensitive-data-chip-${index}`}
                                />
                            </Tooltip>
                        );
                    })
                }
                </TableCell>
                <TableCell key="restrictions" className={`restrictions-table-box ${inActiveClass}`}>
                    <MaterialTable className="restrictions-table">
                        <TableBody>
                            <TableRow className="restriction-row">
                                <TableCell key="prompt">Prompt</TableCell>
                                <TableCell key="promptValue" style={{color: prompt.color}}>{prompt.value}</TableCell>
                            </TableRow>
                            <TableRow  className="restriction-row">
                                <TableCell key="reply">Reply</TableCell>
                                <TableCell key="replyValue" style={{color: reply.color}} >{reply.value}</TableCell>
                            </TableRow>
                        </TableBody>
                    </MaterialTable>
                </TableCell>
                {
                    showStatusColumn &&
                    <TableCell key="status">
                        <Switch
                            data-track-id="ai-app-content-restriction-update-status"
                            data-testid="ai-app-content-restriction-update-status"
                            checked={!!model.status}
                            onChange={({target}) => handleStatusUpdate(+target.checked, model)}
                            disabled={!permissionCheckerUtil.checkHasUpdatePermission(permission)}
                            color="primary"
                        />
                    </TableCell>
                }
                {
                    permissionCheckerUtil.hasUpdateOrDeletePermission(permission) &&
                    <TableCell key="action">
                        <ActionButtonsWithPermission
                            permission={permission}
                            onEditClick={() => handlePolicyEdit(model)}
                            onDeleteClick={() => handlePolicyDelete(model)}
                        />
                    </TableCell>
                }
            </TableRow>
        );
    }
    render() {
        const {cPolicies, handlePageChange} = this.props;
        return (
            <Table
                tableClassName="permission-table-globals"
                data={cPolicies}
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
                isRowCustom={true}
                hasElevation={false}
                pageChange={handlePageChange}
                noDataText="No content restriction found."
            />
        )
    }
}

VAIApplicationAccessContentRestriction.defaultProps = {
    showStatusColumn: true,
    permission: {}
}

export default VAIApplicationAccessContentRestriction;