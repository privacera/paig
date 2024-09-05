import React, {Component, Fragment} from "react";
import { inject, observer } from "mobx-react";
import { observable } from "mobx";

import { Grid, Box, Paper } from "@material-ui/core";

import f from "common-ui/utils/f";
import { DEFAULTS } from "common-ui/utils/globals";
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import FSModal from 'common-ui/lib/fs_modal';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import {MetaDataHeader, MetadataSearch, VMetaDataList, MetadataNameHeader, MetadataDescription} from "components/metadata/v_metadata";
import VMetaDataForm, {metadata_form_def} from "components/metadata/v_metadata_form";
import BaseContainer from 'containers/base_container';
import CMetaDataValues from 'containers/metadata/c_metadata_values'

@inject("metaDataStore")
@observer
class CMetaData extends Component {
  @observable _vState = {
    metaData: null,
    searchValue: ''
  }
  constructor(props) {
    super(props);

    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.ACCOUNT.META_DATA.PROPERTY);

    this.cMetaData = f.initCollection();
    this.cMetaData.params = {
      size: DEFAULTS.DEFAULT_PAGE_SIZE
    };

    this.form = createFSForm(metadata_form_def);
  }

  componentDidMount() {
    this.fetchMetaData();
  }

  fetchMetaData = () => {
    this.props.metaDataStore.fetchMetaData({
      params: this.cMetaData.params
    }).then(res => {
      const {models, pageState} = res;
      f.resetCollection(this.cMetaData, [...f.models(this.cMetaData), ...models], pageState);
      this.handleMetaDataSelect();
    }, f.handleError(this.cMetaData));
  }

  handleMetaDataSelect = (model) => {
    this._vState.metaData = model || this._vState.metaData || f.models(this.cMetaData)[0] || null;
    this.metaDataValuesRef?.showMetadataValues?.(this._vState.metaData?.id);
  }

  handleRefresh = () => {
    f.beforeCollectionFetch(this.cMetaData);
    delete this.cMetaData.params.page;
    this.fetchMetaData();
  };

  handlePageChange = () => {
    this.handleRefresh();
  };
  handleOnChange = (e, val) => {
    this._vState.searchValue = val;
    this.cMetaData.params.name = val || undefined;
  }
  handleSearch = () => {
    this._vState.metaData = null;
    delete this.cMetaData.params.page;
    f.beforeCollectionFetch(this.cMetaData);
    this.fetchMetaData();
  }
  handleAdd = () => {
    this.form.clearForm();
    this.Modal.show({
      title: "Add Vector DB Metadata"
    });
  }
  handleEdit = () => {
    this.form.clearForm();
    this.form.refresh(this._vState.metaData);
    this.form.model = this._vState.metaData;
    this.Modal.show({
      title: "Edit Vector DB Metadata"
    });
  }
  handleSave = async () => {
    await this.form.validate();
    if (!this.form.valid) {
      return;
    }
    let data = this.form.toJSON();
    data = Object.assign({}, this.form.model, data);

    this.Modal.okBtnDisabled(true);

    if (data.id) {
      try {
        data = await this.props.metaDataStore.updateMetaData(data);
        Object.assign(this._vState.metaData, data);
        this.Modal.hide();
        f.notifySuccess("Vector DB Metadata updated successfully");
        this.handleRefresh();
      } catch (e) {
        f.handleError(null, null, {modal: this.Modal})(e);
        console.error("Error updating metadata:", e);
      }
    } else {
      delete data.id;
      try {
        await this.props.metaDataStore.createMetaData(data);
        this.Modal.hide();
        f.notifySuccess("Vector DB Metadata added successfully");
        this.handleRefresh();
      } catch (e) {
        f.handleError(null, null, {modal: this.Modal})(e);
        console.error("Error creating metadata:", e);
      }
    }
  }
  handleDelete = () => {
    let {metaData} = this._vState;

    f._confirm.show({
      title: "Confirm Delete Vector DB Metadata",
      children: <Fragment>Are you sure you want to delete <b>{metaData.name}</b> metadata?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
     .then((confirm) => {
        this.props.metaDataStore.deleteMetaData(metaData.id, {
          models: this.cMetaData
        }).then(() => {
          f.notifySuccess("Vector DB Metadata deleted successfully");
          f.handlePagination(this.cMetaData, this.cMetaData.params);
          confirm.hide();
          this._vState.metaData = null;
          this.handleRefresh();
        }, f.handleError(null, null, {confirm}));
      }, () => {});
  }
    
  render() {

    return (
      <BaseContainer handleRefresh={this.handleRefresh}>
        <Box component={Paper}>
          <Grid container>
            <Grid item xs={12} md={4} lg={3} className="border-right">
              <MetaDataHeader
                data={this.cMetaData}
                permission={this.permission}
                handleAdd={this.handleAdd}
              />
              <MetadataSearch
                _vState={this._vState}
                handleOnChange={this.handleOnChange}
                handleSearch={this.handleSearch}
              />
              <VMetaDataList
                _vState={this._vState}
                data={this.cMetaData}
                fetchData={this.fetchMetaData}
                handleMetaDataSelect={this.handleMetaDataSelect}
                permission={this.permission}
              />
            </Grid>
            <Grid item xs={12} md={8} lg={9} data-testid="metadata-details">
              <MetadataNameHeader
                _vState={this._vState}
                permission={this.permission}
                handleEdit={this.handleEdit}
                handleDelete={this.handleDelete}
              />
              <MetadataDescription
                _vState={this._vState}
              />
              <CMetaDataValues
                ref={ref => this.metaDataValuesRef = ref}
              />
            </Grid>
          </Grid>
        </Box>
        <FSModal ref={ref => this.Modal = ref} dataResolve={this.handleSave}>
          <VMetaDataForm form={this.form} />
        </FSModal>
      </BaseContainer>
    );
  }
}

CMetaData.defaultProps = {
  vName: "metaData"
};

export default CMetaData;