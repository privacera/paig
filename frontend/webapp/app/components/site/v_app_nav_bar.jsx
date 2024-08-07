import React, {Component, Fragment, useEffect, useState} from 'react';
import {Link, useLocation} from 'react-router-dom';
import {observer} from 'mobx-react';
import {reaction} from 'mobx';
import { matchPath } from 'react-router';

import Tooltip from '@material-ui/core/Tooltip';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Collapse from '@material-ui/core/Collapse';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import Box from '@material-ui/core/Box';

import UiState from 'data/ui_state';
import UISidebarTabsUtil from 'utils/ui_sidebar_tabs_util';
import hashHistory from 'common-ui/routers/history';

const NavDrawer = ({sidebarList}) => {
  const [isHover, setHover] = useState(false);
  const location = useLocation().pathname;
  const filterParentList = sidebarList.filter(menu => !menu.isChild);

  const handleFocus = () => {
    if(document.body.classList.contains('mini-navbar') && !document.body.classList.contains('hover-effect')) {
      document.body.className = "pace-done body-small mini-navbar hover-effect"
      setHover(true);
    }
  }

  const handleBlur = () => {
    if(document.body.classList.contains('mini-navbar') && document.body.classList.contains('hover-effect')) {
      document.body.className = "pace-done body-small mini-navbar"
      setHover(false);
    }
  }

  return (
    <Drawer
      variant="permanent"
      className={"drawer " + (isHover? "drawer--hover-effect": "")}
      classes={{
        paper: "drawerPaper sidebar-padding"
      }}
      onMouseEnter={handleFocus} 
      onMouseLeave={handleBlur}
    >
      <List>
        {/* <Navheader /> */}
        {filterParentList.map(menu => <NavList key={menu.to ? menu.to : menu.name} menu={menu} location={location} />)}
      </List>
    </Drawer>
  )
};

const NavList = observer(({menu, location}) => {

  const menuToggleAttrName = menu.menuToggleAttrName ? menu.menuToggleAttrName: null;
  let isParentActive = false;
  const highlightSubMenus = (location, items = []) => {
    return items.childrenRoutes && items.childrenRoutes.some((c) => {
      //matchPath to check match path dynamic path
      return  location.includes(c) || matchPath(location, { path:c, exact:false })
    });
  }

  if(menuToggleAttrName) {
    isParentActive = menu.child.some(child => child.to === location);
    if (!isParentActive && menu.childrenRoutes) {
      isParentActive = highlightSubMenus(location, menu);
    }
  }

  useEffect(() => {
    if(isParentActive && menuToggleAttrName && !UiState.menuToggle[menuToggleAttrName]) {
      UiState.menuToggle[menuToggleAttrName] = true;
    }
  }, []);

  const handleExpandCollapse = (event) => {
    if(menuToggleAttrName) {
      UiState.menuToggle[menuToggleAttrName] = !UiState.menuToggle[menuToggleAttrName];
    }
  }

  const handleRedirectToRoute = (menu, ...props) => {
    if (menu.onClick) {
      menu.onClick(...props);
    } else {
      hashHistory.push(menu.to);
    }
  }

  const WrapLinkComponent = ({menu, children}) => {
    if (menu.to) {
      return (
        <Link  to={menu.to} onClick={(e) => e.preventDefault()} className="color-inherit sidebar-list-item"
               id={menu.to.substr(menu.to.lastIndexOf("/") + 1).toLowerCase()+"_submenu"}>
          {children}
        </Link>
      )
    }
    return (
      <Fragment>
        {children}
      </Fragment>
    )
  }

  let selectedClass = (location === menu.to ? "active-list-item": "");
  let selectedChildMenu = null;
  const menuId = menu?.to?.substr(menu.to.lastIndexOf("/") + 1).toLowerCase()+"_menu";

  return (
    <Fragment>
      {
        menuToggleAttrName ? 
          <ListItem component="li"
            className={`navlist-element border-radius-4 padding-left-right-0 pointer ${isParentActive ? 'active-list-parent': ""} ${UiState.menuToggle[menuToggleAttrName] ? 'menu-expanded' : ''}`}
            onClick={handleExpandCollapse}
            id={menuToggleAttrName+"_menu"}
            data-testid={menuToggleAttrName+"_menu"}
            data-track-id={menuToggleAttrName+"_menu"}
          >
            <button className="list-item" aria-expanded={(UiState.menuToggle[menuToggleAttrName] ? "true" : "false")} aria-controls={(menuToggleAttrName)} tabIndex="0">
              <ListItemIcon className="list-item-icon">{menu.icon}</ListItemIcon>
              <ListItemText primary={menu.name} className="list-item-text" />
              <div> {UiState.menuToggle[menuToggleAttrName] ? <ExpandLess className="list-expand-less" /> : <ExpandMore className="list-expand-more" />} </div>
            </button>
          </ListItem>
        :
          <Tooltip title={menu.istoolTip ? menu.tooltipText : ""}>
            <WrapLinkComponent menu={menu}>
              <ListItem data-testid={menuId} data-track-id={menuId} component="li" onClick={(...props) => handleRedirectToRoute(menu, ...props)}
                className={"pointer list-item border-radius-4 padding-left-right-0 " + selectedClass}
              >
                <Box display="flex" alignItems="center">
                  <ListItemIcon className="list-item-icon">{menu.icon}</ListItemIcon>
                  <ListItemText primary={menu.name} className="list-item-text" />
                </Box>
              </ListItem>
            </WrapLinkComponent>
          </Tooltip>
      }
      {
        menu.child && menu.child.length > 0 &&
        <Collapse className='collapse-list' in={UiState.menuToggle[menuToggleAttrName]} timeout='auto' unmountOnExit id={(menuToggleAttrName)}>
          <List component='ul' disablePadding>
          {
            menu.child.map((childMenu) => {
              let selectedClass = (location === childMenu.to || (childMenu.childrenRoutes && highlightSubMenus(location, childMenu)) ? "active-list-item": "");
              if(selectedClass == "active-list-item"){
                selectedChildMenu = childMenu;
              }
              const subMenuId = childMenu.to?.substr(childMenu.to.lastIndexOf("/") + 1).toLowerCase()+"_submenu";
              return (
                <Tooltip key={childMenu.to ? childMenu.to: childMenu.name} title={childMenu.istoolTip ? childMenu.tooltipText : ""}>
                  <WrapLinkComponent menu={childMenu}>
                    <ListItem
                      tabIndex="-1"
                      component="li"
                      className={"pointer border-radius-4 collapsed-list-item list-item padding-left-right-0 " + selectedClass}
                      // selected={!!selectedClass}
                      key={childMenu.to ? childMenu.to : childMenu.name}
                      onClick={(...props) => handleRedirectToRoute(childMenu, ...props)}
                      data-testid={subMenuId}
                      data-track-id={subMenuId}
                    >
                      <Box display="flex" alignItems="center" >
                        <ListItemText
                          primary={childMenu.name} 
                          className="list-item-text" 
                        />
                      </Box>
                    </ListItem>
                  </WrapLinkComponent>
                </Tooltip>
              );
            })
          }
          </List>
        </Collapse>
      }
      { !UiState.menuToggle[menuToggleAttrName] && selectedChildMenu ?
          <List component='ul' disablePadding>
            <Tooltip key={selectedChildMenu.to ? selectedChildMenu.to: selectedChildMenu.name} title={selectedChildMenu.istoolTip ? selectedChildMenu.tooltipText : ""}>
              <WrapLinkComponent menu={selectedChildMenu}>
                <ListItem
                    tabIndex="-1"
                    component="li"
                    className={"pointer border-radius-4 list-item active-list-item padding-left-right-0"}
                    // selected={!!selectedClass}
                    key={selectedChildMenu.to ? selectedChildMenu.to : selectedChildMenu.name}
                    onClick={(...props) => handleRedirectToRoute(selectedChildMenu, ...props)}
                >
                  <Box display="flex" alignItems="center" >
                    <ListItemText
                        primary={selectedChildMenu.name}
                        className="list-item-text m-l-37"
                    />
                  </Box>
                </ListItem>
              </WrapLinkComponent>
            </Tooltip>
          </List> : null
      }
    </Fragment>
  )
})

@observer
class AppNavBar extends Component {
  constructor(props) {
    super(props);

    //listen to reaction and render this component
    this.dispose = reaction(
      () => UiState.refreshMenu,
      () => {
        if (UiState.refreshMenu) {
          //doing this to get latest sidebarmenu changes
          UISidebarTabsUtil._getSidebarList();
          this.setState({});
          UiState.refreshMenu = false;
        }
      }
    )
  }

  componentWillUnmount(){
    // dispose the reaction method
    if (this.dispose) {
      this.dispose();
    }
    delete this.dispose;
  }

  render() {
    const sidebarList = UiState.getSideBarList();
    return (
      <div id="wrapper">
        <nav className="navbar-default navbar-static-side" role="navigation" aria-label="Main navigation">
          <div className="sidebar-collapse">
            <ul className="nav metismenu" id="side-menu">
              <NavDrawer sidebarList={[...sidebarList]}/>
            </ul>
          </div>
        </nav>
      </div>
    )
  }
}

export default AppNavBar;