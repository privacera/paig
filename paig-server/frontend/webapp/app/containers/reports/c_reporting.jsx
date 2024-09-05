import React, { Component, Fragment, createRef } from 'react';

import Grid from '@material-ui/core/Grid';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography';
import withStyles from '@material-ui/core/styles/withStyles';

/* other project imports */
import { REPORT_DETAILS } from 'utils/globals';
import hashHistory from 'common-ui/routers/history';
import BaseContainer from 'containers/base_container';
import { GenAIReportUtil } from 'components/reports/gen_ai_report_util';
import { FEATURE_PERMISSIONS } from 'utils/globals';
// import { configProperties } from 'utils/config_properties';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import CUsersGenAIApplicationSummary from 'containers/reports/c_users_gen_ai_application_summary';
import CSensitiveDataSummary from 'containers/reports/c_sensitive_data_report_summary';
import CUsersWhoViewedUserContentSummary from 'containers/reports/c_users_who_viewed_content_summary';

export const REPORTS_TYPE = {
  [REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME]: {
    name: REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME,
    label: REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.LABEL,
    type: REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME,
    view: CUsersGenAIApplicationSummary,
    saveReportSupport: false,
    supportSchedule: false,
    downloadSupport: true,
    exportCSVSupport: false,
    description: REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.DESCRIPTION,
    downloadFileName: REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.DOWNLOAD_FILE_NAME
  },
  [REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.NAME]: {
    name: REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.NAME,
    label: REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.LABEL,
    type: REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.NAME,
    view: CSensitiveDataSummary,
    saveReportSupport: false,
    supportSchedule: false,
    downloadSupport: true,
    exportCSVSupport: false,
    description: REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.DESCRIPTION,
    downloadFileName: REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.DOWNLOAD_FILE_NAME
  },
  // TODO: [PAIG-2025] Uncommnets to see Content Viewing Compliance Report when Admin Audits enables
  // [REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.NAME]: {
  //   name: REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.NAME,
  //   label: REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.LABEL,
  //   type: REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.NAME,
  //   view: CUsersWhoViewedUserContentSummary,
  //   saveReportSupport: true,
  //   supportSchedule: false,
  //   downloadSupport: true,
  //   exportCSVSupport: false,
  //   description: REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.DESCRIPTION,
  //   downloadFileName: REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.DOWNLOAD_FILE_NAME
  // }
}

export const findReportTypeFor = (reportTypeName = '') => {
  let rType = Object.values(REPORTS_TYPE).find(reportType => reportTypeName == reportType.name);
  if (rType) {
    return rType.type;
  } else {
    return REPORTS_TYPE[REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME].type;
  }
}

export const findReportTypeName = (reportTypeName = '') => {
  let type = findReportTypeFor(reportTypeName);
  if (type && REPORTS_TYPE[type]) {
    return REPORTS_TYPE[type].name;
  }
  return null;
}

export const redirectToReport = (reportType, configId = 'new') => {
  hashHistory.push(`/reports/${reportType}/${configId}`);
}

export const replaceCurrentUrl = (reportType, configId) => {
  hashHistory.replace(`/reports/${reportType}/${configId}`);
}

export const supportScheduleReport = (reportType) => {
  let report = REPORTS_TYPE[reportType];
  if (report) {
    return report.supportSchedule;
  }
}

let GROUP_REPORTS = [];

class CReporting extends Component {
  state = {
    view: '',
    configId: undefined,
    uploadPdf: false
  }
  constructor(props) {
    super(props);
    this.setReportsGroups();
    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.PORTAL.REPORTS.PROPERTY);
    // const supportSchedule = configProperties.isReportsSchedulingEnable();
    // if (!supportSchedule) {
    //   for(const reportType in REPORTS_TYPE) {
    //     const report = REPORTS_TYPE[reportType];
    //     if (report.supportSchedule) {
    //       report.supportSchedule = supportSchedule;
    //     }
    //   }
    // }
    const hasUpdatePerm = permissionCheckerUtil.checkHasUpdatePermission(this.permission);
    const hasExportPerm = permissionCheckerUtil.checkHasExportPermission(this.permission);
    for (const reportType in REPORTS_TYPE) {
      const report = REPORTS_TYPE[reportType];
      if (!hasUpdatePerm) {
        report.saveReportSupport = false;
      }
      if (!hasExportPerm) {
        report.downloadSupport = false;
        report.exportCSVSupport = false;
      }
    }
  }

  setReportsGroups = () => {
    GROUP_REPORTS = [];
    GROUP_REPORTS.push(...[{
      name: 'Gen AI Applications',
      reports: [
        REPORTS_TYPE[REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME], 
        REPORTS_TYPE[REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.NAME],
        // TODO: [PAIG-2025] Uncommnets to see Content Viewing Compliance Report when Admin Audits enables
        // REPORTS_TYPE[REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.NAME]
      ]
    }]);
  }

  componentDidMount = () => {
    if (!this.props.match.params) {
      return;
    }
    this.setConfigIdAndReportType();
  }

  setConfigIdAndReportType = async () => {
    let configId = this.props.match.params.configId;
    let reportType = this.props.match.params.reportType;
    const { state } = this;

    if (configId && !reportType) {
      const reportUtil = new GenAIReportUtil();
      reportUtil.setConfigId(configId);
      // let config = await reportUtil.fetchConfig();
      if (config) {
        reportType = findReportTypeFor(Utils.parseJSON(config.paramJson).reportType);
      }
      state.uploadPdf = true;
    }

    let rType = REPORTS_TYPE[reportType];
    if (rType) {
      state.view = rType.name;
    }
    if (configId) {
      if (configId == 'new') {
        state.configId = '';
      } else {
        state.configId = configId;
      }
    }
    this.setState(this.state);
  }

  handleLoad = (view, configId) => {
    this.state.view = view;
    this.state.configId = configId;
    this.setState(this.state);
  }

  handleSelect = (reportType) => {
    hashHistory.push(`/built_in_reports/${reportType}/new`);
  }

  handleBack = () => {
    this.state.view = '';
    this.state.configId = undefined;
    this.setState(this.state);
  }

  resetConfig = () => {
    this.state.configId = undefined;
    this.setState(this.state);
  }

  handleRefresh = () => {
    this.activeReportRef?.handleRefresh?.();
  }

  render() {
    let view = null;
    let showBackButton = false;
    let reportType = null;
    const showRefresh = this.props.match?.params?.reportType || false;
    switch (this.state.view) {
      case REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME:
        reportType = REPORTS_TYPE[REPORT_DETAILS.USER_GEN_AI_APPLICATION_SUMMARY.NAME];
        showBackButton = true;
        view = <CUsersGenAIApplicationSummary ref={ ref => this.activeReportRef = ref} reportTypeObj={reportType} configId={this.state.configId} resetConfig={this.resetConfig} uploadPdf={this.state.uploadPdf}
          saveReportSupport={reportType.saveReportSupport} supportScheduleReport={reportType.supportSchedule} downloadSupport={reportType.downloadSupport} exportCSVSupport={reportType.exportCSVSupport}
        />
        break;
      case REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.NAME:
          reportType = REPORTS_TYPE[REPORT_DETAILS.SENSITIVE_DATA_GEN_AI_SUMMARY.NAME];
          showBackButton = true;
          view = <CSensitiveDataSummary ref={ ref => this.activeReportRef = ref} reportTypeObj={reportType} configId={this.state.configId} resetConfig={this.resetConfig} uploadPdf={this.state.uploadPdf}
            saveReportSupport={reportType.saveReportSupport} supportScheduleReport={reportType.supportSchedule} downloadSupport={reportType.downloadSupport} exportCSVSupport={reportType.exportCSVSupport}
          />
          break;
      // TODO: [PAIG-2025] Uncommnets to see Content Viewing Compliance Report when Admin Audits enable
      // case REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.NAME:
      //   reportType = REPORTS_TYPE[REPORT_DETAILS.USERS_WHO_VIEWED_USER_CONTENT_SUMMARY.NAME];
      //     showBackButton = true;
      //     view = <CUsersWhoViewedUserContentSummary ref={ ref => this.activeReportRef = ref} reportTypeObj={reportType} configId={this.state.configId} resetConfig={this.resetConfig} uploadPdf={this.state.uploadPdf}
      //       saveReportSupport={reportType.saveReportSupport} supportScheduleReport={reportType.supportSchedule} downloadSupport={reportType.downloadSupport} exportCSVSupport={reportType.exportCSVSupport}
      //     />
      //     break;
      default:
        showBackButton = false;
        view = <FieldSetReportWidget onSelect={this.handleSelect} />
    }
    return (
      <BaseContainer showRefresh={showRefresh} showBackButton={showBackButton} handleRefresh={this.handleRefresh}>
        {view}
      </BaseContainer>
    )
  }
}

CReporting.defaultProps = {
  _vName: 'c_reporting',
};

const ReportCardView = withStyles({
  reportCard: {
    height: "100%"
  }
})(({ report, onSelect, classes }) => {
  return (
    <Grid item md={6} xs={12} data-track-id={report.name}>
      <Card classes={{ root: classes.reportCard }}>
        <CardContent>
          <Typography gutterBottom variant="h6" color="textSecondary">
            {report.label}
          </Typography>
          <Typography gutterBottom variant="body2" color="textSecondary" component="p">
            {report.description}
          </Typography>
          <a onClick={e => onSelect && onSelect(report.type)}>View Report</a>
        </CardContent>
      </Card>
    </Grid>
  )
})

const FieldSetReportWidget = ({ onSelect }) => {
  return (
    <Fragment>
      {
        GROUP_REPORTS.map((report, i) => report.reports.length ? (
          // <fieldset className="reports-fieldset" key={i}>
          //   <legend><Typography variant="body1" component="span">{report.name}</Typography></legend>
          <Grid container spacing={3} className="premade-reportcards" key={i}>
            {report.reports.map(r => <ReportCardView key={r.name} report={r} onSelect={onSelect} />)}
          </Grid>
          // </fieldset>
        ) : null)
      }
    </Fragment>
  )
}

export default CReporting;