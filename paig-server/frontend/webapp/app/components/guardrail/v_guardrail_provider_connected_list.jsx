import React, {Component} from 'react';

import {TableCell} from '@material-ui/core';

import Table from 'common-ui/components/table';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

class VConnectedGuardrail extends Component {
    getHeaders = () => {
        const {permission} = this.props;

        const headers = [];

        headers.push(...[
            <TableCell key="name">Name</TableCell>,
            <TableCell key="description">Description</TableCell>
        ]);

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            headers.push(
                <TableCell key="action" width="90px">Action</TableCell>
            )
        }

        return headers;
    }
    getRows = (model) => {
        const {permission, handleEdit, handleDelete} = this.props;

        const rows = [];

        rows.push(...[
            <TableCell key="name">{model.name}</TableCell>,
            <TableCell key="description">{model.description}</TableCell>
        ])

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            rows.push(
                <TableCell key="action">
                    <ActionButtonsWithPermission
                        permission={permission}
                        onEditClick={() => handleEdit(model)}
                        onDeleteClick={() => handleDelete(model)}
                    />
                </TableCell>
            )
        }

        return rows;
    }
    render() {
        const {data, handlePageChange} = this.props;

        return (
            <Table
                hasElevation={false}
                data={data}
                getHeaders={this.getHeaders}
                getRowData={this.getRows}
                pageChange={handlePageChange}
                noDataText="No guardrails provider connection"
            />
        )
    }
}

export {
    VConnectedGuardrail
}