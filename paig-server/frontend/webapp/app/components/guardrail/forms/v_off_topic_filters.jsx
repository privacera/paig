import React from 'react';

import {TableCell} from '@material-ui/core';

import Table from 'common-ui/components/table';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import {ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import { FormGroupInput } from 'common-ui/components/form_fields';

class VOffTopics extends React.Component {
    getHeaders = () => {
        const {permission} = this.props;

        const headers = [
            <TableCell key="topic">Topic</TableCell>,
            <TableCell key="definition">Definition</TableCell>,
            <TableCell key="sample-phrases">Sample Phrases</TableCell>
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

        let samplePhrases = model.samplePhrases?.join('\n');

        let rows = [
            <TableCell key="topic">{model.topic}</TableCell>,
            <TableCell key="definition">
                <FormGroupInput
                    as="textarea"
                    showLabel={false}
                    disabled={true}
                    variant="standard"
                    rows={1}
                    maxRows={4}
                    InputProps={{disableUnderline: true}}
                    value={model.definition}
                />
            </TableCell>,
            <TableCell key="sample-phrases">
                <FormGroupInput
                    as="textarea"
                    showLabel={false}
                    disabled={true}
                    variant="standard"
                    rows={1}
                    InputProps={{disableUnderline: true, maxRows: 4}}
                    value={samplePhrases}
                />
            </TableCell>
        ];

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
                noDataText="No off topics found"
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
                tableRowAttr={{
                    'data-testid': 'off-topics-table'
                }}
            />
        );
    }
}

export {
    VOffTopics
};