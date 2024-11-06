import React, { Component, Fragment } from "react";
import { observer } from "mobx-react";
import { maxBy } from 'lodash';

import { Box, Grid, Paper, Typography } from "@material-ui/core";

import { ApplicationTable } from "containers/dashboard/application_table";
import DataAccessGraph from "components/dashboard/data_access_graph";
import DonutChart from "components/dashboard/donut_chart";
import { Loader, getSkeleton } from 'common-ui/components/generic_components'
import f from "common-ui/utils/f";

const PaperCard = (props) => {
  const { children, boxProps={}, paperProps={} } = props;
  return (
    <Box {...boxProps}>
      <Paper {...paperProps}>
        <Box p={2}>{children}</Box>
      </Paper>
    </Box>
  );
};

const VChartComponent = observer(({title, data, trackId}) => {
  return (
    <Grid item md={4} sm={6} xs={12} className="graph-border-left" data-track-id={trackId}>
      <Typography className="graph-subtitle" gutterBottom>
        {title}
      </Typography>
      <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
        <DonutChart data={f.models(data).length ? f.models(data)[0] : {} } />
      </Loader>
    </Grid>
  )
})

const VUsage = ({cMessageUsage, cSensitiveDataPromptUsage, cSensitiveDataRepliesUsage}) => {
  return (
    <PaperCard boxProps={{mb: 2}} paperProps={{'data-track-id': 'usage'}}>
      <Typography variant="h6" gutterBottom className="graph-title">
        Usage
      </Typography>
      <Grid container spacing={3}>
        <VChartComponent
          title="Messages"
          data={cMessageUsage}
          trackId="messages"
        />
        <VChartComponent
          title="Sensitive Data in Prompts"
          data={cSensitiveDataPromptUsage}
          trackId="sensitive-data-prompts"
        />
        <VChartComponent
          title="Sensitive Data in Replies"
          data={cSensitiveDataRepliesUsage}
          trackId="sensitive-data-replies"
        />
      </Grid>
    </PaperCard>
  )
}

const VSensitiveDataAccess = observer(({data}) => {
  let firstHalf = [];
  let secondHalf = [];

  let models = f.models(data);
  let length = models.length;
  // Find the maximum queries value across all models
  let maxQuery = maxBy(models, 'queries')?.queries || 0;

  if (length) {
    const middleIndex = Math.ceil(length / 2);
    firstHalf = models.slice(0, middleIndex);
    secondHalf = models.slice(middleIndex);
  }

  return (
    <PaperCard boxProps={{my: 2}} paperProps={{'data-track-id': 'sensitive-data-in-applications'}}>
      <Typography variant="h6" gutterBottom className="graph-title" id="sensitive-data-title">
        Sensitive Data Accessed in Applications
      </Typography>
      <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
        <Grid container spacing={3}>
          {
            firstHalf.length > 0
            ? (
              <Fragment>
                <Grid item md={6} xs={12} className="border-right">
                  <ApplicationTable distributionData={firstHalf} maxQuery={maxQuery} />
                </Grid>
                <Grid item md={6} xs={12}>
                  <ApplicationTable distributionData={secondHalf} maxQuery={maxQuery} />
                </Grid>
              </Fragment>
            )
            : (
              <Grid item xs={12}>
                <Box data-testId="noData" display="flex" justifyContent="center" alignItems="center" height="100px">
                  <Typography variant='subtitle1' className="noDataText" color="textSecondary" >No data to display</Typography>
                </Box>
              </Grid>
            )
          }

        </Grid>
      </Loader>
    </PaperCard>
  )
})

const VDataAccess = observer(({data}) => {
  let models = f.models(data);
  let model = models.length > 0 ? models[0] : null;

  return (
    <PaperCard boxProps={{my: 2}} paperProps={{'data-track-id': 'data-access'}}>
      <Typography variant="h6" gutterBottom className="graph-title">
        Data Access
      </Typography>
      <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <DataAccessGraph data={{
                chartData: model?.series || [],
                categories: model?.categories || []
              }}
            />
          </Grid>
        </Grid>
      </Loader>
    </PaperCard>
  );
});

export {
  VUsage,
  VSensitiveDataAccess,
  VDataAccess
}
