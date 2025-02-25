import React from 'react';

import { Box, Paper, Grid, Typography } from '@material-ui/core';

import { FormGroupSwitch } from 'common-ui/components/form_fields';

const VHeaderWithStatus = ({label, description, status, onChange}) => {
    return (
        <Box component={Paper} elevation={0} p="15px">
            <Grid container spacing={1}>
                <Grid item xs={12}>
                    <Typography variant="h6" data-testid="header">{label}</Typography>
                </Grid>
                <Grid item xs={12}>
                    <Typography variant="body2" color="textSecondary" className="w-b-bw" data-testid="description">
                        {description}
                    </Typography>
                </Grid>
                <FormGroupSwitch
                    data-testid="enable-filter"
                    label="Enable filter"
                    name="status"
                    checked={status}
                    onChange={onChange}
                />
            </Grid>
        </Box>
    )
}

export {
    VHeaderWithStatus
}