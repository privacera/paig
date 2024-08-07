import React from 'react'

import {UI_CONSTANTS} from 'utils/globals'
import UISidebarTabsUtil from 'utils/ui_sidebar_tabs_util';
import CPageNotFound from 'containers/c_page_not_found';
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
    //check if landing page is hidden, if hidden then redirect to first visible option as landing page
    let menu = UISidebarTabsUtil.sideBarList.find(menu => menu.sidebar == UI_CONSTANTS.DASHBOARD)
    let m = UISidebarTabsUtil.sideBarList[0];
    if (menu) {
        landingPage = menu.to;
    } else if (m) {
        if (m.child && m.child[0]) {
            landingPage = m.child[0].to;
        } else {
            landingPage = m.to;
        }
    }
    return landingPage;
}

export {
    Authorization, getRedirectPath
}