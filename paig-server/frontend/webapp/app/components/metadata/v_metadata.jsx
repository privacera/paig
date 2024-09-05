import React, { Component } from "react";
import { observer } from "mobx-react";
import InfiniteScroll from 'react-infinite-scroll-component';

import { Grid, Typography, List, ListItem, ListItemText } from "@material-ui/core";
import AddIcon from '@material-ui/icons/Add';

import { SearchField } from 'common-ui/components/filters';
import {CustomAnchorBtn, CanUpdate} from 'common-ui/components/action_buttons';
import f from "common-ui/utils/f";
import { Loader, getSkeleton } from 'common-ui/components/generic_components';
import { FormGroupInput } from 'common-ui/components/form_fields';
import { ActionButtonsWithPermission } from 'common-ui/components/action_buttons';

const MetaDataHeader = observer(({data, permission, handleAdd}) => {
  let count = f.pageState(data).totalElements || 0;

  return (
    <Grid container className="p-l-15 p-r-15 p-t-10 p-b-10 align-items-center border-bottom">
      <Grid item xs={10}>
        <Typography variant="body1">Vector DB Metadata ({count})</Typography>
      </Grid>
      <Grid item xs={2}>
        <CanUpdate permission={permission}>
          <CustomAnchorBtn
            className="pull-right"
            onClick={handleAdd}
            icon={<AddIcon />}
            tooltipLabel="Add Vector DB Metadata"
            data-testid="add-metadata"
            data-track-id="add-metadata"
          />
        </CanUpdate>
      </Grid>
    </Grid>
  )
})

const MetadataSearch = observer(({_vState, handleSearch, handleOnChange}) => {
  return (
    <Grid container className="m-b-sm m-t-sm p-l-15 p-r-15">
      <SearchField
        value={_vState.searchValue}
        colAttr={{xs: 12, sm: 12, 'data-track-id': 'metadata-search'}}
        data-testid="metadata-search"
        placeholder="Search metadata"
        onChange={handleOnChange}
        onEnter={handleSearch}
      />
    </Grid>
  )
})

@observer
class VMetaDataList extends Component {
  fetchData = () => {
    const {data} = this.props;
    data.params.page = (data.params.page || 0) + 1;
    this.props.fetchData?.();
  }
  render() {
    const {data, _vState, handleMetaDataSelect} = this.props;

    let models = f.models(data);
    let pageState = f.pageState(data);

    return (
      <Grid container>
        <Grid item xs={12}>
          <Loader promiseData={data} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
            <List id="scrollableDiv" style={{height: 500, overflow: 'auto'}}>
              <InfiniteScroll
                dataLength={models.length}
                next={this.fetchData}
                hasMore={pageState.totalPages > (pageState.number + 1)}
                scrollableTarget="scrollableDiv"
                loader={
                  <Typography
                    variant="h6"
                    className="p-l-15 p-r-15"
                    color="textSecondary"
                  >
                    <Loader isLoading={true} loaderContent={getSkeleton('TWO_SLIM_LOADER')} />
                  </Typography>
                }
              >
                {
                  models.map(model => {
                    return (
                      <ListItem
                        data-testid="metadata-list-item"
                        button
                        key={model.id}
                        selected={_vState.metaData?.name === model.name}
                        onClick={() => {
                          handleMetaDataSelect(model);
                        }}
                      >
                        <ListItemText
                          className={_vState.metaData?.name === model.name ? 'list-item-text-selected' : ''}
                          primary={model.name}
                          primaryTypographyProps={{variant: 'body2'}}
                        />
                      </ListItem>
                    )
                  })
                }
              </InfiniteScroll>
            </List>
          </Loader>
        </Grid>
      </Grid>
    )
  }
}

const MetadataNameHeader = observer(({_vState, permission, handleEdit, handleDelete}) => {
  return (
    <Grid container className="p-l-15 p-r-15 border-bottom" style={{paddingTop: '13px', paddingBottom: '13px'}} >
      <Grid item xs={12} sm={10}>
        <Typography variant="body1" data-testid="name">
          {_vState.metaData?.name || ''}
        </Typography>
      </Grid>
      <Grid item xs={12} sm={2}>
        <div className="pull-right" data-testid='metadata-action'>
          <ActionButtonsWithPermission
            permission={permission}
            hideEdit={!_vState.metaData}
            hideDelete={!_vState.metaData}
            onEditClick={handleEdit}
            onDeleteClick={handleDelete}
          />
        </div>
      </Grid>
    </Grid>
  )
})

const MetadataDescription = observer(({_vState}) => {
  return (
    <Grid container className="m-t-sm p-l-15 p-r-15">
      <FormGroupInput
        inputProps={{'data-testid': 'description'}}
        value={_vState.metaData?.description || '--'}
        label="Description"
        colAttr={{xs: 12}}
        variant="standard"
        rows={1}
        rowsMax={6}
        multiline={true}
        disabled={true}
      />
    </Grid>
  )
});

export {
  MetaDataHeader,
  MetadataSearch,
  VMetaDataList,
  MetadataNameHeader,
  MetadataDescription
};