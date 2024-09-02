/* library imports */
import React, {Component, Fragment} from 'react';
import {observable} from 'mobx';
import {inject} from 'mobx-react';

/* other project imports */
import BaseContainer from 'containers/base_container';
import {REPORTS_TYPE, findReportTypeName} from 'containers/reports/c_reporting';
import {Search, VSavedReportTable} from 'components/reports/v_saved_reports_listing';
import {DEFAULTS} from 'common-ui/utils/globals';
import f from 'common-ui/utils/f';
import {Utils} from 'common-ui/utils/utils';

@inject('shieldAuditsReportsStore')
class CSavedReportsListing extends Component {

  @observable _vState = {
    searchValue: '',
    selectedReportType: ''
  };

  allowedExportReportsType=[
    //{label: REPORTS_TYPE[1].label, value: REPORTS_TYPE[1].name}
  ]

  constructor(props){
    super(props);
    this.cData.params = {
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
      sort: 'updateTime,DESC'
    };
  }
  cData = f.initCollection();

  componentDidMount() {
    this.fetchReportConfig();
  }
  fetchReportConfig = () => {
    f.beforeCollectionFetch(this.cData);
    this.props.shieldAuditsReportsStore.searchReports({
      params: this.cData.params
    })
    .then(this._postFetch, f.handleError(this.cData));
  }
  _postFetch = res => {
    // let models = res.models.slice();
    // const _models = models.filter(model => {
    //   if (!model.reportType) {
    //     model.reportType = this.getReportTypeName(model) || '';
    //   }
    //   return (this.allowedExportReportsType.includes(model.reportType));
    // });
    f.resetCollection(this.cData, res.models, res.pageState);
  }
  getReportTypeName(model) {
		let paramJson = Utils.parseJSON(model.paramJson);
		return findReportTypeName(paramJson.reportType);
	}

  handleSearch = (val) => {
    this.cData.params.name = val || undefined;
    this.cData.params.page = undefined;
    this.fetchReportConfig();
  }

  handleDelete = (model) => {
    f._confirm.show({
      title: `Delete Saved Report`,
      children: <Fragment>Are you sure you want to delete <b>{model.name}</b> report?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
    .then((confirm) => {
      this.props.shieldAuditsReportsStore.deleteReport(model.id, {models: this.cData})
      .then(() => {
          f.handlePagination(this.cData, this.cData.params);
          f.notifySuccess('Report deleted');
          confirm.hide();
          this.fetchReportConfig();
      }, f.handleError(null, null, {confirm}));
    }, () => {});
  }
  handlePageChange = () => {
    this.fetchReportConfig();
  }
  handleRefresh = () => {
    this.fetchReportConfig();
  }
  handleSorting = () => {
    this.fetchReportConfig();
  }

  render () {
    const {_vState, cData, handleSearch, handlePageChange, handleDelete, handleRefresh} = this;

    return (
      <BaseContainer
        handleRefresh={handleRefresh}
        headerChildren={(
          <Search
            _vState={_vState}
            handleSearch={handleSearch}
          />
        )}
        titleColAttr={{md: 8, sm: 8}}
      >
        <VSavedReportTable
          _vState={_vState}
          cData={cData}
          handlePageChange={handlePageChange}
          handleDelete={handleDelete}
        />
      </BaseContainer>
    );
  }
}

export default CSavedReportsListing;