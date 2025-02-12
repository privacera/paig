import React, {Component} from 'react';
import {inject, observer} from 'mobx-react';

import {Grid} from '@material-ui/core';
import f from 'common-ui/utils/f';
import VEvaluationPurposeForm, {evaluation_purpose_form_def} from "components/audits/evaluation/v_evalutaion_purpose_form";
import { createFSForm } from 'common-ui/lib/form/fs_form';

const hardcodedTemplates = [
  {
    title: "Finance",
    chip: "Auditor",
    description:
      "As a finance auditor member consider a comprehensive evaluation of the financial model to assess its accuracy, identify potential biases, and ensure compliance with relevant regulations.",
  },
  {
    title: "Risk Management",
    chip: "Risk Analyst",
    description:
      "As a risk analyst, evaluate the financial model to identify potential risks, assess their impact, and recommend mitigation strategies to safeguard financial stability.",
  },
  {
    title: "Investment Strategy",
    chip: "Investment Analyst",
    description:
      "As an investment strategist, assess the financial model’s projections, identify key growth opportunities, and validate assumptions to support data-driven investment decisions.",
  },
];

@inject('evaluationStore')
@observer
class CEvaluationPurposeForm extends Component {
  _vState = {}
  constructor(props) {
    super(props);
    this.form = createFSForm(evaluation_purpose_form_def);
    this.cEvalTemplateList = f.initCollection();
    this.cEvalTemplateList.params = {
      size: 3,
      sort: 'create_time,desc'
    }
    this.cEvalTemplateList.models = [...hardcodedTemplates];
    this.fetchEvaluationAppsList();
  }
  fetchEvaluationAppsList = () => {
    f.beforeCollectionFetch(this.cEvalTemplateList);
    this.props.evaluationStore.fetchEvaluationReports({
      params: this.cEvalTemplateList.params
    }).then(res => {
      const mockRes = {
        models: [
          {
            application_names: "Finance App",
            config_name: "Finance Config",
            purpose: "Evaluate the financial model for accuracy and compliance.",
            eval_id: "eval_001",
            config_id: 101,
            status: "Completed",
            owner: "user_123",
            passed: "10",
            failed: "2",
            id: 1,
            report_id: "report_001",
            create_time: "2023-10-01T10:00:00Z"
          },
          {
            application_names: "Risk Management App",
            config_name: "Risk Config",
            purpose: "Assess the risk management model for potential risks and mitigation strategies.",
            eval_id: "eval_002",
            config_id: 102,
            status: "In Progress",
            owner: "user_456",
            passed: "5",
            failed: "1",
            id: 2,
            report_id: "report_002",
            create_time: "2023-10-02T11:00:00Z"
          },
          {
            application_names: "Compliance App",
            config_name: "Compliance Config",
            purpose: "Ensure the financial model adheres to all relevant regulations and standards.",
            eval_id: "eval_003",
            config_id: 103,
            status: "Pending",
            owner: "user_789",
            passed: "8",
            failed: "3",
            id: 3,
            report_id: "report_003",
            create_time: "2025-02-10T12:00:00Z"
          },
          {
            application_names: "Performance Analysis App",
            config_name: "Performance Config",
            purpose: "Evaluate the financial model performance metrics and identify trends.",
            eval_id: "eval_004",
            config_id: 104,
            status: "Completed",
            owner: "user_101",
            passed: "12",
            failed: "4",
            id: 4,
            report_id: "report_004",
            create_time: "2025-02-01T13:00:00Z"
          }
        ]
      };
      const apiTemplates = mockRes.models.map(model => ({
        title: `Custom - Last Used ${this.formatCreateTime(model.create_time)}`,
        chip: "",
        description: model.purpose
      }));
      const combinedTemplates = [...hardcodedTemplates, ...apiTemplates];

      this.cEvalTemplateList.models = combinedTemplates;

      f.resetCollection(this.cEvalTemplateList, combinedTemplates, mockRes.pageState);
      console.log(this.cEvalTemplateList.models, 'this.cEvalTemplateList.models');
    }, f.handleError(this.cEvalTemplateList));
  }

  // Function to format create_time
  formatCreateTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    
    const diffTime = now - date;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const diffMonths = Math.floor(diffDays / 30);
    const diffYears = Math.floor(diffDays / 365);
  
    if (diffDays === 0) {
      return "Today";
    } else if (diffDays === 1) {
      return "Yesterday";
    } else if (diffDays === 2) {
      return "Day before yesterday";
    } else if (diffDays <= 6) {
      return "Earlier this week";
    } else if (diffDays <= 13) {
      return "Last week";
    } else if (diffDays <= 20) {
      return "Two weeks ago";
    } else if (diffDays <= 27) {
      return "Three weeks ago";
    } else if (diffMonths === 1) {
      return "A month ago";
    } else if (diffMonths === 2) {
      return "Two months ago";
    } else if (diffMonths <= 5) {
      return "A few months ago";
    } else if (diffMonths <= 11) {
      return "Several months ago";
    } else if (diffYears === 1) {
      return "A year ago";
    } else if (diffYears <= 2) {
      return "Two years ago";
    } else if (diffYears <= 5) {
      return "A few years ago";
    } else {
      return date.toISOString().split("T")[0];
    }
  };

  resolveForm = async () => {
      await this.form.validate();
      if (!this.form.valid) {
        return;
      }
      let data = this.form.toJSON();
      data = Object.assign({}, this.form.model, data);

      this.modalRef.current.okBtnDisabled(true);
  
      if (data.id) {
        try {
          await this.props.evaluationStore.updateConfig(data);
          this.modalRef.current.hide();
          f.notifySuccess("Configuration updated successfully");
          this.fetchEvaluationAppsList();
        } catch (e) {
          f.handleError(null, null, {modal: this.modalRef.current})(e);
          console.error("Error updating configuration:", e);
        }
      } else {
        delete data.id;
        try {
          await this.props.evaluationStore.addConfig(data);
          this.modalRef.current.hide();
          f.notifySuccess("Configuration added successfully");
          this.fetchEvaluationAppsList();
        } catch (e) {
          f.handleError(null, null, {modal: this.modalRef.current})(e);
          console.error("Error creating configuration:", e);
        }
      }
  }
  render() {
    const {_vState, cEvalTemplateList} = this;
    
    return (
      <>
        <VEvaluationPurposeForm _vState={this._vState} data={cEvalTemplateList} form={this.form}/>
      </>
    );
  }
}

CEvaluationPurposeForm.defaultProps = {
  vName: 'evaluationPurposeForm'
}

export default CEvaluationPurposeForm;