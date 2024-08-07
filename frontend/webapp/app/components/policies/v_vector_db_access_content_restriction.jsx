import React, {Component} from 'react';

import {TableRow, TableCell, Switch, Chip} from '@material-ui/core';
import Tooltip from '@material-ui/core/Tooltip';
import PersonIcon from '@material-ui/icons/Person';
import PeopleIcon from '@material-ui/icons/People';

import f from 'common-ui/utils/f';
import Table from 'common-ui/components/table';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';

class VVectorDBAccessContentRestriction extends Component {
    getMetaDataDescription = (name) => {
        const {cMetaData} = this.props;
        const foundData = cMetaData && f.models(cMetaData).find(
            data => data.name === name
        );

        return foundData ? foundData.description : '';
    };

    getUserGroups = (model, accessType) => {
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
                    value: accessType === 'allow' ? ['Everyone'] : ['Others']
                });
            } else {
                userGroups.push({
                    label: 'groups',
                    value: model.groups
                });
            }
        }
        return userGroups;
    }
    getHeaders = () => {
        const {permission, showStatusColumn} = this.props;
        const headers = [
            // <TableCell key="description" width="200px">Description</TableCell>,
            <TableCell key="metadataKey" width="200px">Vector DB Metadata</TableCell>,
            <TableCell key="metadataValue" className="tag-value-cell" width="200px">Value</TableCell>,
            <TableCell key="grantedAccess" width="300px">Granted Access</TableCell>,
            <TableCell key="deniedAccess">Denied Access</TableCell>
        ]

        if (showStatusColumn) {
            headers.push(<TableCell key="status" width="70px">Status</TableCell>)
        }

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            headers.push(<TableCell key="action" width="90px">Actions</TableCell>)
        }
        return headers;
    }
    getRowData = (model, i) => {
        const {permission, handleStatusUpdate, handlePolicyEdit, handlePolicyDelete, showStatusColumn} = this.props;

        let allowedUserGroups = this.getUserGroups({users: model.allowedUsers, groups: model.allowedGroups}, 'allow');
        let deniedUserGroups = this.getUserGroups({users: model.deniedUsers, groups: model.deniedGroups});

        const description = this.getMetaDataDescription(model.metadataKey);

        let metaData = model.metadataKey;
        if (model.metadataValue) {
            metaData += ` = ${model.metadataValue}`;
        }

        return (
            <TableRow
                key={model.id || i}
                hover
                data-testid="table-row"
                className="restriction-row"
            >
                {/* <TableCell>{model.description || model.name}</TableCell> */}
                <TableCell>
                    <Tooltip
                        title={description}
                        placement="top"
                        arrow
                    >
                        <Chip
                            className="table-container-chips m-r-xs m-b-xs"
                            size="small"
                            label={model.metadataKey}
                        />
                    </Tooltip>
                </TableCell>
                <TableCell>
                    <Chip
                        className="table-container-chips m-r-xs m-b-xs"
                        size="small"
                        label={model.metadataValue}
                    />
                </TableCell>
                <TableCell>
                    {
                        allowedUserGroups.map((userGroup) => {
                            return userGroup.value.map((value, index) => {
                                return (
                                    <Chip
                                        key={value + index}
                                        className="table-container-chips m-r-xs m-b-xs"
                                        size="small"
                                        label={<span>{userGroup.label == 'users' ? <PersonIcon fontSize="small" color="action" /> : <PeopleIcon fontSize="small" color="action" />} {value}</span>}
                                    />
                                )
                            })
                        })
                    }
                </TableCell>
                <TableCell>
                    {
                        deniedUserGroups.map((userGroup) => {
                            return userGroup.value.map((value, index) => {
                                return (
                                    <Chip
                                        key={value + index}
                                        className="table-container-chips m-r-xs m-b-xs"
                                        size="small"
                                        label={<span>{userGroup.label == 'users' ? <PersonIcon fontSize="small" color="action" /> : <PeopleIcon fontSize="small" color="action" />} {value}</span>}
                                    />
                                )
                            })
                        })
                    }
                </TableCell>
                {
                    showStatusColumn &&
                    <TableCell>
                        <Switch
                            checked={!!model.status}
                            onChange={({target}) => handleStatusUpdate(+target.checked, model)}
                            disabled={!permissionCheckerUtil.checkHasUpdatePermission(permission)}
                            color="primary"
                            data-testid="vector-db-status-switch"
                        />
                    </TableCell>
                }
                {
                    permissionCheckerUtil.hasUpdateOrDeletePermission(permission) &&
                    <TableCell>
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
                noDataText="No RAG contextual data filtering found."
            />
        )
    }
}

VVectorDBAccessContentRestriction.defaultProps = {
    permission: {},
    showStatusColumn: true
}

export default VVectorDBAccessContentRestriction;