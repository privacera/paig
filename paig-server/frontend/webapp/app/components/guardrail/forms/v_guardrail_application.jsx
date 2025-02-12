import React, {Component} from 'react';

import {TableCell} from '@material-ui/core';

import Table from 'common-ui/components/table';
import {FormGroupCheckbox} from 'common-ui/components/form_fields';

class VApplications extends Component {
    getHeaders = () => {
        return [
            <TableCell key="checkbox"></TableCell>,
            <TableCell key="name">Name</TableCell>,
            <TableCell key="description">Description</TableCell>
        ];
    }
    getRowData = (model) => {
        const {handleAccountSelection} = this.props;

        return [
            <TableCell key="checkbox" width="30px">
                <FormGroupCheckbox
                    inputProps={{'data-testid': 'checkbox'}}
                    checked={model.selected}
                    onChange={(e) => {
                        model.selected = e.target.checked;
                        handleAccountSelection(model);
                    }}
                />
            </TableCell>,
            <TableCell key="name">{model.name}</TableCell>,
            <TableCell key="description">{model.description}</TableCell>
        ];
    }
    render() {
        const {data} = this.props;

        return (
            <Table
                hasElevation={false}
                data={data}
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
            />
        )
    }
}

export {
    VApplications
};