import React from 'react'

import {UI_CONSTANTS} from 'utils/globals';
import CPageNotFound from 'containers/c_page_not_found';
import UISidebarTabsUtil from 'utils/ui_sidebar_tabs_util';
import CForbiddenError from 'containers/c_forbidden_error';

const Authorization = (WrappedComponent, sidebar = "", isForbidden = () => false, componentProps={}) => {
    return ({...props}) => {
        if (!isForbidden() && UISidebarTabsUtil.hasAccess(sidebar)) {
            let isVisible = UISidebarTabsUtil.isSidebarVisibleFor(sidebar);
            if (isVisible || !sidebar) {
                return <WrappedComponent {...props} {...componentProps} />
            } else {
                return <CPageNotFound {...props} />;
            }
        } else {
            return <CForbiddenError {...props} />
        }
    }
}

const getRedirectPath = (pathname='/') => {
    let landingPage = '/dashboard';
    // check if landing page is hidden, if hidden then redirect to first visible option as landing page
    // Find the menu containing the dashboard
    let menu = UISidebarTabsUtil.sideBarList.find(menu => 
        menu.child && menu.child.some(child => child.sidebar === UI_CONSTANTS.DASHBOARD)
    )
    if (menu) {
        let dashboardItem = menu.child.find(child => child.sidebar === UI_CONSTANTS.DASHBOARD);
        landingPage = dashboardItem.to;
    } else {
        // Default to first available menu item
        let firstMenu = UISidebarTabsUtil.sideBarList[0];
        if (firstMenu?.child?.length > 0) {
            landingPage = firstMenu.child[0].to;
        } else {
            landingPage = firstMenu?.to || landingPage;
        }
    }
    return landingPage;
}

export {
    Authorization, getRedirectPath
}