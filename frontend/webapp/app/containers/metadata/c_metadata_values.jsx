import React, {Component, Fragment} from "react";
import { inject, observer } from "mobx-react";
import { observable } from "mobx";

import { Grid } from "@material-ui/core";

import { SearchField } from 'common-ui/components/filters';
import f from "common-ui/utils/f";
import { DEFAULTS } from "common-ui/utils/globals";
import {AddButtonWithPermission} from 'common-ui/components/action_buttons';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import {createFSForm} from 'common-ui/lib/form/fs_form';
import FSModal from 'common-ui/lib/fs_modal';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import VMetaDataValues from "components/metadata/v_metadata_values";
import VMetaDataValueForm, {metadata_value_form_def} from "components/metadata/v_metadata_values_form";

@inject('metaDataStore', 'metaDataValuesStore')
@observer
class CMetaDataValues extends Component {
  @observable _vState = {
    metadataId: null,
    searchValue: ''
  }
  constructor(props) {
    super(props);

    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.ACCOUNT.META_DATA_VALUES.PROPERTY);

    this.cMetaDataValues = f.initCollection({ loading: false });
    this.cMetaDataValues.params = {
      size: DEFAULTS.DEFAULT_PAGE_SIZE
    };

    this.form = createFSForm(metadata_value_form_def);
  }

  showMetadataValues = (metadataId) => {
    if (metadataId && metadataId === this._vState.metadataId) {
      return;
    }
    this.setMetadataId(metadataId);
    this.handleRefresh();
  }

  setMetadataId = (metadataId) => {
    this._vState.metadataId = metadataId || null;
    this._vState.searchValue = '';
    this.cMetaDataValues.params.metadataId = metadataId;
    delete this.cMetaDataValues.params.page;
    delete this.cMetaDataValues.params.metadataValue;
  }

  fetchMetaDataValues = () => {
    f.beforeCollectionFetch(this.cMetaDataValues);
    this.props.metaDataValuesStore.fetchMetaDataValues({
      params: this.cMetaDataValues.params
    }).then(f.handleSuccess(this.cMetaDataValues), f.handleError(this.cMetaDataValues));
  };

  handleRefresh = () => {
    if (this._vState.metadataId) {
      this.fetchMetaDataValues();
    } else {
      f.resetCollection(this.cMetaDataValues);
    }
  };

  handlePageChange = () => {
    this.handleRefresh();
  };

  handleOnChange = (e, val) => {
    this._vState.searchValue = val;
    this.cMetaDataValues.params.metadataValue = val || undefined;
  }

  handleSearch = (value) => {
    delete this.cMetaDataValues.params.page;
    this.fetchMetaDataValues();
  }
  handleAdd = () => {
    this.form.clearForm();
    this.form.refresh({
      metadataId: this._vState.metadataId
    });
    this.Modal.show({
      title: "Add Value"
    });
  }
  handleEdit = (model) => {
    this.form.clearForm();
    this.form.refresh(model);
    this.form.model = model;
    this.Modal.show({
      title: "Edit Value"
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
        await this.props.metaDataValuesStore.updateMetaDataValue(data);
        this.Modal.hide();
        f.notifySuccess("Value updated successfully");
        this.fetchMetaDataValues();
      } catch (e) {
        f.handleError(null, null, {modal: this.Modal})(e);
        console.error("Error updating metadata value:", e);
      }
    } else {
      delete data.id;
      try {
        await this.props.metaDataValuesStore.createMetaDataValue(data);
        this.Modal.hide();
        f.notifySuccess("Value added successfully");
        this.fetchMetaDataValues();
      } catch (e) {
        f.handleError(null, null, {modal: this.Modal})(e);
        console.error("Error creating metadata value:", e);
      }
    }
  }
  handleDelete = (model) => {
    f._confirm.show({
      title: "Confirm Delete Value",
      children: <Fragment>Are you sure you want to delete <b>{model.metadataValue}</b> value?</Fragment>,
      btnCancelText: 'Cancel',
      btnOkText: 'Delete',
      btnOkColor: 'secondary',
      btnOkVariant: 'text'
    })
     .then((confirm) => {
        this.props.metaDataValuesStore.deleteMetaDataValue(model.id, {
          models: this.cMetaDataValues,
        }).then(() => {
          f.notifySuccess("Value deleted successfully");
          f.handlePagination(this.cMetaDataValues, this.cMetaDataValues.params);
          confirm.hide();
          this.fetchMetaDataValues();
        }, f.handleError(null, null, {confirm}));
      }, () => {});
  }
  handleMetaDataChange = (value) => {
    this._vState.metadataId = value;
    this.cMetaDataValues.params.metadataId = this._vState.metadataId;
    delete this.cMetaDataValues.params.metadataValue;
    delete this.cMetaDataValues.params.page;
    if (value) {
      this.fetchMetaDataValues();
    }
  }
    
  render() {
    return (
      <Fragment>
        <Grid container className="m-t-md p-l-15 p-r-15 align-items-center">
          <SearchField
            colAttr={{
              xs: 12,
              sm: 9,
              md: 8,
              lg: 6,
              'data-track-id': 'metadata-value-search'
            }}
            value={this._vState.searchValue}
            placeholder="Search value"
            onChange={this.handleOnChange}
            onEnter={this.handleSearch}
          />
          <AddButtonWithPermission
            permission={this.permission}
            label="Add Value"
            colAttr={{xs: 12, sm: 3, md: 4, lg: 6, 'data-track-id': 'metadata-value-add'}}
            disabled={!this._vState.metadataId}
            data-testid="add-metadata-value"
            onClick={this.handleAdd}
          />
        </Grid>
        <VMetaDataValues
          data={this.cMetaDataValues}
          permission={this.permission}
          pageChange={this.handlePageChange}
          handleEdit={this.handleEdit}
          handleDelete={this.handleDelete}
        />
        <FSModal ref={ref => this.Modal = ref} dataResolve={this.handleSave}>
          <VMetaDataValueForm form={this.form} />
        </FSModal>
      </Fragment>
    );
  }
}

CMetaDataValues.defaultProps = {
  vName: "metaDataValues"
};

export default CMetaDataValues;