import React, { Component } from "react";
import { inject } from "mobx-react";
import { observable } from "mobx";

import f from "common-ui/utils/f";
import { DEFAULTS } from "common-ui/utils/globals";
import BaseContainer from "containers/base_container";
import VSensitiveData from "components/account/sensitive_data/v_sensitive_data";
import { SearchField } from 'common-ui/components/filters';

@inject("sensitiveDataStore")
class CSensitiveData extends Component {
  @observable _vState = {
    searchValue: ''
  }
  constructor(props) {
    super(props);

    this.cSensitiveData = f.initCollection();
    this.cSensitiveData.params = {
      size: DEFAULTS.DEFAULT_PAGE_SIZE
    };
  }

  componentDidMount() {
    this.fetchSensitiveData();
  }

  fetchSensitiveData = () => {
    f.beforeCollectionFetch(this.cSensitiveData);
    this.props.sensitiveDataStore.fetchSensitiveData({
        params: this.cSensitiveData.params
    }).then(f.handleSuccess(this.cSensitiveData), f.handleError(this.cSensitiveData));
  };

  handleRefresh = () => {
    this.fetchSensitiveData();
  };

  handlePageChange = () => {
    this.handleRefresh();
  };

  handleSearch = (value) => {
    this._vState.searchValue = value;
    this.cSensitiveData.params.name = value || undefined;
    this.cSensitiveData.params.page = undefined;
    this.fetchSensitiveData();
  }

  render() {
    return (
      <BaseContainer
        handleRefresh={this.handleRefresh}
        titleColAttr={{ lg: 8, md: 7 }}
        headerChildren={(
          <SearchField
            initialValue={this._vState.searchValue}
            colAttr={{xs: 12, sm: 4, md: 4}}
            placeholder="Search Tags"
            onEnter={this.handleSearch}
            data-track-id="search-sensitive-data"
          />
        )}
      >
        <VSensitiveData
          data={this.cSensitiveData}
          pageChange={this.handlePageChange}
        />
      </BaseContainer>
    );
  }
}

CSensitiveData.defaultProps = {
  vName: "sensitiveData"
};

export default CSensitiveData;
