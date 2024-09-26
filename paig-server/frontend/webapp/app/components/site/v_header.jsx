import { observable } from 'mobx';
import { inject, observer } from 'mobx-react';
import React, { Component, Fragment, createRef } from 'react';
import { Link } from 'react-router-dom';

import AppBar from '@material-ui/core/AppBar';
import Box from '@material-ui/core/Box';
import IconButton from '@material-ui/core/IconButton';
import MUILink from '@material-ui/core/Link';
import MenuItem from '@material-ui/core/MenuItem';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import AccountCircleIcon from '@material-ui/icons/AccountCircle';
import ArrowDropDownIcon from '@material-ui/icons/ArrowDropDown';
import MenuIcon from '@material-ui/icons/Menu';

import UiState from 'data/ui_state';
import { CommandDisplay } from 'common-ui/components/action_buttons';
import { PopperMenu } from 'common-ui/components/generic_components';
import { createFSForm } from 'common-ui/lib/form/fs_form';
import FSModal from 'common-ui/lib/fs_modal';
import UserManagementForm from 'components/user_management/v_user_management_form';
import { user_form_def } from 'components/user_management/user_form_def';
import { BookIcon } from './privacera_logo';
import { DarkPaigLogo } from './paig_logo';

@inject('userStore')
@observer
class ProfileMenu extends Component {
  @observable _vState = {
    popoverOpen: null
  };

  constructor(props) {
    super(props);
    // this.permission = permissionCheckerUtil.getPermissions(FEATURE_PERMISSIONS.PORTAL.USER.PROPERTY);
    this.initializeRefs();
    this.form = createFSForm( user_form_def );
  }

  initializeRefs = () => {
    this.aboutModal = createRef();
    this.profileModal = createRef();
    this.Modal = createRef();
  }

  handleProfileEdit = (callback) => {
    if(callback){
      callback()  
    }
    const { rolePermissions, ...restProps } = UiState.user;
    if (this.profileModal.current) {
      this.form.clearForm();
      this.form.model = UiState.user;
      this.form.refresh({
        ...restProps,
        roles: rolePermissions.map((r) => r.role)
      });
      this.profileModal.current.show({
        showOkButton: false
      });
    }
  }

  renderLink = (label, onClick) => {
    const handleOnClick = () => {
      this.handleClose();
      if(onClick) {
        onClick();
      }
    }
    return (
      <div className="m-b-sm">
        <MUILink onClick={handleOnClick}>{label}</MUILink>
      </div>
    )
  }

  handleModalClose = () => {
    if (this.supportWrapper.current && this.supportWrapper.current.contactSupport) {
      this.supportWrapper.current.contactSupport.current.hide();
    }
  }

  handleClose = () => {
    this._vState.popoverOpen = null;
  }

  handleAbout = () => {
    if (this.aboutModal.current) {
      this.aboutModal.current.show({ showOkButton: false });
    }
  }

  render() {
    return (
      <Fragment>
        <li className="dropdown m-r-sm">
          <PopperMenu
            buttonType="Button"
            isButtonContained={false}
            menuListProps={{
              tabIndex: null
            }}
            label={(
              <Fragment>
                <Typography component="div" className="header--nav-text" data-track-id="header-user-email" >
                  <Box display='inline'>
                    <AccountCircleIcon /> {UiState.user ? UiState.user.username : '--'}
                  </Box>
                </Typography>
                <ArrowDropDownIcon />
              </Fragment>
            )}
            buttonProps={{
              size: 'small',
              'aria-label': 'account of current user',
              'aria-controls': 'menu-appbar',
              'aria-haspopup': 'true',
              className: 'header--menu-email'
            }}
            renderCustomMenus={(handleClose) => {
              return([
                <MenuItem 
                  key="1" 
                  variant={'primary'}
                  disableTouchRipple={true}
                  className="no-highlight-hover"
                >
                  <div className="copy-tenent" data-track-id="account-id">
                    <Typography key={1} variant="caption" color="textSecondary" className="priv-username-display-name-label">
                      Account Id:
                    </Typography>
                    <CommandDisplay id="tenent-id" command={UiState.getTenantId()} />
                    <hr className='m-0' />
                  </div>
                </MenuItem>,
                <MenuItem 
                  key="2"
                  variant="primary"
                  data-track-id="profile"
                  onClick={(e) => {this.handleProfileEdit(handleClose)}}
                > 
                  Profile
                </MenuItem>,
                <MenuItem 
                  data-testid="logout"
                  key="3"
                  variant="primary"
                  data-track-id="logout"
                  onClick={() => {
                    UiState.logout();
                    handleClose();
                  }}
                >
                  Log Out
                </MenuItem>
              ])
            }}
          />
          {
            UiState.user &&
            <FSModal ref={this.profileModal} dataTitle={'User Profile'}>
              <UserManagementForm form={this.form} isProfile={true}/>
            </FSModal>
          }
        </li>
      </Fragment>
    )
  }
}

@observer
class NavbarHeaderRight extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (!UiState.user) {
      return null
    }

    return (
      <nav aria-label="account-navigation">
        <Box component="ul" className="navbar-top-links navbar-right">
          <Box data-track-id="documentation" onClick = {() => {window.open("docs/", '_blank')}} className="pointer">
            <BookIcon className="list-svg-icon"/> Documentation
          </Box>
          <ProfileMenu />
        </Box>
      </nav>
    );
  }
}

class Header extends Component {

  render() {
    return (
      // <nav className="navbar-static-top">
      <Fragment>
        <div className="header--root">
          <AppBar position="fixed" className="header--app-bar">
            <Toolbar className="MuiToolbar-medium">
              <Box className="header--flex-space">
                <Box className="header--logo-container">
                  <IconButton
                    edge="start"
                    className="header--menu-button"
                    data-track-id="header-menu-button"
                    aria-label="menu"
                    onClick={() => UiState.toggleSideBar()}
                  >
                    <MenuIcon />
                  </IconButton>
                  <Navheader />
                </Box>
                <Box display="flex" alignItems="center">
                  <NavbarHeaderRight />
                </Box>
              </Box>
            </Toolbar>
          </AppBar>
        </div>
      </Fragment>
    );
  }
}

class Navheader extends Component {
  render() {
    return(
      <div className="header--logo" data-track-id="privacera-logo" aria-label="Privacera logo" aria-describedby="Click here for homepage">
        <div className="dropdown profile-element" aria-hidden="true">
          <span>
            <Link to="/">
              <DarkPaigLogo />
            </Link>
          </span>
        </div>
      </div>
    );
  }
}

export default Header;