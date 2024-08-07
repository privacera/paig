/* library imports */
import React, {Component} from 'react';

/* other project imports */
import { Grid, Typography } from '@material-ui/core';

import BaseContainer from 'containers/base_container';
import {ErrorLogo} from 'components/site/v_error_page_component';

class CForbiddenError extends Component {

  constructor(props){
    super(props);
  }

  render () {
    return (
      <BaseContainer showName={false} showRefresh={false} routes={null}>
        <Grid container className="text-center">
          <div className="page-error-container">
            <div className="page-error-left text-left">
              <Typography variant="h4" className="m-b-md">Access Denied</Typography>
              <Typography variant="body1" className="m-b-xs">Error Code: 403</Typography>
              <Typography variant="body2">Sorry, you don't have permission to use this portal</Typography>
              <Typography variant="body2">Please contact your System Administrator</Typography>
            </div>
            <div className="page-error-right">
              <ErrorLogo errorCode="403" />
            </div>
          </div>
        </Grid>
      </BaseContainer>
    );
  }
}

export default CForbiddenError;