import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react'

import {Grid, Typography, TableCell} from '@material-ui/core';

import f from 'common-ui/utils/f';
import { SearchField } from 'common-ui/components/filters';
import {AddButtonWithPermission, ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import { permissionCheckerUtil } from "common-ui/utils/permission_checker_util";
import Table from "common-ui/components/table";

const Filters = observer(({data, _vState, permission, handleCreate, handleOnChange, handleSearch}) => {
    return (
        <Fragment>
            <Grid container spacing={3}>
                <Grid item xs={12} sm={6}>
                    <Typography data-testid="template-header">Templates ({f.pageState(data).totalElements || 0})</Typography>
                </Grid>
            </Grid>
            <Grid container spacing={3}>
                <SearchField
                    value={_vState.searchValue}
                    colAttr={{xs: 12, sm: 6, 'data-track-id': 'response-template-search'}}
                    inputProps={{'data-testid': 'response-template-search'}}
                    placeholder="Search Response Template"
                    onChange={handleOnChange}
                    onEnter={handleSearch}
                />
                <AddButtonWithPermission
                    permission={permission}
                    colAttr={{xs: 12, sm: 6}}
                    label="Create Template"
                    onClick={handleCreate}
                    data-testid="add-response-template-btn"
                />
            </Grid>
        </Fragment>
    )
})

class VResponseTemplate extends Component {
    getHeaders = () => {
        const {permission} = this.props;

        let headers = [];

        headers.push(...[
            <TableCell key="name" data-testid="response">Response</TableCell>,
            <TableCell key="description" data-testid="description">Description</TableCell>
        ]);

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            headers.push(
                <TableCell key="actions" width="90px" data-testid="actions">Actions</TableCell>
            )
        }

        return headers;
    }
    getRows = (model) => {
        const {permission, handleEdit, handleDelete} = this.props;

        let rows = [];

        rows.push(...[
            <TableCell key="name" data-testid="response">{model.response}</TableCell>,
            <TableCell key="description" data-testid="description">{model.description}</TableCell>
        ]);

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            rows.push(
                <TableCell key="actions" data-testid="actions">
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
                noDataText="No response template created"
            />
        )
    }
}

export {
    Filters,
    VResponseTemplate
}