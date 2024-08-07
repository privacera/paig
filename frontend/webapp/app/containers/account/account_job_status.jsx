import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {inject} from 'mobx-react';

import {JobProgressContainer} from 'containers/base_container';

@inject('jobManagerStore')
class AccountJobStatus extends Component {
  state = {
    status: 'IN_PROGRESS'
  }
  componentDidMount() {
    this.checkJobStatus();
  }
  componentWillUnmount() {
    clearTimeout(this.jobStatusTimer);
    this.jobStatusTimer = null;
  }
  checkJobStatus = async () => {
    let {jobManagerStore, pollJobStatus} = this.props;
    try {
      const {models} = await jobManagerStore.getJobDetail({
        params: {
          size: 1,
          jobType: 'PCLOUD_BOOTSTRAP_TENANT'
        }
      })

      let data = models.length > 0 ? models[0] : null;
      if (data && data.status === 'SUCCESS') {
        pollJobStatus(true)
      } else {
        clearTimeout(this.jobStatusTimer);
        this.jobStatusTimer = setTimeout(this.checkJobStatus, 3000);
        this.setState({status: data.status})
      }
    } catch(e) {
      console.log('Error checking job status', e);
      pollJobStatus(true)
    }
  }
  render() {
    return (
      <JobProgressContainer
        status={this.state.status}
      />
    );
  }
}

AccountJobStatus.propTypes = {
  pollJobStatus: PropTypes.func
};

export default AccountJobStatus;