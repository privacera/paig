import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react';

import {TableCell} from '@material-ui/core';

import Table from 'common-ui/components/table';
import {Checkbox} from 'common-ui/components/filters';
import {Select2} from 'common-ui/components/generic_components';

const HighMediumLowComponent = observer(({model, handleStrengthChange, handleStrengthResponseChange, handleCustomizeReplyChange}) => {
    const highMediumLowData = [
        {label: 'High', value: 'high'},
        {label: 'Medium', value: 'medium'},
        {label: 'Low', value: 'low'}
    ];

    return (
        <Fragment>
            <Select2
                value={model.filterStrengthPrompt}
                data={highMediumLowData}
                placeholder="Select Guardrail Strength"
                disableClearable={true}
                data-testid="guardrail-strength"
                onChange={val => handleStrengthChange(val, model)}
                multiple={false}
            />
            <Checkbox
                fields={model}
                attr="customReply"
                labelText="Customize Reply"
                data-testid="custom-reply"
                onChange={e => handleCustomizeReplyChange(e, model)}
            />
            {
                model.customReply &&
                <Select2
                    value={model.filterStrengthResponse}
                    data={highMediumLowData}
                    placeholder="Select Guardrail Strength"
                    data-testid="guardrail-strength-response"
                    disableClearable={true}
                    onChange={val => handleStrengthResponseChange(val, model)}
                    multiple={false}
                />
            }
        </Fragment>
    )
})

class VContentModeration extends Component {
    getHeaders = () => {
        return [
            <TableCell key="status" data-testid="status">Status</TableCell>,
            <TableCell key="category" data-testid="category">Category</TableCell>,
            <TableCell key="description" data-testid="description">Description</TableCell>,
            <TableCell key="guardrail-strength" data-testid="guardrail-strength" width="175px">Guardrail Strength</TableCell>
        ]
    }
    getRowData = (model) => {
        const {handleContentSelection, handleStrengthChange, handleStrengthResponseChange, handleCustomizeReplyChange} = this.props;
        return [
            <TableCell key="status">
                <Checkbox
                    fields={model}
                    attr="filterSelected"
                    data-testid="status"
                    onChange={e => {
                        handleContentSelection(model, e.target.checked);
                    }}
                />
            </TableCell>,
            <TableCell key="category" data-testid="category">
                {model.category}
            </TableCell>,
            <TableCell key="description" data-testid="description">
                {model.description}
            </TableCell>,
            <TableCell key="guardrail-strength">
                {
                    model.strengthType === 'high_medium_low'
                    ?
                        <HighMediumLowComponent
                            model={model}
                            handleStrengthChange={handleStrengthChange}
                            handleStrengthResponseChange={handleStrengthResponseChange}
                            handleCustomizeReplyChange={handleCustomizeReplyChange}
                        />
                    : null
                }
            </TableCell>
        ]
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
    VContentModeration
}