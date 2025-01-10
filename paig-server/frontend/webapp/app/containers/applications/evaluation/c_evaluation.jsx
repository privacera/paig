import React, { Component, Fragment } from "react";
import { inject } from "mobx-react";
import { Box, Button, Typography, Card, CardContent } from "@material-ui/core";

import BaseContainer from "containers/base_container";
import f from "common-ui/utils/f";
import { AddButtonWithPermission } from "common-ui/components/action_buttons";
import { PaginationComponent } from "common-ui/components/generic_components";
import gdprLogo from "common-ui/images/gdpr.png";
import {createFSForm} from 'common-ui/lib/form/fs_form';
import {evaluation_details_form_def} from 'components/applications/evaluation/v_evaluation_details_form';



@inject("evaluationStore")
class CEvaluation extends Component {
  constructor(props) {
    super(props);

    this.permission = true; // Replace with actual permission logic if required.
    this.form = createFSForm(evaluation_details_form_def);

    this.evaluationReports = f.initCollection();
    this.evaluationReports.params = {
      size: 10, // Default page size
      sort: "createTime,desc",
    };
  }

  componentDidMount() {
    // this.getEvaluationReports();
  }

  getEvaluationReports = () => {
    f.beforeCollectionFetch(this.evaluationReports);
    this.props.evaluationStore
      .getReports({ params: this.evaluationReports.params })
      .then(
        f.handleSuccess(this.evaluationReports),
        f.handleError(this.evaluationReports)
      );
  };

  handleRefresh = () => {
    // this.getEvaluationReports();
  };

  handleReportCreate = () => {
    this.props.history.push("/evaluation/create");
  };

  handleReportEdit = (id) => {
    this.props.history.push(`/evaluation/${id}`);
  };

  handleDeleteReport = (report) => {
    f._confirm
      .show({
        title: "Confirm Delete",
        children: (
          <Fragment>
            Are you sure you want to delete <b>{report.name}</b> report?
          </Fragment>
        ),
        btnCancelText: "Cancel",
        btnOkText: "Delete",
        btnOkColor: "secondary",
        btnOkVariant: "text",
      })
      .then(
        (confirm) => {
          this.props.evaluationStore
            .deleteReport(report.id, { models: this.evaluationReports })
            .then(() => {
              f.notifySuccess(
                `The Evaluation Report ${report.name} was deleted successfully`
              );
              confirm.hide();
              this.handleRefresh();
            }, f.handleError());
        },
        () => {}
      );
  };

  handlePageChange = (page) => {
    this.evaluationReports.params.page = page - 1;
    this.handleRefresh();
  };

  render() {
    const {
      evaluationReports,
      handleReportCreate,
      handleReportEdit,
      handleDeleteReport,
    } = this;

    return (
      <BaseContainer
        handleRefresh={this.handleRefresh}
        titleColAttr={{
          sm: 8,
          md: 8,
        }}
      >
        <Card style={{ display: "flex", padding: 16 }}>
          <Box
            style={{
              flex: 1,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <img
              src={gdprLogo}
              alt="GDPR Illustration"
              style={{ width: "100%", maxWidth: 300 }}
            />
          </Box>

          <CardContent style={{ flex: 2, paddingLeft: 24 }}>
            <Typography variant="h5" gutterBottom>
              How does Evaluation work?
            </Typography>
            <Typography variant="body1" paragraph>
              <ol style={{ paddingLeft: 20 }}>
                <li>
                  Click configure button to begin the process
                  <ol type="a" style={{ paddingLeft: 20, marginTop: 8 }}>
                    <li>Select AI application</li>
                    <li>State purpose of application to generate categories</li>
                  </ol>
                </li>
                <li>Select categories to tune evaluation</li>
                <li>Customize test suite generated based on above points</li>
                <li>Start Vulnerability scan</li>
                <li>View and review summary of scan</li>
              </ol>
            </Typography>
            <Button 
              variant="contained" 
              color="primary"
              onClick={handleReportCreate}
            >
              Configure
            </Button>
          </CardContent>
        </Card>

        <PaginationComponent
          promiseData={evaluationReports}
          callback={this.handlePageChange}
        />
      </BaseContainer>
    );
  }
}

export default CEvaluation;
