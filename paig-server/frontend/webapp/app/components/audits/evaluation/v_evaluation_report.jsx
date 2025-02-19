import React from "react";
import { observer } from "mobx-react";

import { Box, Grid, Paper, Typography } from "@material-ui/core";

import f from 'common-ui/utils/f';
import { Loader, getSkeleton } from "common-ui/components/generic_components";
import RadialBarChart from "components/audits/evaluation/radial_bar_chart";

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

const VEvaluationOverview = observer(({ cEvaluationOverview }) => {
  const evaluationDataList = f.models(cEvaluationOverview) || [];
  return (
    <PaperCard boxProps={{ mb: 2 }}>
      <Loader
        promiseData={cEvaluationOverview}
        loaderContent={getSkeleton("THREE_SLIM_LOADER")}
      >
        <Grid container spacing={2}>
          {evaluationDataList.map((evaluationData, index) => {
            console.log(evaluationData, 'evaluationData')
            return (
              <Grid item md={4} sm={6} xs={12} key={index} className="graph-border-left">
                <Typography className="graph-subtitle" gutterBottom>
                  {evaluationData.categories}
                </Typography>
                <RadialBarChart
                  chartData={evaluationData}
                />
              </Grid>
            );
          })}
        </Grid>
      </Loader>
    </PaperCard>
  );
});

export default VEvaluationOverview;
