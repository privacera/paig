import React, {Component, Fragment} from 'react';
import {observer} from 'mobx-react'

import {Grid, Accordion, AccordionSummary, AccordionDetails, Typography, TableCell} from '@material-ui/core';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

import CREATE_GUARDRAIL_ICON from 'images/create-guardrail-icon.svg';
import TEST_GUARDRAIL_ICON from 'images/test-guardrail-icon.svg';
import PROTECT_GUARDRAIL_ICON from 'images/protect-guardrail-icon.svg';
import INTERVENE_GUARDRAIL_ICON from 'images/intervene-guardrail-icon.svg';
import f from 'common-ui/utils/f';
import { SearchField } from 'common-ui/components/filters';
import {Select2} from 'common-ui/components/generic_components';
import {AddButtonWithPermission, ActionButtonsWithPermission} from 'common-ui/components/action_buttons';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import Table from 'common-ui/components/table';
import {GUARDRAIL_PROVIDER} from 'utils/globals';


const VInfo = ({icon, label, info}) => {
    return (
        <Grid item xs={12} md={3}>
            <Grid container>
                <Grid item xs={2} md={4} lg={3}>
                    {icon}
                </Grid>
                <Grid item xs={10} md={8} lg={9}>
                    <Typography variant="subtitle2">{label}</Typography>
                    <Typography variant="caption">
                        {info}
                    </Typography>
                </Grid>
            </Grid>
        </Grid>
    )
}

const VGuardrailInfo = () => {
    return (
        <Accordion defaultExpanded={true}>
            <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel1a-content"
                id="panel1a-header"
            >
                <Typography variant="body1">
                    Overview
                </Typography>
            </AccordionSummary>
            <AccordionDetails>
                <Grid container spacing={1}>
                    <VInfo
                        icon={<img src={CREATE_GUARDRAIL_ICON} />}
                        label="Create a Guardrail"
                        info="Define properties such as filters, sensitive information checks, or custom rules to ensure content aligns with guidelines."
                    />
                    <VInfo
                        icon={<img src={TEST_GUARDRAIL_ICON} />}
                        label="Test Guardrail"
                        info="Run tests with different inputs to verify the guardrail performs as expected, refining the configuration if necessary."
                    />
                    <VInfo
                        icon={<img src={PROTECT_GUARDRAIL_ICON} />}
                        label="Protect AI Applications"
                        info="Easily assign guardrails to your AI applications using the dedicated button, or integrate them seamlessly when creating new applications."
                    />
                    <VInfo
                        icon={<img src={INTERVENE_GUARDRAIL_ICON} />}
                        label="Intervene and Audit"
                        info="Violations are handled automatically by modifying, masking, or blocking access to affected data. A detailed log is kept for easy review and compliance tracking."
                    />
                </Grid>
            </AccordionDetails>
        </Accordion>
    )
}

const Filters = observer(({data, _vState, permission, handleCreate, handleOnChange, handleSearch, handleGuardrailProviderChange, handleApplicationChange, cApplications}) => {
    return (
        <Fragment>
            <Grid container spacing={3}>
                <Grid item xs={12} sm={6} data-testid="guardrail-header">
                    <Typography>Guardrails ({f.pageState(data).totalElements || 0})</Typography>
                </Grid>
                <AddButtonWithPermission
                    data-testid="add-guardrail-btn"
                    data-track-id="add-guardrail-btn"
                    permission={permission}
                    colAttr={{xs: 12, sm: 6}}
                    label="Create Guardrail"
                    onClick={handleCreate}
                />
            </Grid>
            <Grid container spacing={3}>
                <SearchField
                    value={_vState.searchValue}
                    colAttr={{xs: 12, sm: 4, 'data-track-id': 'guardrail-search'}}
                    inputProps={{'data-testid': 'guardrail-search'}}
                    placeholder="Search Guardrail"
                    onChange={handleOnChange}
                    onEnter={handleSearch}
                />
                <Grid item xs={12} sm={4}>
                    <Select2
                        value={_vState.providers}
                        data={Object.values(GUARDRAIL_PROVIDER).filter((provider) => provider.NAME !== GUARDRAIL_PROVIDER.PAIG.NAME)}
                        placeholder="Select Guardrail Provider"
                        onChange={handleGuardrailProviderChange}
                        labelKey="LABEL"
                        valueKey="NAME"
                        multiple={true}
                        data-testid="guardrail-provider"
                    />
                </Grid>
                {/* <Grid item xs={12} sm={4}>
                    <Select2
                        value={_vState.applications}
                        data={f.models(cApplications)}
                        placeholder="Select Application"
                        onChange={handleApplicationChange}
                        labelKey="name"
                        valueKey="id"
                        multiple={true}
                    />
                </Grid> */}
            </Grid>
        </Fragment>
    )
})

class VGuardrailListing extends Component {
    getHeaders = () => {
        const {permission} = this.props;

        let headers = [];

        headers.push(...[
            <TableCell key="name" data-testid="name">Name</TableCell>,
            <TableCell key="description" data-testid="description">Description</TableCell>,
            <TableCell key="guardrail_provider" data-testid="guardrail-provider">Guardrail Providers</TableCell>
        ]);
{/*             <TableCell key="applied_application">Applied Application</TableCell>, */}
{/*             <TableCell key="filters_set">Filters set</TableCell> */}

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            headers.push(
                <TableCell key="actions" width="115px" data-testid="action">Actions</TableCell>
            )
        }

        return headers;
    }
    getRows = (model) => {
        const {permission, handleEdit, handleDelete, handlePreview} = this.props;

        let rows = [];

        let provider = Object.values(GUARDRAIL_PROVIDER).find(p => p.NAME === model.guardrailProvider);

        rows.push(...[
            <TableCell key="name" data-testid="name">{model.name}</TableCell>,
            <TableCell key="description" data-testid="description">{model.description}</TableCell>,
            <TableCell key="guardrail_provider" data-testid="guardrail-provider">
                {provider ? provider.LABEL : model.guardrailProvider || GUARDRAIL_PROVIDER.PAIG.LABEL}
            </TableCell>
        ]);
{/*             <TableCell key="applied_application"></TableCell>, */}
{/*             <TableCell key="filters_set"></TableCell> */}

        if (permissionCheckerUtil.hasUpdateOrDeletePermission(permission)) {
            rows.push(
                <TableCell key="actions" data-testid="action">
                    <ActionButtonsWithPermission
                        permission={permission}
                        showPreview={true}
                        onPreviewClick={() => handlePreview(model)}
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
                noDataText="No guardrails created"
            />
        )
    }
}

export {
    VGuardrailInfo,
    VGuardrailListing,
    Filters
}