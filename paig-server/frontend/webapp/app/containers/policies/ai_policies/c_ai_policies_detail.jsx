import React, {Component, Fragment} from 'react';
import { observer, inject } from 'mobx-react';
import {observable} from 'mobx';
import { withRouter } from 'react-router';
import { cloneDeep } from 'lodash';

import {Grid, Typography, Card, Badge, Tooltip, CardContent} from '@material-ui/core';
import GroupIcon from '@material-ui/icons/Group';
import PersonIcon from '@material-ui/icons/Person';
import ContactsIcon from '@material-ui/icons/Contacts';
import BlockOutlinedIcon from '@material-ui/icons/BlockOutlined';
import CheckCircleOutlineIcon from '@material-ui/icons/CheckCircleOutline';
import RemoveCircleOutlineOutlinedIcon from '@material-ui/icons/RemoveCircleOutlineOutlined';
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';

import f from 'common-ui/utils/f';
import {FEATURE_PERMISSIONS} from 'utils/globals';
import { permissionCheckerUtil } from 'common-ui/utils/permission_checker_util';
import { AddButtonWithPermission } from 'common-ui/components/action_buttons';
import AIPolicyFormUtil from 'containers/policies/ai_policies/ai_policy_form_util';
import { TagChip } from 'common-ui/lib/fs_select/fs_select';
import { Loader, getSkeleton } from 'common-ui/components/generic_components'
import {DEFAULTS, STATUS} from 'common-ui/utils/globals';
import {configProperties} from 'utils/config_properties';

@inject('aiPoliciesStore', 'dashboardStore', 'vectorDBStore', 'vectorDBPolicyStore')
@observer
class CAIPolicies extends Component {
  cSensitiveDataInApplication = f.initCollection();
  cContentRestrictionData = f.initCollection();
  cVectorDBs = f.initCollection();
  cVectorDBsContentRestrictionData = f.initCollection();
  @observable _vState = {
    application: {},
    accessPolicy: {},
    vectorDBModel: {}
  }
  constructor(props) {
    super(props);
    this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.GOVERNANCE.AI_POLICIES.PROPERTY);
    this.aiPolicyFormUtil = new AIPolicyFormUtil();

    this._vState.application = props.application;

    this.cVectorDBs.params = {
      size: DEFAULTS.DEFAULT_PAGE_SIZE,
      sort: 'createTime,desc'
    }

    this.cContentRestrictionData.params = {
      size: 1,
      status: 1
    }
  }

  componentDidMount() {
    // this.fetchApplication();
    this.fetchAccessPolicy();
    this.fetchContentRestrictionData();
    if(configProperties.isVectorDBEnable()){
      this.getVectorDBs();
    }
    this.fetchSensitiveDataInApplications();
  }

  /*fetchApplication = async () => {
    const { match, application, aiApplicationStore } = this.props;
    const {id, applicationId } = match?.params ?? {};
    const appId = id || applicationId;
    if (!application) {
      const response = await aiApplicationStore.getAIApplicationById(appId, UiState.getHeaderWithTenantId());
      this._vState.application = response;
    } else {
      this._vState.application = application;
    }
    this.fetchAccessPolicy();
    this.fetchContentRestrictionData();
    this.fetchSensitiveDataInApplications();
  }*/

  fetchAccessPolicy = async() => {
    const {application} = this._vState;
    try {
      let response = await this.props.aiPoliciesStore.getGlobalPermissionPolicy(application.id);
      this._vState.accessPolicy = response;
    } catch(e) {
      console.error('Failed to get policy count', e)
    }
  }

  getVectorDBs = () => {
    f.beforeCollectionFetch(this.cVectorDBs)
    this.props.vectorDBStore.getVectorDBs({
      params: this.cVectorDBs.params
    }).then(f.handleSuccess(this.cVectorDBs, this.fetchContentRestrictionDataVD), f.handleError(this.cVectorDBs));
  }

  fetchContentRestrictionData = () => {
    const { id, applicationId } = this.props?.match?.params ?? {};
    const appId = id || applicationId;

    f.beforeCollectionFetch(this.cContentRestrictionData);
    this.props.aiPoliciesStore.getAllPolicies(appId, {
      params: this.cContentRestrictionData.params
    })
    .then(
      f.handleSuccess(this.cContentRestrictionData),
      f.handleError(this.cContentRestrictionData)
    );
  };
  
  fetchContentRestrictionDataVD = () => {
    const { vectorDBs } = this._vState.application;
    const associatedVectorDBName = vectorDBs[0];
    if (vectorDBs && vectorDBs.length > 0) {
    const associatedVectorDBObject = f.models(this.cVectorDBs).find(db => db.name === associatedVectorDBName);  
      if(associatedVectorDBObject) {
        this._vState.vectorDBModel = associatedVectorDBObject
        f.beforeCollectionFetch(this.cVectorDBsContentRestrictionData);
        this.props.vectorDBPolicyStore.getAllPolicies(associatedVectorDBObject.id, {
          params: this.cContentRestrictionData.params
        })
        .then(
          f.handleSuccess(this.cVectorDBsContentRestrictionData),
          f.handleError(this.cVectorDBsContentRestrictionData)
        );
      }
    }  
  };

  fetchSensitiveDataInApplications = async () => {
    const { applicationKey } = this._vState.application ?? {};
    if (!applicationKey) {
      console.error('Application key not found');
      return;
    }
    const updatedParams = {
      ...this.cSensitiveDataInApplication.params,
      "includeQuery.applicationKey": applicationKey,
      groupBy: 'traits'
    };
    f.beforeCollectionFetch(this.cSensitiveDataInApplication);
    try {
      let result = await this.props.dashboardStore.fetchCounts({
        params: updatedParams
      });
      let formattedData = this.formatSensitiveDataInApplications(result);
      f.resetCollection(this.cSensitiveDataInApplication, formattedData);
    } catch(e) {
      console.error("Failed to get tags in application", e);
      f.resetCollection(this.cSensitiveDataInApplication, []);
    }
  }

  formatSensitiveDataInApplications = (data = {}) => {
    const transformedData = [];
    if (!data.traits) {
      return transformedData;
    }
    for (const key in data.traits) {
      transformedData.push(key);
    }
    return transformedData;
  }

  handleRedirect = () => {
    const { application } = this._vState;
    this.props.history.push(`/ai_application/${application.id}/ai_policies`);
  }

  handleVectorDBRedirect = () => {
    const { vectorDBModel } = this._vState;
    this.props.history.push(`/vector_db/${vectorDBModel.id}`);
  }

  reAssignOthersOptionToGroups = () => {
    const data = cloneDeep(this.aiPolicyFormUtil.getFormData());
    
    if (data.others?.length) {
      data.groups = ["public"];
    }
    delete data.others;

    return data;
  }

  render () {
    const {handleTabSelect} = this.props
    const {cSensitiveDataInApplication,
      cContentRestrictionData, cVectorDBsContentRestrictionData, handleVectorDBRedirect
    } = this;
    return (
      <Fragment>
        <Grid container spacing={1} className="m-b-sm">
          <Grid item xs={12} md={12} data-track-id="tracked-sensitive-data">
            <div className='full-card-height'> 
              <Card className='full-width'> 
                <SensitiveDataAccessed 
                  sensitiveData={cSensitiveDataInApplication}
                />
              </Card>
            </div>
          </Grid>
        </Grid>
        <Grid container spacing={1} className="m-b-sm">
          <Grid item xs={12} md={6} data-track-id="app-access-control">
            <div className='full-card-height'> 
              <Card className='full-width'>
                <Permissions 
                  accessPolicy={this._vState.accessPolicy}
                  contentRestrictionData={cContentRestrictionData} 
                  permission={this.permission}
                  handleTabSelect={handleTabSelect}
                />
              </Card>
            </div>
          </Grid>
          {
            configProperties.isVectorDBEnable() && this._vState.application.vectorDBs.length > 0 &&
            <Grid item xs={12} md={6} data-track-id="vector-db-permissions">
              <div className='full-card-height'> 
                <Card className='full-width'>
                  <VectoDbPermissions 
                    vectorDBModel={this._vState.vectorDBModel}
                    contentRestrictionData={cVectorDBsContentRestrictionData} 
                    permission={this.permission}
                    handleVectorDBRedirect={handleVectorDBRedirect}
                  />
                </Card>
              </div>
            </Grid>
          }
        </Grid>
      </Fragment>
    )
  }
}

const SensitiveDataAccessed = observer(({ sensitiveData }) => {
  let models = f.models(sensitiveData)
  return (
    <CardContent data-testid="sensitive-data-card" style={{ height: '100%' }}>
      <Tooltip arrow placement="top" title={"This section displays a list of tags identified in the interactions with the GenAI application. Each tag icon represents a category of tags that has been either submitted to or received from the application, ensuring transparency in data privacy monitoring."}>
        <Typography variant="h6" component="h2" className="m-b-sm inline-block" gutterBottom>
          Tracked Tags in GenAI Application Interactions
        </Typography>
      </Tooltip>
      <Loader promiseData={sensitiveData} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
        {
          (models.length > 0) ?
            <div data-testid="chip-wrapper" style={{ display: 'flex', flexWrap: 'wrap' }}>
              {
                models.map((dataObject, index) => (
                  <div key={`data_${index}`}>
                    <TagChip
                      data-testid="tagchip"
                      icon={<SimCardAlertIcon className="icon-styles" />}
                      label={String(dataObject)}
                      style={{ margin: '5px' }}
                      size="small"
                    />
                  </div>
                ))
              }
            </div>
          :
            <div data-testid="no-sensitive-data"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: "70%"
              }}
            >
              No tags available
            </div>
        }
      </Loader>
    </CardContent>
  )
})

const updatePublicGroupToEveryone = (groups=[]) => {
  return groups.map(group => {
    if (group == 'public') {
      return 'Everyone';
    }
    return group;
  });
}

const calculateTotalCount = (sensitiveData, contentRestrictionData) => {
  const contentRestrictionCount = f.pageState(contentRestrictionData).totalElements;
  const sensitiveDataCount = f.pageState(sensitiveData).numberOfElements;
  return contentRestrictionCount - sensitiveDataCount;
};

const Permissions = observer(({ accessPolicy, contentRestrictionData, permission, handleTabSelect}) => {
  let totalCount = f.pageState(contentRestrictionData).totalElements;
  const handleClick = () => {
    handleTabSelect(1, "permission");
  };
  return (
    <div>
      <CardContent  data-testid="permission-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }} className="m-b-md">
          <Tooltip arrow placement="top" title={"This section provides a summary of the current permission settings for the AI Application"}>
            <Typography variant="h6" component="h2" style={{ marginBottom: '10px'}}>
              Application Access Control Summary
            </Typography>
          </Tooltip>
          <AddButtonWithPermission
            className="pull-right"
            colAttr={{sm: 3}}
            permission={permission}
            label="manage"
            variant="outlined"
            onClick={handleClick}
            data-testid="manage-permission-btn"
            data-track-id="manage-permission-btn"
          />
        </div>
        <div data-testid="allow-access-row" style={{ display: 'flex', alignItems: 'center' }} className="m-b-md">
          <CheckCircleOutlineIcon className="m-r-sm text-success" />
          <Typography variant="subtitle1" component="div">
            Granted Access Count
          </Typography>
          <div style={{ marginLeft: 'auto' }}>
            <CustomTooltip
              dataTestId="allow-access-users"
              titleText="Users"
              badgeContent={accessPolicy.allowedUsers?.length || 0}
              badgeIcon={<PersonIcon color="action" />}
              uniqueData={accessPolicy.allowedUsers}
            />
            <CustomTooltip
              dataTestId="allow-access-groups"
              titleText="Groups"
              badgeContent={accessPolicy.allowedGroups?.length || 0}
              badgeIcon={<GroupIcon color="action" />}
              uniqueData={updatePublicGroupToEveryone(accessPolicy.allowedGroups)}
            />
            <CustomTooltip
              dataTestId="allow-access-roles"
              titleText="Roles"
              badgeContent={accessPolicy.allowedRoles?.length || 0}
              badgeIcon={<ContactsIcon color="action" />}
              uniqueData={accessPolicy.allowedRoles}
            />
          </div>
        </div>
        
        <div data-testid="deny-access-row" style={{ display: 'flex', alignItems: 'center' }} className="m-b-md">
          <BlockOutlinedIcon className="m-r-sm" color="secondary"/>
          <Typography data-testid="deny-access-title" variant="subtitle1" component="div">
            Access Denials Enforced
          </Typography>
          <div style={{ marginLeft: 'auto' }}>
            <CustomTooltip
              dataTestId="deny-access-users"
              titleText="Users"
              badgeContent={accessPolicy.deniedUsers?.length || 0}
              badgeIcon={<PersonIcon color="action" />}
              uniqueData={accessPolicy.deniedUsers}
            />
            <CustomTooltip
              dataTestId="deny-access-groups"
              titleText="Groups"
              badgeContent={accessPolicy.deniedGroups?.length || 0}
              badgeIcon={<GroupIcon color="action" />}
              uniqueData={updatePublicGroupToEveryone(accessPolicy.deniedGroups)}
            />
            <CustomTooltip
              dataTestId="deny-access-roles"
              titleText="Roles"
              badgeContent={accessPolicy.deniedRoles?.length || 0}
              badgeIcon={<ContactsIcon color="action" />}
              uniqueData={accessPolicy.deniedRoles}
            />
          </div>
        </div>

        <div data-testid="cont-rest-row" style={{ display: 'flex', alignItems: 'center' }}>
          <RemoveCircleOutlineOutlinedIcon className="m-r-sm" />
          <Typography data-testid="cont-rest-title" variant="subtitle1" component="div">
            Active Content Restrictions
          </Typography>
          <div style={{ marginLeft: 'auto' }}>
            <Badge data-testid="sim-icon"
              badgeContent={totalCount}
              color="primary"
              className="m-r-md"
            >
              <SimCardAlertIcon className="MuiSvgIcon-colorAction" />
            </Badge>
          </div>
        </div>

      </CardContent>
    </div>
  );
});

const VectoDbPermissions = observer(({ vectorDBModel, contentRestrictionData, permission, handleVectorDBRedirect}) => {
  let totalCount = f.pageState(contentRestrictionData).totalElements;
  return (
    <Fragment>
      <CardContent data-testid="vector-db-permission-card" data-track-id="vector-db-permission-card">
        <Grid item xs={12}>
          <Loader promiseData={contentRestrictionData} loaderContent={getSkeleton('TWO_SLIM_LOADER')}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }} className="m-b-md">
              <Typography variant="h6" component="h2" color="primary" onClick={handleVectorDBRedirect}  style={{ cursor: 'pointer' }}>
                VectorDB - {vectorDBModel && vectorDBModel.name ? vectorDBModel.name : ''}
              </Typography>
            </div>
          </Loader>
        </Grid>   
        <Grid item xs={12}>
          <div data-testid="cont-rest-row" style={{ display: 'flex', alignItems: 'center' }} className="m-b-md">
            <RemoveCircleOutlineOutlinedIcon className="m-r-sm" />
            <Typography data-testid="cont-rest-title" variant="subtitle1" component="div">
              RAG Filtering Permissions
            </Typography>
            <div style={{ marginLeft: 'auto' }}>
              <Badge data-testid="sim-icon"
                badgeContent={totalCount}
                color="primary"
                className="m-r-md"
              >
                <SimCardAlertIcon color="action" />
              </Badge>
            </div>
          </div>
          <div data-testid="cont-rest-row" style={{ display: 'flex', alignItems: 'center' }} className="m-b-md">
            <GroupIcon className="m-r-sm" />
            <Tooltip arrow placement="top" title={"When enabled, this feature restricts the retrieval of data chunks and contextual information from RAG to only those elements the user or group has explicit permission to access. It ensures that each user's data interactions align with their designated access rights, enhancing data security and compliance"}>
              <Typography data-testid="cont-rest-title" variant="subtitle1" component="div">
                User/Group Access-Limited Retrieval
              </Typography>
            </Tooltip>
            <div style={{ marginLeft: 'auto' }}>
              <Badge data-testid="sim-icon"
                color="primary"
                className="m-r-md"
              >
                {
                  vectorDBModel.userEnforcement === STATUS.enabled.value
                  ? <CheckCircleIcon className="text-success" />
                  : <CancelIcon color="action" />
                }
              </Badge>
            </div>
          </div>
        </Grid>
      </CardContent>
    </Fragment>
  );
});

const SimCardAlertIcon = ({ className='MuiSvgIcon-colorAction' }) => {
  return (
    <svg
      className={`MuiSvgIcon-root MuiSvgIcon-fontSizeMedium ${className}`}
      focusable="false"
      aria-hidden="true"
      viewBox="0 0 24 24"
      data-testid="sim-card-alert-icon"
    >
      <path d="M18 2h-8L4.02 8 4 20c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-5 15h-2v-2h2v2zm0-4h-2V8h2v5z"></path>
    </svg>
  );
};

const CustomTooltip = ({
  titleText,
  badgeContent,
  badgeIcon,
  uniqueData,
  dataTestId
}) => {
  return (
    <Tooltip
      title={
        <div data-testid="tooltip-comp" style={{ display: 'flex', flexDirection: 'column' }}>
          <Typography data-testid="tooltip-title" variant="subtitle2" gutterBottom>
            {titleText}
          </Typography>
          <div style={{ display: 'flex', flexWrap: 'wrap' }}>
            {uniqueData?.map((data, index) => (
              <TagChip
                data-testid="tagchip"
                key={index}
                icon={badgeIcon}
                label={data.trim()}
                size="small"
                style={{ margin: '5px' }}
              />
            ))}
          </div>
        </div>
      }
      placement="bottom"
      className="m-r-md"
      arrow
    >
      <Badge data-testid={dataTestId} badgeContent={badgeContent} color="primary">
        {badgeIcon}
      </Badge>
    </Tooltip>
  );
};

export default withRouter(CAIPolicies);