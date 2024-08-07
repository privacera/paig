import React, {Component, Fragment} from 'react';
import {observer,inject} from 'mobx-react';

import Chip from '@material-ui/core/Chip';
import Typography from '@material-ui/core/Typography';

import f from 'common-ui/utils/f';
import {ACTION_TYPE} from 'utils/globals';
import {Utils} from 'common-ui/utils/utils';
import {DATE_TIME_FORMATS} from 'common-ui/utils/globals';
import {Loader, getSkeleton} from 'common-ui/components/generic_components';
import VAdminAuditsOperationDetailView from 'components/compliance/v_admin_audits_operation_detail';

@observer
@inject('adminAuditsStore')
class CAdminAuditsOperationDetail extends Component {
  constructor(props) {
    super(props);

    this.cAdminAuditsOperationDetail = f.initCollection();
    this.cAdminAuditsOperationDetail.params = {
      sort: 'transactionSequenceNumber,asc',
      "includeQuery.transactionId": this.props.operationDetailObj?.transactionId
    }

  }

  componentDidMount() {
    this.getOperationDetail();
  }

  getOperationDetail() {
    f.beforeCollectionFetch(this.cAdminAuditsOperationDetail);
    this.props.adminAuditsStore.fetchComplianceAudits({
      params: this.cAdminAuditsOperationDetail.params
    })
    .then(f.handleSuccess(this.cAdminAuditsOperationDetail), f.handleError(this.cAdminAuditsOperationDetail));
  }

  render() {
    const {operationDetailObj} = this.props;
    return (
      <Fragment>
        <Loader promiseData={this.cAdminAuditsOperationDetail} loaderContent={getSkeleton('THREE_SLIM_LOADER')}>
          <div data-testid="admin-audits-operation-detail">
            {operationDetailObj.action === ACTION_TYPE.UPDATE.VALUE &&
              <div className="pull-right" data-testid="update-indicators">
                <span key={1} className="diff-primary diff-label" data-testid="added-indicator"></span>
                <span style={{verticalAlign: 'middle'}}>Added</span>
                <span key={2} className="m-l-sm diff-danger diff-label" data-testid="deleted-indicator"></span>
                <span style={{verticalAlign: 'middle'}}>Deleted</span>
              </div>
            }
            {operationDetailObj.objectId && 
              <div key={1} className="m-b-sm" data-testid="object-id">
                <Typography variant="body2">
                  <b>ID:</b> <Chip size="small" color="primary" label={operationDetailObj.objectId}/>
                </Typography>
              </div>
            }
            {operationDetailObj.objectName &&
              <div key={2} className="m-b-sm" data-testid="object-name">
                <Typography variant="body2">
                  <b>Name:</b> <span>{operationDetailObj.objectName}</span>
                </Typography>
              </div>
            }
            <div key={3} className="m-b-sm" data-testid="log-time">
              <Typography variant="body2">
                <b>{Utils.toTitleCase(operationDetailObj.action)} Date:</b> <span>{operationDetailObj.logTime ? Utils.dateUtil.getTimeZone(operationDetailObj.logTime, DATE_TIME_FORMATS.DATE_FORMAT) : '--'}</span>
              </Typography>
            </div>
            <div key={4} className="m-b-sm" data-testid="acted-by">
              <Typography variant="body2">
                <b>{Utils.toTitleCase(operationDetailObj.action)} By:</b> <span>{operationDetailObj.actedByUsername}</span>
              </Typography>
            </div>              
            <VAdminAuditsOperationDetailView operationData={this.cAdminAuditsOperationDetail} />
          </div>
        </Loader>
      </Fragment>
    )
  }
}

CAdminAuditsOperationDetail.defaultProps = {
  vName: 'adminAuditsOperationDetail'
}

export default CAdminAuditsOperationDetail;