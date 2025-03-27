import React, {Component} from 'react';

import {TableCell} from '@material-ui/core';

import Table from 'common-ui/components/table';
import {PROMPT_REPLY_ACTION_TYPE} from 'utils/globals';
import {Select2} from 'common-ui/components/generic_components';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

class VSensitiveDataRegex extends Component {
    getHeaders = () => {
        const headers = [
            <TableCell key="regex" data-testid="regex">Name</TableCell>,
            <TableCell key="pattern" data-testid="pattern">Pattern</TableCell>,
            <TableCell key="description" data-testid="description">Description</TableCell>
        ]

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(this.props.permission)) {
            headers.push(
                <TableCell key="action" width="135px" data-testid="action">Action</TableCell>,
                <TableCell key="user-action" width="90px" data-testid="user-action"></TableCell>
            );
        }

        return headers;
    }
    getRowData = (model, i) => {
        const {permission, handleEdit, handleRemove, handleActionChange} = this.props;

        const rows = [
            <TableCell key="regex" data-testid="regex">{model.name}</TableCell>,
            <TableCell key="pattern" data-testid="pattern">{model.pattern}</TableCell>,
            <TableCell key="description" data-testid="description">{model.description}</TableCell>
        ];

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            rows.push(...[
                <TableCell key="action">
                    <Select2
                        data={Object.values(PROMPT_REPLY_ACTION_TYPE)}
                        labelKey="LABEL"
                        valueKey="VALUE"
                        disableClearable={true}
                        value={model.action}
                        onChange={(value) => {
                            handleActionChange(value, model);
                        }}
                        data-testid="action"
                    />
                </TableCell>,
                <TableCell key="user-action" data-testid="user-action">
                    <ActionButtonsWithPermission
                        permission={permission}
                        onEditClick={() => handleEdit(model, i)}
                        onDeleteClick={() => handleRemove(model)}
                    />
                </TableCell>
            ]);
        }

        return rows;
    }
    render() {
        const {data} = this.props;

        return (
            <Table
                hasElevation={false}
                data={data}
                noDataText="No regex found"
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
                tableRowAttr={{
                    'data-testid': 'sensitive-data-regex-table'
                }}
            />
        )
    }
}

export {
    VSensitiveDataRegex
}