import React, {Component} from 'react';

import {TableCell} from '@material-ui/core';

import Table from 'common-ui/components/table';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {Select2} from 'common-ui/components/generic_components';
import {PROMPT_REPLY_ACTION_TYPE} from 'utils/globals';
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

class VSensitiveDataElements extends Component {
    getHeaders = () => {
        const headers = [
            <TableCell key="name">Name</TableCell>,
            <TableCell key="description">Description</TableCell>
        ]

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(this.props.permission)) {
            headers.push(
                <TableCell key="action" width="135px">Action</TableCell>,
                <TableCell key="user-action" width="90px"></TableCell>
            );
        }

        return headers;
    }
    getRowData = (model) => {
        const {permission, handleActionChange, handleRemove} = this.props;

        const rows = [
            <TableCell key="name">{model.name}</TableCell>,
            <TableCell key="description">{model.description}</TableCell>
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
                        data-testid="sensitive-data-action"
                        onChange={(value) => {
                            handleActionChange(value, model);
                        }}
                    />
                </TableCell>,
                <TableCell key="user-action">
                    <ActionButtonsWithPermission
                        permission={permission}
                        hideEdit={true}
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
                noDataText="No elements found"
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
                tableRowAttr={{
                    'data-testid': "sensitive-data-table"
                }}
            />
        )
    }
}

export {
    VSensitiveDataElements
}