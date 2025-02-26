import React, {Component} from 'react';
import {inject} from 'mobx-react';

import f from 'common-ui/utils/f';
import VEvaluationPurposeForm from "components/audits/evaluation/v_evalutaion_purpose_form";

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
class CEvaluationPurposeForm extends Component {
  constructor(props) {
    super(props);
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
      const apiTemplates = res.models.map(model => ({
        title: `Custom - Last Used ${this.formatCreateTime(model.create_time)}`,
        chip: "",
        description: model.purpose
      }));
      const combinedTemplates = [...hardcodedTemplates, ...apiTemplates];

      this.cEvalTemplateList.models = combinedTemplates;

      f.resetCollection(this.cEvalTemplateList, combinedTemplates, res.pageState);
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

  render() {
    const {cEvalTemplateList} = this;
    const {_vState, form} = this.props
    
    return (
      <>
        <VEvaluationPurposeForm _vState={_vState} data={cEvalTemplateList} form={form}/>
      </>
    );
  }
}

CEvaluationPurposeForm.defaultProps = {
  vName: 'evaluationPurposeForm'
}

export default CEvaluationPurposeForm;