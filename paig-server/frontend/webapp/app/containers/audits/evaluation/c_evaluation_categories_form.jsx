import React, { Component } from "react";

import VEvaluationCategoriesForm from "components/audits/evaluation/v_evaluation_categories_form";

class CEvaluationCategoriesForm extends Component {
  constructor(props) {
    super(props);
    this.state = {
      showSuggested: true,
      selectedCategories: []
    };
  }

  componentDidMount() {
    const { _vState } = this.props;
    const evalCategories = _vState.purposeResponse;
    const suggestedCategories = evalCategories.suggested_categories.map((category) => category.Name);
    this.props.form.refresh({ categories: suggestedCategories });
    if (suggestedCategories.length === 0) {
      this.setState({showSuggested: false})
    }
    this.setState({ selectedCategories: suggestedCategories });
  }

  handleToggle = () => {
    this.setState((prevState) => ({
      showSuggested: !prevState.showSuggested,
    }));
  };

  setSelectedCategories = (selectedCategories) => {
    this.setState({ selectedCategories });
  };

  render() {
    const { selectedCategories, showSuggested } = this.state;
    const { _vState } = this.props;
    const evalCategories = _vState.purposeResponse;
    const filteredCategories = showSuggested ? evalCategories.suggested_categories : evalCategories.all_categories;

    return (
      <VEvaluationCategoriesForm
        form={this.props.form}
        selectedCategories={selectedCategories}
        showSuggested={showSuggested}
        handleToggle={this.handleToggle}
        filteredCategories={filteredCategories}
        setSelectedCategories={this.setSelectedCategories}
        _vState={_vState}
      />
    );
  }
}

export default CEvaluationCategoriesForm;