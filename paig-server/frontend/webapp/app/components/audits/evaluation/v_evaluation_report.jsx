import React, {Component, Fragment} from "react";
import { observer } from "mobx-react";

import { Box, Grid, Paper, Typography } from "@material-ui/core";
import TableCell from '@material-ui/core/TableCell';

import f from 'common-ui/utils/f';
import Table from "common-ui/components/table";
import RadialBarChart from "components/audits/evaluation/radial_bar_chart";
import { Loader, getSkeleton } from "common-ui/components/generic_components";
import {IncludeExcludeComponent} from 'common-ui/components/v_search_component';

const CATEGORIES = {
  Category: { multi: false, category: "Category", type: "text", key: 'category' },
  Prompt: { multi: false, category: "Prompt", type: "text", key: 'prompt' },
  Response: { multi: false, category: "Response", type: "text", key: 'response' }
}

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
        <TableCell key="category">Category</TableCell>
        <TableCell key="prompt" className='min-width-200'>Prompt</TableCell>
        {responseHeaders}
      </Fragment>
    );
  }

  getRows = (model) => {
    const responseCells = model.responses?.map((response, index) => (
      <TableCell key={`response-${index}`}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '4px' }}>
          <Typography
            style={{
              padding: '4px 8px',
              borderRadius: '4px',
              backgroundColor: response.status === 'PASSED' ? '#d4edda' : response.status === 'FAILED' ? '#f8d7da' : '#fff3cd',
              color: response.status === 'PASSED' ? '#155724' : response.status === 'FAILED' ? '#721c24' : '#856404',
              fontSize: '12px',
              fontWeight: 500
            }}
          >
            {response.status || '--'}
          </Typography>
          {response.response || '--'}
        </div>
      </TableCell>
    )) || [<TableCell key="response-empty">--</TableCell>];
  
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
                console.log(evaluationData, 'evaluationData')
                return (
                  <Grid item md={4} sm={6} xs={12} key={index} className="graph-border-left">
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
                categoriesOptions={Object.values(CATEGORIES)}
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
