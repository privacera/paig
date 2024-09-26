import {hot} from 'react-hot-loader';
import React, {Component, createRef} from 'react';
import {reaction} from 'mobx';
import {Provider} from 'mobx-react'
import { withRouter } from "react-router";
import { SnackbarProvider } from 'notistack';
//import DevTools from 'mobx-react-devtools';

import {withStyles} from '@material-ui/core/styles';
import { ThemeProvider } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

import theme from 'components/site/theme';
import {Routes} from 'routers/routes';
import UiState from 'data/ui_state'
import UISidebarTabsUtil from 'utils/ui_sidebar_tabs_util';
import AccountJobStatus from 'containers/account/account_job_status';
import {PaigLoader} from 'components/site/paig_logo';
import {FailedTenantSetup} from 'containers/base_container';
import f from 'common-ui/utils/f';
import {createRoutes} from 'common-ui/lib/RouteUtils';
import {Confirm} from 'common-ui/lib/fs_modal';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import "pdfmake/build/pdfmake";
import PDFUtil from 'components/reports/reports_pdfUtil';
import PendoInitializer from 'components/pendo/pendo_initializer';

if (PDFUtil && PDFUtil.loadFonts) {
  PDFUtil.loadFonts();
}

const SnackbarStyleComponent = withStyles((theme) => ({
  containerRoot: {
    wordBreak: 'break-word !important',
    wordWrap: 'break-word !important',
    maxWidth: 'calc(30% - 40px)'
  },
  contentRoot: {
    flexWrap: 'nowrap'
  },
  action: {
    paddingLeft: 0
  }
}))(SnackbarProvider);

class Root extends Component {
  constructor(props) {
    super(props);
    this.notificationSystem = createRef();
    this.confirm = createRef();

    permissionCheckerUtil.setUp();

    reaction(
      () => UiState.refreshProps,
      () => {
        // if (UiState.refreshProps) {
          // this.refresh();
        // }
      }
    )
  }
  state = {
    error: false,
    loaded: false,
    jobLoaded: false,
    pendoApiKey: null,
    pendoHost: null
  }
  async fetch() {
    try {
      UISidebarTabsUtil.setStores(this.props.stores);
      await UiState.fetch();
      this.setState({loaded: true});
      UiState.setRefreshProps(false);
    } catch(e) {
      console.log(e);
      this.setState({error: true, loaded: true});
      return;
    }

    /*
    let pendoApiKey = null;
    let pendoHost = null;
    try {
      let {models} = await this.props.stores.generalStore.getAllProperties();
      let model = models.find(model => model.name === 'TRACKING_KEY')
      let host = models.find(model => model.name === 'TRACKING_HOST')
      if (model) {
        pendoApiKey = model.value;
        pendoHost = host?.value || null;

        setTimeout(() => {
          this.setupPendo();
        }, 100)
      }
      
    } catch (e) {
      console.log(e);
    }

    this.setState({loaded: true, pendoApiKey, pendoHost});
    */
  }
  async refresh() {
    const { history: hashHistory } = this.props
    this.setState({loaded: false});
    try {
      const load = await UiState.refreshProperties();
    } catch(e) {
    	console.log('Error loading properties', e);
    }
    this.setState({loaded: true});
    UiState.setRefreshProps(false);
  }
  setupPendo = () => {
    // This function creates visitors and accounts in Pendo
    // You will need to replace <visitor-id-goes-here> and <account-id-goes-here> with values you use in your app
    // Please use Strings, Numbers, or Bools for value types.

    let user = UiState.getLoggedInUser();
    pendo?.initialize({
      visitor: {
        id: user.email,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        full_name: `${user.firstName}${user.lastName ? (' ' + user.lastName) : ''}`,
        // keycloakId: user.keycloakId,
        roles: user.tenants[0].roles.join(', ')
      },
      account: {
        id: user.tenants[0].tenantId
      }
    });
  }
  componentDidMount() {
    this.fetch();
    f.setNotificationSystem(this.notificationSystem.current);
    f.setConfirmBox(this.confirm.current);
  }
  handlePollJobStatus = (jobLoaded) => {
    this.setState({jobLoaded});
  }
  onClickDismiss = key => () => {
    this.notificationSystem.current.closeSnackbar(key);
  }
  render() {
    const {state, onClickDismiss} = this;
    const {stores={}} = this.props;

    let renderComponent = null;
    if (state.loaded) {
      if (state.error) {
        renderComponent = <FailedTenantSetup />
      } else if (state.jobLoaded) {
        renderComponent = Routes();
        UiState.setRoutes(createRoutes(renderComponent.props.children));
      } else {
        renderComponent = <AccountJobStatus pollJobStatus={this.handlePollJobStatus} />
      }
    }

    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Provider { ...stores }>
          <SnackbarStyleComponent ref={this.notificationSystem} maxSnack={10}
            action={(key) => (
              <IconButton data-testid="snackbar-close-btn" onClick={onClickDismiss(key)}>
                <CloseIcon className="text-white" />
              </IconButton>
            )}
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
          >
            { state.loaded ? renderComponent : <PaigLoader /> }
            {
              state.pendoApiKey &&
              <PendoInitializer apiKey={state.pendoApiKey} host={state.pendoHost} />
            }
            <Confirm ref={this.confirm} maxWidth="xs" />
            {/*<DevTools />*/}
          </SnackbarStyleComponent>
        </Provider>
      </ThemeProvider>
    )
  }
}

export default hot(module)(withRouter(Root));