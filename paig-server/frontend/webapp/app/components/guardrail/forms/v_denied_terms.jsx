import React, {Component} from 'react';

import {TableCell} from '@material-ui/core';

import Table from 'common-ui/components/table';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';

class VDeniedTerms extends Component {
    getHeaders = () => {
        const {permission} = this.props;

        const headers = [
            <TableCell key="terms">Term</TableCell>,
            <TableCell key="phrases-and-keywords">Phrases and keywords</TableCell>,
        ];

        if (permissionCheckerUtil.checkHasDeletePermission(permission)) {
            headers.push(
                <TableCell key="user-action" width="90px">Actions</TableCell>
            );
        }

        return headers;
    }
    getRowData = (model, i) => {
        const {permission, handleEdit, handleRemove} = this.props;

        let rows = [
            <TableCell key="terms">{model.term}</TableCell>,
            <TableCell key="phrases-and-keywords">
                {model.keywords?.join(', ')}
            </TableCell>,
        ]

        if (permissionCheckerUtil.checkHasDeletePermission(permission)) {
            rows.push(
                <TableCell key="user-action">
                    <ActionButtonsWithPermission
                        permission={permission}
                        onEditClick={() => handleEdit(model, i)}
                        onDeleteClick={() => handleRemove(model)}
                    />
                </TableCell>
            );
        }

        return rows;
    }
    render() {
        const {data} = this.props;
        return (
            <Table
                hasElevation={false}
                data={data}
                noDataText="No terms found"
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
            />
        );
    }
}

export default VDeniedTerms;