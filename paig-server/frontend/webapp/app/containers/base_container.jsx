import React, {Component, Fragment} from 'react';
import { withRouter } from 'react-router';

import {Grid, Button, Box, Typography, LinearProgress} from '@material-ui/core';
import KeyboardArrowLeftIcon from '@material-ui/icons/KeyboardArrowLeft';

import Navbar from 'components/site/v_header';
import PageSidebar from 'components/site/v_app_nav_bar';
import UiState from 'data/ui_state';
import {ErrorLogo} from 'components/site/v_error_page_component';
import {Utils} from 'common-ui/utils/utils';
/* import {TourManager2} from 'common-ui/components/generic_components'; */
import {RefreshButton, BackButton} from 'common-ui/components/action_buttons';

class PageContent extends Component {
  render() {
    let name = this.props.title || this.props.pageTitle;

    const {match} = this.props;
    let allRoutes = UiState.getRoutes();
    if (allRoutes != null && allRoutes.length) {
      let route = allRoutes.find(route => route.path == match.path);
      if (route) {
        name = name || route.name || '';
      }
    }
    const {
      showName, handleRefresh, children, showBackButton, backButtonProps, headerChildren, showRefresh, titleColAttr,
      showBreadCrumb, breadcrumbBgColor, nameProps, containerClasses
    } = this.props;

    return (
      <div className="main-page">
        {
          showBreadCrumb &&
          <Grid container spacing={3} alignItems="center"
            style={{backgroundColor: breadcrumbBgColor || ''}}
            className={containerClasses}
          >
            {
              (showBackButton || showName || showRefresh) &&
              <Grid item xs={12} md={'auto'} {...titleColAttr}>
                <Box display="flex" alignItems="center">
                  {showBackButton && 
                    <BackButton
                      size="medium"
                      {...backButtonProps}
                    />
                  }
                  {showName && <Box data-testid="page-title" component={Typography} variant="h5" style={{fontWeight: '400', color: '#000000'}}  {...nameProps} >{name}</Box>}
                  {
                    showRefresh &&
                    <RefreshButton
                      data-testid="header-refresh-btn"
                      data-track-id="refresh-button"
                      wrapItem={false}
                      pullRight={false}
                      onClick={handleRefresh}
                    />
                  }
                </Box>
              </Grid>
            }
            {headerChildren}
          </Grid>
        }
        <Grid container spacing={3} className="m-b-sm">
          <Grid item xs={12} md={12} sm={12}>
            {children}
          </Grid>
        </Grid>
        <Footer />
      </div>
    );
  }
}

PageContent.defaultProps = {
  showRefresh: true,
  showName: true,
  titleColAttr: {},
  showBackButton: false,
  showBreadCrumb: true,
  nameProps: {}
}

class BaseContainer extends Component {
  render() {
    return (
      <div id="base-container">
        <header>
          <Grid container >
            <Grid item xs={12}>
              <Box className="border-bottom nav-height">
                <Navbar/>
              </Box>
            </Grid>
          </Grid>
        </header>
        <PageSidebar {...this.props} />
        <PageContent 
          routes={this.props}
          pageTitle={this.props.pageTitle}
          children={this.props.children}
          {...this.props}
        />
        {/* <TourManager2 /> */}
      </div>
    )
  }
}

const JobProgressContainer = ({status}) => {
  return (
    <div id="base-container">
      <header>
        <Grid container >
          <Grid item xs={12}>
            <Box className="border-bottom nav-height">
              <Navbar/>
            </Box>
          </Grid>
        </Grid>
      </header>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Box mt={5} className="loader-container">
            <div className="loader-inner">
              {
                status === 'FAILED'
                ?
                  (
                    <Fragment>
                      <Typography variant="h5" className="m-b-sm">
                        PAIG AI Signup Rush!
                      </Typography>
                      <Typography variant="body2" className="m-b-sm">
                        We are currently experiencing a higher-than-usual volume of sign-ups, which may result in a slight delay in setting up your account.
                        We recommend trying to log in again in a few minutes.
                      </Typography>
                      <Typography variant="body2" className="m-b-sm">
                        If you continue to experience issue, please reach out to our support team at <a href="mailto:paig-support@privacera.com" target="_blank">paig-support@privacera.com</a>.
                      </Typography>
                      <Typography variant="body2" className="m-b-sm">
                        We appreciate your patience!
                      </Typography>
                      <LinearProgress />
                    </Fragment>
                  )
                :
                  (
                    <Fragment>
                      <Typography variant="h5" className="m-b-sm">
                        Your account is being prepared. This initial setup might take a few minutes.
                      </Typography>
                      <LinearProgress />
                    </Fragment>
                  )
              }
            </div>
          </Box>
        </Grid>
      </Grid>
    </div>
  )
}

const Footer = () => {
  const moment = Utils.dateUtil.momentInstance();
  return (
      <div className="footer">
        <div className="pull-right">
          &copy; {moment().year()} Privacera, Inc. All rights reserved.
        </div>
      </div>
  )
}

const FailedTenantSetup = () => {
  return (
    <Grid container className="text-center">
      <div className="page-error-container m-t-xl">
        <div className="page-error-left text-left">
          <Typography variant="h4" className="m-b-md">Oops! Something went wrong</Typography>
          <Typography variant="body2">Our server's swamped right now. We're either handling too many requests or doing some quick maintenance. Don't sweat it, we'll be back on track ASAP! Need help urgently?</Typography>
          <Typography variant="body2">Contact our support team <a href="mailto:paig-support@privacera.com" target="_blank">here.</a></Typography>
          <Button variant="contained" color="primary" size="small" className="m-t-md" onClick={UiState.logout}>
            <KeyboardArrowLeftIcon fontSize="small" /> Home
          </Button>
        </div>
        <div className="page-error-right">
          <ErrorLogo errorCode="500" />
        </div>
      </div>
    </Grid>
  )
}

BaseContainer.defaultProps = {
  showBreadCrumb: true,
  containerClasses: ''
}

export default withRouter(BaseContainer);
export {
  JobProgressContainer,
  FailedTenantSetup
}