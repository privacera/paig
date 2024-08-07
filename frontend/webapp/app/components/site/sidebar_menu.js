import React from 'react';

import DashboardIcon from '@material-ui/icons/Dashboard';
import SecurityIcon from '@material-ui/icons/Security';
import InsertChartOutlinedOutlinedIcon from '@material-ui/icons/InsertChartOutlinedOutlined';

import { UI_CONSTANTS } from 'utils/globals';
import { AccountIcon, CodeWindowIcon, ShieldIcon } from './privacera_logo';


const SIDEBAR_MENU = [{
  to: "/dashboard",
  name: "Dashboard",
  icon: <DashboardIcon className="list-svg-icon" />,
  sidebar: UI_CONSTANTS.DASHBOARD
}, {
  menuToggleAttrName: "applications",
  name: "Application",
  icon: <CodeWindowIcon className="list-svg-icon" />,
  sidebar: UI_CONSTANTS.APPLICATIONS,
  child: [{
    to: "/ai_applications",
    name: "AI Applications",
    isChild: true,
    sidebar: UI_CONSTANTS.AI_APPLICATIONS,
    childrenRoutes: ["/ai_applications/", "/ai_application/create", "/ai_application/:id"]
  }, {
    to: "/vector_db",
    name: "Vector DB",
    isChild: true,
    sidebar: UI_CONSTANTS.VECTOR_DB,
    childrenRoutes: ["/vector_db/", "/vector_db/create", "/vector_db/:id"]
  }]
}, {
   menuToggleAttrName: "audits",
   name: "Security",
   icon: <SecurityIcon className="list-svg-icon" />,
   sidebar: UI_CONSTANTS.AUDITS,
   child: [{
     to: "/audits_security",
     name: "Access Audits",
     isChild: true,
     sidebar: UI_CONSTANTS.SECURITY
   }]
 }, 
// TODO: [PAIG-2025] Uncomment to enable Admin Audits
//  {
//   menuToggleAttrName: "compliance",
//   name: "Compliance",
//   icon: <ShieldIcon className="list-svg-icon" />,
//   sidebar: UI_CONSTANTS.COMPLIANCE,
//   child: [{
//     to: "/admin_audits",
//     name: "Admin Audits",
//     isChild: true,
//     sidebar: UI_CONSTANTS.ADMIN_AUDITS
//   }]
// }, 
{
  menuToggleAttrName: "reports",
  name: "Reports",
  icon: <InsertChartOutlinedOutlinedIcon className="list-svg-icon" />,
  sidebar: UI_CONSTANTS.REPORTS,
  child: [{
    to: "/built_in_reports",
    name: "Built-in Reports",
    icon: "",
    isChild: true,
    sidebar: UI_CONSTANTS.BUILT_IN_REPORTS,
    childrenRoutes: ["/built_in_reports","/built_in_reports/:reportType/new"]
  }, 
  // TODO: [PAIG-2025] Uncomments to enable Saved Reports
  // {
  //   to: "/saved_reports",
  //   name: "Saved Reports",
  //   icon: "",
  //   isChild: true,
  //   sidebar: UI_CONSTANTS.SAVED_REPORTS,
  //   childrenRoutes: ["/saved_reports", "/reports/:id/:pid"]
  // }
]
}, {
  menuToggleAttrName: "account",
  name: "Account",
  icon: <AccountIcon className="list-svg-icon" />,
  sidebar: UI_CONSTANTS.ACCOUNT,
  child: [
  // TODO: [PAIG-2025] Uncomments to enable Shield Configuration
  //   {
  //   to: "/shield_configuration",
  //   name: "Shield Configuration",
  //   isChild: true,
  //   sidebar: UI_CONSTANTS.SHIELD_CONFIGURATION
  // },
  {
    to: "/user_management",
    name: "User Management",
    isChild: true,
    sidebar: UI_CONSTANTS.USER_MANAGEMENT
  }, {
    to: "/tags",
    name: "Tags",
    isChild: true,
    sidebar: UI_CONSTANTS.SENSITIVE_DATA
  }, {
    to: "/vector_db_metadata",
    name: "Vector DB Metadata",
    isChild: true,
    sidebar: UI_CONSTANTS.META_DATA
  }]
}]

export {
  SIDEBAR_MENU
};
