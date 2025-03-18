import React, {Component} from 'react';
import {observer} from 'mobx-react';

import {Accordion, AccordionSummary, AccordionDetails, Typography, Grid, Paper} from '@material-ui/core';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

import {GUARDRAIL_PROVIDER} from 'utils/globals';

const ProviderCard = ({ provider, onClick }) => (
    <Grid
        item
        className="m-b-sm app-panel-card-width pointer"
        key={provider.NAME}
        onClick={() => onClick(provider)}
    >
        <Paper elevation={2} className="application-widget" aria-label={provider.LABEL}>
            <div className="halo app-icon pointer">
                {
                    provider.IMG_URL &&
                    <img className={"services-logo " + provider.NAME} src={provider.IMG_URL} alt="service-logo" />
                }
            </div>
        </Paper>
        <div className="m-t-xs appstore-landing-label text-center">
            {provider.LABEL}
        </div>
    </Grid>
);

const ProviderAccordion = ({ title, providers, onProviderClick, noProviderMessage, accordianSummaryProps={}, accordianDetailProps={} }) => (
    <Accordion defaultExpanded>
        <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls={`${title}-content`}
            id={`${title}-header`}
            {...accordianSummaryProps}
        >
            <Typography variant="body2">{`${title} (${providers.length})`}</Typography>
        </AccordionSummary>
        <AccordionDetails {...accordianDetailProps}>
            <Grid container spacing={3} className="appstore-landing-container">
                {providers.length > 0 ? (
                    providers.map((provider) => (
                        <ProviderCard key={provider.NAME} provider={provider} onClick={onProviderClick} />
                    ))
                ) : (
                    <Grid item xs={12}>
                        <Typography variant="body2">{noProviderMessage}</Typography>
                    </Grid>
                )}
            </Grid>
        </AccordionDetails>
    </Accordion>
);

const ConnectedProvider = observer(({ _vState, handleConnectedProviderClick }) => {
    const providers = Object.values(GUARDRAIL_PROVIDER).filter((provider) =>
        _vState.connectedProvider.includes(provider.NAME)
    );

    return (
        <ProviderAccordion
            title="Connected Providers"
            providers={providers}
            onProviderClick={handleConnectedProviderClick}
            noProviderMessage="No Providers Connected"
            accordianSummaryProps={{
                'data-testid': 'connected-provider-summary'
            }}
            accordianDetailProps={{
                'data-testid': 'connected-provider-details'
            }}
        />
    );
});

const AvailableProviders = observer(({ _vState, handleProviderClick }) => {
    const providers = Object.values(GUARDRAIL_PROVIDER).filter(
        (provider) => provider.NAME !== GUARDRAIL_PROVIDER.PAIG.NAME && !_vState.connectedProvider.includes(provider.NAME)
    );

    return (
        <ProviderAccordion
            title="Available Providers"
            providers={providers}
            onProviderClick={handleProviderClick}
            noProviderMessage="No Providers Available"
            accordianSummaryProps={{
                'data-testid': 'available-provider-summary'
            }}
            accordianDetailProps={{
                'data-testid': 'available-provider-details'
            }}
        />
    );
});

export {
    ConnectedProvider,
    AvailableProviders
}