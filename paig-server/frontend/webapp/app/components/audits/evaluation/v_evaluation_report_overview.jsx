import React, {Component, Fragment} from "react";
import {observer} from "mobx-react";

import {Box, Grid, Paper, Typography} from "@material-ui/core";

import f from 'common-ui/utils/f';
import RadialBarChart from "components/audits/evaluation/radial_bar_chart";
import {Loader, getSkeleton} from "common-ui/components/generic_components";
import EventIcon from '@material-ui/icons/Event';
import AccountCircleIcon from '@material-ui/icons/AccountCircle';
import ContactsIcon from '@material-ui/icons/Contacts';
import {Utils} from 'common-ui/utils/utils';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';

const moment = Utils.dateUtil.momentInstance();

const SEVERITY_MAP = {
  "CRITICAL": {'label': 'Severe Failure', 'color': '#E101014D'},
  "HIGH": {'label': 'High Conern', 'color': '#FFCAB3'},
  "MEDIUM": {'label': 'Moderate Conern', 'color': '#FFEDB2'},
  "LOW": {'label': 'Low Concern', 'color': '#B2F0D6'}
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

const getCreateTime = (model) => {
  return model?.create_time ? moment(model.create_time).format(DATE_TIME_FORMATS.DATE_TIME_FORMAT_SHORT) : '--'
}

const getRunAs = (model) => {
  return model?.target_users ? model.target_users.split(',').join(', ') : '--'
}

const VEvalReportBasicInfo = ({model}) => {
  return (
    <PaperCard boxProps={{mb: 2}} paperProps={{'data-track-id': 'basic-report-info'}}>
      <Grid container spacing={3}>
        <Grid item md={4} sm={6} xs={12} className="border-right" alignItems="center">
              <Box justifyContent='center'>
              <Typography  variant="subtitle2" className="m-b-xs" >
                Created
              </Typography>
              <Typography>
              <EventIcon color="action" className="m-r-xs"/>
              <span>{getCreateTime(model)}</span>
              </Typography>
              </Box>
        </Grid>
        <Grid item md={4} sm={6} xs={12} className="border-right" alignItems="center">
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
        <Grid item md={4} sm={6} xs={12}>
              <Typography variant="subtitle2" className="m-b-xs">
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

@observer
class VEvaluationReportOverview extends Component {

  render() {
    const { _vState, parent_vState, cEvaluationOverview, data, handlePageChange, handleSearchByField } = this.props;
    const evaluationDataList = f.models(cEvaluationOverview) || [];
    return (
      <Fragment>
        <VEvalReportBasicInfo model={_vState.reportData}/>
        <Grid container spacing={3}>
            <Grid item spacing={3} md={5} sm={5} xs={12}>
                  <PaperCard boxProps={{ mb: 2 }}>
                    <Loader
                      promiseData={cEvaluationOverview}
                      loaderContent={getSkeleton("THREE_SLIM_LOADER")}
                    >
                      <Grid container spacing={2}>
                        {evaluationDataList.map((evaluationData, index) => {
                          return (
                            <Grid item md={4} sm={4} xs={12} key={index} className="graph-border-left m-l-md">
                              <Typography className="graph-title" gutterBottom>
                                Overall Score
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
            </Grid>
            <Grid item md={7} sm={12}>
              <Grid container spacing={3}>
                  {Object.entries(SEVERITY_MAP).map(([severityKey, data], index) => (
                    <Grid item md={6} sm={12} key={index}>
                      <Paper data-track-id="top-users">
                        {/* Header */}
                          <Box sx={{ backgroundColor: data.color, p: 1}}>
                            <Typography variant="bod1">
                              {data.label}
                            </Typography>
                          </Box>
                          {/* Content area */}
                          <Box display="flex" justifyContent="space-between" alignItems="center" p={2}>
                          </Box>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
            </Grid>
        </Grid>
      </Fragment>
    );
  };
}

export default VEvaluationReportOverview;