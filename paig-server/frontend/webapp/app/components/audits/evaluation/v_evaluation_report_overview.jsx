import React, {Component, Fragment} from "react";
import {observer} from "mobx-react";

import {Box, Grid, Paper, Typography, Divider, Chip} from "@material-ui/core";

import f from 'common-ui/utils/f';
import RadialBarChart from "components/audits/evaluation/radial_bar_chart";
import {Loader, getSkeleton} from "common-ui/components/generic_components";
import EventIcon from '@material-ui/icons/Event';
import AccountCircleIcon from '@material-ui/icons/AccountCircle';
import AssignmentIcon from '@material-ui/icons/Assignment';
import ContactsIcon from '@material-ui/icons/Contacts';
import {Utils} from 'common-ui/utils/utils';
import {SEVERITY_MAP, CATEGORY_DESCRIPTIONS} from 'utils/globals';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import EvalDonutChart from "components/audits/evaluation/eval_donut_chart";

const moment = Utils.dateUtil.momentInstance();

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

const getCreateTime = (model) => {
  return model?.create_time ? moment(model.create_time).format(DATE_TIME_FORMATS.DATE_TIME_FORMAT_SHORT) : '--'
}

const getRunAs = (model) => {
  return model?.target_users ? model.target_users.split(',').join(', ') : '--'
}

const getScore = (model) => {
  let total = model.passed + model.failed + model.error;
  const percentage = total ? ((model.passed / total) * 100).toFixed(2) + "%" : "0%";

  return (
    <span>
      {percentage}  ({model.passed}/{total})
    </span>
  )
}

const VEvalReportBasicInfo = ({model}) => {
  return (
    <PaperCard boxProps={{mb: 2}} paperProps={{'data-track-id': 'basic-report-info'}}>
      <Grid container spacing={3}>
        {model?.result?.map((result, index) => (
          <Grid 
            item 
            xs={3}
            className={`border-right ${model?.result?.length > 1 ? 'col-5-grid' : ''}`} 
            alignItems="center"
          >
            <Box justifyContent='center'>
              <Typography variant="subtitle2" className="m-b-xs ellipsize">
                {result.application_name || 'Application Score'}
              </Typography>
              <Typography>
                <AssignmentIcon color="action" className="m-r-xs"/>
                {getScore(result) || '--'}
              </Typography>
            </Box>
          </Grid>
        ))}  

        <Grid item xs={3} className={`border-right ${model?.result?.length > 1 ? 'col-5-grid' : ''}`}  alignItems="center">
          <Box justifyContent='center'>
            <Typography variant="subtitle2" className="m-b-xs">
              Created
            </Typography>
            <Typography>
              <EventIcon color="action" className="m-r-xs"/>
              <span>{getCreateTime(model)}</span>
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={3} className={`border-right ${model?.result?.length > 1 ? 'col-5-grid' : ''}`}  alignItems="center">
          <div>
            <Typography variant="subtitle2" className="m-b-xs">
              Run By
            </Typography>
            <Typography>
              <AccountCircleIcon color="action" className="m-r-xs"/>
              <span>{model?.owner || '--'}</span>
            </Typography>
          </div>
        </Grid>
        <Grid item xs={3} className={` ${model?.result?.length > 1 ? 'col-5-grid' : ''}`} >
          <Typography variant="subtitle2" className={`m-b-xs`} >
            Run As
          </Typography>
          <Typography>
            <ContactsIcon color="action" className="m-r-xs"/>
            <span>{getRunAs(model)}</span>
          </Typography>
        </Grid>
      </Grid>
    </PaperCard>
  )
}

const getCategories = (appsData) => {
  if (!appsData) return [];
  
  // Get all unique categories across all apps
  const allCategories = new Set();
  Object.values(appsData).forEach(appData => {
    Object.keys(appData.categories || {}).forEach(cat => allCategories.add(cat));
  });
  
  // Calculate pass/total ratio for each category
  const categoriesWithRatio = Array.from(allCategories).map(category => {
    const appValues = Object.values(appsData).map(app => {
      const catData = app.categories?.[category] || {};
      return (catData.pass || 0) / (catData.total || 1);
    });
    
    // Calculate the average ratio for the category
    const avgRatio = appValues.reduce((sum, val) => sum + val, 0) / appValues.length;
    
    return {
      name: category,
      diffScore: avgRatio
    };
  });
  
  return categoriesWithRatio
    .sort((a, b) => a.diffScore - b.diffScore);
}

@observer
class VEvaluationReportOverview extends Component {

  render() {
    const { _vState, parent_vState, cEvaluationOverview, data, handlePageChange, handleSearchByField, handleTabSelect } = this.props;
    const evaluationDataList = f.models(cEvaluationOverview) || [];
    return (
      <Fragment>
        <VEvalReportBasicInfo model={_vState.reportData}/>

        <Grid container spacing={2} className="m-b-sm"> 
          {/* Overall Score chart */}
          <Grid item lg={5} md={6} sm={12} xs={12} >
            <PaperCard>
              <Loader
                promiseData={cEvaluationOverview}
                loaderContent={getSkeleton("THREE_SLIM_LOADER")}
              >
                <Grid container spacing={2}>
                  {evaluationDataList.map((evaluationData, index) => {
                    return (
                      <Fragment>
                        <Grid item md={12} sm={12}>
                          <Typography className="graph-title inline-block" gutterBottom>
                            Overall Score
                          </Typography>
                        </Grid>
                        <RadialBarChart
                          chartData={evaluationData}
                        />
                      </Fragment>
                    );
                  })}
                </Grid>
              </Loader>
            </PaperCard>
          </Grid>
          {/* Severity Metrics */}
          <Grid item lg={7} md={6} sm={12} xs={12} className="eval-metrics-container">
            <Grid container spacing={3} className="eval-metrics-box">
              {Object.entries(SEVERITY_MAP).map(([severityKey, data], index) => (
                <Grid item md={6} sm={12} key={index} className="eval-metrics">
                  <Paper data-track-id="top-users">
                    {/* Header */}
                    <Box sx={{ backgroundColor: data.COLOR, p: 1}}>
                      <Typography variant="subtitle1" className="graph-title">
                        {data.LABEL}
                      </Typography>
                    </Box>
                    {/* Content area */}
                    <Box display="flex" p={2} style={{ gap: '10px' }}>
                      {Object.keys(_vState?.reportSeverity || {}).length === 0 ? (
                        // If reportSeverity is empty, show a single box with 0
                        <Box
                          flex={1}
                          justifyContent="space-between"
                          alignItems="center"
                          mb={1}
                          className="pointer"
                          onClick={() => handleTabSelect(1, [{category: 'Severity', operator: 'is', value: severityKey}])}
                        >
                          <Typography variant="body1" color="textPrimary" className="graph-title" >
                            0
                          </Typography>
                        </Box>
                      ) : (
                        // If reportSeverity is not empty, map over its entries
                        Object.entries(_vState?.reportSeverity || {}).map(([applicationName, severities], idx, array) => (
                          <>
                            <Box
                              key={applicationName}
                              flex={1}
                              justifyContent="space-between"
                              alignItems="center"
                              mb={1}
                              className="pointer"
                              onClick={() => handleTabSelect(1, [{category: 'Severity', operator: 'is', value: severityKey}])}
                            >
                              {array.length > 1 && (
                                <Typography variant="subtitle1" color="textSecondary">
                                  {applicationName}
                                </Typography>
                              )}
                              <Typography variant="body1" color="textPrimary" className="graph-title" >
                                {severities?.[severityKey] || 0}
                              </Typography>
                            </Box>
                            {idx < array.length - 1 && (
                              <Divider orientation="vertical" flexItem />
                            )}
                          </>
                        ))
                      )}
                    </Box>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Grid>
        </Grid>

        <Grid container spacing={2} className="stretch-eval-card">  
          {/* Severity Donut chart and Category table */}
          {Object.entries(_vState.reportStats || {}).map(([category, appsData]) => (
            <Grid item
              xs={12}
              sm={Object.keys(appsData || {}).length === 1 ? 6 : 12}
              key={category}
            >
              <PaperCard boxProps={{ mb: 2 }} style={{ height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  {category === "null" || !category ? "Custom" : category}
                </Typography>
                <Typography variant="body2" color="textSecondary" gutterBottom className="min-height-50">
                  {CATEGORY_DESCRIPTIONS[category] || CATEGORY_DESCRIPTIONS["Custom"]}
                </Typography>
                <Grid container spacing={3}>
                  <Grid item lg={6} md={6} sm={12} xs={12} >     
                  <Grid container spacing={3}>
                      {Object.entries(appsData || {}).map(([appName, appData], index, array) => (
                
                        <Grid item lg={Object.keys(appsData || {}).length === 1 ? 12 : 6} md={Object.keys(appsData || {}).length === 1 ? 12 : 6} sm={12} xs={12} >
                        <Box key={appName} flex="1 0 200px">
                          <Typography variant="subtitle1" color="textSecondary">
                            {array.length === 1 ? "Overall Pass Rate" : appName}
                          </Typography>
                          {appData.severity && SEVERITY_MAP[appData.severity] ? (
                            <Chip
                              className="table-container-chips m-r-xs m-b-xs"
                              size="small"
                              label={SEVERITY_MAP[appData.severity].LABEL}
                              style={{
                                backgroundColor: SEVERITY_MAP[appData.severity].COLOR
                              }}
                            />
                          ) : (
                            <Box style={{ height: '24px' }}/>
                          )}
                          {/* Donut chart for each app */}
                          <EvalDonutChart
                            appName={appName}
                            data={appData}
                          />
                        </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </Grid>
                  {/* <Divider orientation="vertical" flexItem /> */}
                  <Grid item lg={6} md={6} sm={12} xs={12}>
                    <Typography variant="subtitle1" color="textSecondary">
                      Results overview
                    </Typography>
                    <Box component="table" className="results-table">
                      {/* Table Header */}
                      <thead className="results-table-header">
                        <tr>
                          <Typography component="th" className="category-column">
                            Category
                          </Typography>
                          {Object.keys(appsData || {}).length === 1 ? (
                            <Typography component="th" className="table-header-cell">
                              Ratio
                            </Typography>
                          ) : (
                            Object.keys(appsData || {}).map(appName => (
                              <Typography key={appName} component="th" className="table-header-cell">
                                {appName}
                              </Typography>
                            ))
                          )}
                        </tr>
                      </thead>
                      {/* Scrollable Table Body */}
                      <Box component="tbody" className="results-table-body">
                        {getCategories(appsData).map((categoryItem) => (
                          <tr key={categoryItem.name}>
                            <td>
                              <Chip
                                className="eval-chips m-r-xs m-b-xs"
                                size="small"
                                label={categoryItem.name}
                                title={categoryItem.name}
                              />
                            </td>
                            {Object.values(appsData || {}).map((appData, idx) => (
                              <Typography key={idx} component="td" className="table-body-cell">
                                {appData.categories?.[categoryItem.name]?.pass || 0} / {appData.categories?.[categoryItem.name]?.total || 0}
                              </Typography>
                            ))}
                          </tr>
                        ))}
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </PaperCard>
            </Grid>
          ))}
        </Grid>
        
      </Fragment>
    );
  };
}

export default VEvaluationReportOverview;