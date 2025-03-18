import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';

import {TableCell} from '@material-ui/core';

import f from 'common-ui/utils/f';
import Table from 'common-ui/components/table';
import { FormHorizontal, FormGroupInput, FormGroupCheckbox } from 'common-ui/components/form_fields';
import {PROMPT_REPLY_ACTION_TYPE} from 'utils/globals';

class VSensitiveDataElementForm extends Component {
    getHeaders = () => {
        return [
            <TableCell key="checkbox" data-testid="checkbox-all">
                Select
            </TableCell>,
            <TableCell key="name" data-testid="name">Name</TableCell>,
            <TableCell key="description" data-testid="description">Description</TableCell>
        ]
    }
    getRowData = (model) => {
        return [
            <TableCell key="checkbox">
                <FormGroupCheckbox
                    inputProps={{'data-testid': 'checkbox'}}
                    checked={model.selected}
                    onChange={(e) => {
                        model.selected = e.target.checked;
                    }}
                />
            </TableCell>,
            <TableCell key="name" data-testid="name">{model.name}</TableCell>,
            <TableCell key="description" data-testid="description">{model.description}</TableCell>
        ]
    }
    render() {
        const {cSensitiveData} = this.props;
        return (
            <Table
                hasElevation={false}
                data={cSensitiveData}
                noDataText="No sensitive data found"
                getHeaders={this.getHeaders}
                getRowData={this.getRowData}
            />
        )
    }
}

export {
    VSensitiveDataElementForm
}