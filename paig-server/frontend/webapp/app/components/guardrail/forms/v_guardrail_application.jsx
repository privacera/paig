import React, {Component, Fragment} from 'react';

import {TableCell, Tooltip} from '@material-ui/core';

import Table from 'common-ui/components/table';
import {FormGroupCheckbox} from 'common-ui/components/form_fields';

class VApplications extends Component {
    getHeaders = () => {
        return [
            <TableCell key="checkbox" width="30px"></TableCell>,
            <TableCell key="name">Name</TableCell>,
            <TableCell key="description">Description</TableCell>
        ];
    }
    getRowData = (model) => {
        const {handleAccountSelection} = this.props;

        const Wrapper = model.disabled ? Tooltip : Fragment;
        const wrapperProps = model.disabled ? {arrow: true, placement: 'top', title: `This application is assigned to guardrail "${model.guardrails.join(', ')}"` } : {};

        return [
            <TableCell key="checkbox">
                <Wrapper {...wrapperProps}>
                    <div>
                        <FormGroupCheckbox
                            inputProps={{'data-testid': 'checkbox'}}
                            disabled={model.disabled}
                            checked={model.selected}
                            onChange={(e) => {
                                model.selected = e.target.checked;
                                handleAccountSelection(model);
                            }}
                        />
                    </div>
                </Wrapper>
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