/* library imports */
import React, {Component} from 'react';

/* other project imports */
import { Grid, Typography, Button } from '@material-ui/core';
import KeyboardArrowLeftIcon from '@material-ui/icons/KeyboardArrowLeft';

import BaseContainer from 'containers/base_container';
import {ErrorLogo} from 'components/site/v_error_page_component';

class CPageNotFound extends Component {

  constructor(props){
    super(props);
  }

  handleGoBack = () => {
    this.props.history.goBack();
  }

  render () {
    return (
      <BaseContainer showRefresh={false} routes={null}>
        <Grid container className="text-center">
          <div className="page-error-container">
            <div className="page-error-left text-left">
              <Typography variant="h4" className="m-b-md">Page Not Found</Typography>
              <Typography variant="body1" className="m-b-xs">Error Code: 404</Typography>
              <Typography variant="body2">It seems that this page doesn’t exist or has been removed</Typography>
              <Button variant="contained" color="primary" size="small" className="m-t-md" onClick={() => this.handleGoBack()}>
                <KeyboardArrowLeftIcon fontSize="small" /> Go Back
              </Button>
            </div>
            <div className="page-error-right">
              <ErrorLogo />
            </div>
          </div>
        </Grid>
      </BaseContainer>
    );
  }
}

export default CPageNotFound;