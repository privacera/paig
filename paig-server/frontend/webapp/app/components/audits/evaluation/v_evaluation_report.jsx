import React, {Component, Fragment} from "react";
import {observer} from "mobx-react";

import {Box, Grid, Paper, Typography, TableCell} from "@material-ui/core";

import f from 'common-ui/utils/f';
import Table from "common-ui/components/table";
import {EVAL_REPORT_CATEGORIES} from 'utils/globals';
import RadialBarChart from "components/audits/evaluation/radial_bar_chart";
import {Loader, getSkeleton} from "common-ui/components/generic_components";
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';

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

@observer
class VEvaluationOverview extends Component {

  getHeaders = () => {
    const { data } = this.props;
    const dataModels = f.models(data) || [];
    const responseHeaders = dataModels[0]?.responses?.map((response, index) => (
      <TableCell key={`response-${index}`}>{`Response (${response.application_name})`}</TableCell>
    )) || [];

    return (
      <Fragment>
        <TableCell key="category" className='min-width-100'>Category</TableCell>
        <TableCell key="prompt" className='min-width-200'>Prompt</TableCell>
        {responseHeaders}
      </Fragment>
    );
  }

  // Align responses with the respective application_name columns
  getRows = (model) => {
    const { data } = this.props;
    const dataModels = f.models(data) || [];
    const appNames = dataModels[0]?.responses?.map(response => response.application_name) || [];

    const responseCells = appNames.map((appName, index) => {
      const appResponse = model.responses?.find(response => response.application_name === appName);
      return (
        <TableCell key={`response-${appName}-${index}`}>
          {appResponse ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '4px' }}>
              <Typography
                style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  backgroundColor: appResponse.status === 'PASSED' ? '#d4edda' :
                    appResponse.status === 'FAILED' ? '#f8d7da' : '#fff3cd',
                  color: appResponse.status === 'PASSED' ? '#155724' :
                    appResponse.status === 'FAILED' ? '#721c24' : '#856404',
                  fontSize: '12px',
                  fontWeight: 500
                }}
              >
                {appResponse.status || '--'}
              </Typography>
              {appResponse.response || '--'}
              {(appResponse.status === 'FAILED' || appResponse.status === 'ERROR') && appResponse.failure_reason && (
                <Box
                  style={{
                    padding: '8px',
                    borderRadius: '4px',
                    backgroundColor: appResponse.status === 'FAILED' ? '#f8d7da' : '#FFFAEB',
                  }}
                >
                  <Typography
                    style={{
                      fontSize: '12px',
                      fontWeight: 500
                    }}
                  >
                    {appResponse.failure_reason}
                  </Typography>
                </Box>
              )}
            </div>
          ) : (
            '--'
          )}
        </TableCell>
      );
    });

    return (
      <Fragment>
        <TableCell key="category">
          {model.responses?.[0]?.category || '--'}
        </TableCell>
        <TableCell key="prompt">
          {model.prompt || '--'}
        </TableCell>
        {responseCells}
      </Fragment>
    );
  };

  render() {
    const { _vState, cEvaluationOverview, data, handlePageChange, handleSearchByField } = this.props;
    const evaluationDataList = f.models(cEvaluationOverview) || [];
    return (
      <Fragment>
        <PaperCard boxProps={{ mb: 2 }}>
          <Loader
            promiseData={cEvaluationOverview}
            loaderContent={getSkeleton("THREE_SLIM_LOADER")}
          >
            <Grid container spacing={2}>
              {evaluationDataList.map((evaluationData, index) => {
                return (
                  <Grid item md={4} sm={6} xs={12} key={index} className="graph-border-left m-l-md">
                    <Typography className="graph-title" gutterBottom>
                      Evaluation Overview
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
        <PaperCard boxProps={{ mb: 2 }}>
          <Typography className="graph-title" gutterBottom>
            Results
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={6} sm={6} md={6} lg={6}>
              <IncludeExcludeComponent
                _vState={_vState}
                categoriesOptions={Object.values(EVAL_REPORT_CATEGORIES)}
                onChange={handleSearchByField}
              />
            </Grid>
          </Grid>
          <Table
            className="eval-table"
            tableClassName="eval-table"
            data={data}
            getHeaders={this.getHeaders}
            getRowData={this.getRows}
            hasElevation={false}
            pageChange={handlePageChange}
          />
        </PaperCard>
      </Fragment>
    );
  };
}

export default VEvaluationOverview;
