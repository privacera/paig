import {observable} from 'mobx';
import {isEmpty, set, get, hasIn} from 'lodash';

import {UI_CONSTANTS} from 'utils/globals';
import {SIDEBAR_MENU} from 'components/site/sidebar_menu';
import {configProperties} from 'utils/config_properties';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';

const {
    PAIG_LENS,
    PAIG_NAVIGATOR,
    PAIG_GUARD,
    SETTINGS,
	DASHBOARD,
    AI_APPLICATIONS,
    SECURITY,
    AUDITS,
    ACCOUNT,
    SHIELD_CONFIGURATION,
    PORTAL_USERS,
    PORTAL_GROUPS,
    VECTOR_DB,
    COMPLIANCE,
    ADMIN_AUDITS,
    SENSITIVE_DATA,
    META_DATA,
    META_DATA_VALUES,
    DOCS,
    REPORTS,
    BUILT_IN_REPORTS,
    SAVED_REPORTS,
    REPORTING,
    AI_APPLICATIONS_PERMISSIONS,
    VECTOR_DB_PERMISSIONS,
    EVALUATION,
    EVALUATION_CONFIG,
    EVALUATION_REPORTS,
    USERS
} = UI_CONSTANTS

const SIDEBAR_MENU_ITEMS = {
    [PAIG_NAVIGATOR]: {
        SUBMENU: {
            [AI_APPLICATIONS]: {
                TABS: [AI_APPLICATIONS, AI_APPLICATIONS_PERMISSIONS]
            },
            [VECTOR_DB]: {
                TABS: [VECTOR_DB, VECTOR_DB_PERMISSIONS]
            }
        }
    },
    [PAIG_LENS]: {
        SUBMENU: {
            [DASHBOARD]: {},
            [EVALUATION_CONFIG] : {},
            [EVALUATION_REPORTS] : {},
            [SECURITY]: {},
            [BUILT_IN_REPORTS]: {}
        }
    },
    [PAIG_GUARD]:{
        SUBMENU: {
            [SENSITIVE_DATA]: {},
            [META_DATA]: {}
        }
    },
    [SETTINGS]: {
        SUBMENU: {
            [USERS]: {
                TABS: [PORTAL_USERS, PORTAL_GROUPS]
            },
            [SHIELD_CONFIGURATION]: {}
        }
    }
}

const UI_FEATURE_SIDEBAR_TABS = {
    [SHIELD_CONFIGURATION]: {
        [SETTINGS]: {
            [SHIELD_CONFIGURATION]: {}
        }
    },
    [VECTOR_DB]: {
        [PAIG_NAVIGATOR]: {
            [VECTOR_DB]: {
                TABS: [VECTOR_DB, VECTOR_DB_PERMISSIONS]
            }
        },
        [PAIG_GUARD]: {
            [META_DATA]: {}
        }
    },
    [EVALUATION]: {
        [PAIG_LENS]: {
            [EVALUATION_CONFIG]: {},
            [EVALUATION_REPORTS]: {}
        }
    }
}

const UI_DEFAULT_FEATURE_SIDEBAR_TABS = {
    [PAIG_NAVIGATOR]: {
        [AI_APPLICATIONS]: {
            TABS: [AI_APPLICATIONS, AI_APPLICATIONS_PERMISSIONS]
        }
    },
    [PAIG_LENS]: {
        [DASHBOARD]: {},
        [SECURITY]: {},
        [BUILT_IN_REPORTS]: {}
    },
    [PAIG_GUARD]:{
        [SENSITIVE_DATA]:{}
    },
    [SETTINGS]: {
        [USERS]: {
            TABS: [PORTAL_USERS, PORTAL_GROUPS]
        }
    }
}

class UISidebarTabsUtil {

    sideBarList = [];
    @observable properties = {};
    propertiesForShowHide = {};

    constructor() {
        this._createDefaultProperties();
    }
    setStores(stores) {
        this.stores = stores;
    }
    setProperties = (properties) => {
        this.properties = properties;
    }
    async fetchProperties() {
        try {
            // let properties = await stores.publicStore.getFeatureFlags();
            // this.properties = this.sortPropertiesInOrder(properties.models)
            this.properties = this.sortPropertiesInOrder([/*{
                "name": "SHIELD_CONFIGURATION",
                "value": 'true'
            },*/ {
                "name": "VECTOR_DB",
                "value": 'true'
            }, 
            {
                "name": "EVALUATION",
                "value": 'true'
            }
        ])
        } catch (e) {
            console.error("Failed to fetch system properties", e);
        }
        configProperties.setProperties(this.properties);
        return this.properties;
    }
    sortPropertiesInOrder = (properties) => {
        let featureSidebarTabs = [...Object.keys(UI_FEATURE_SIDEBAR_TABS)];

        let foundProperties = [];
        let extraProperties = [];

        properties.forEach(property => {
            let index = featureSidebarTabs.indexOf(property.name.toUpperCase());
            if (index > -1) {
                foundProperties[index] = property;
            } else {
                extraProperties.push(property);
            }
        })

        return [...foundProperties.filter(prop => prop), ...extraProperties.filter(prop => prop)];
    }
    async evalPropertiesForAccessControl() {
        this.properties.forEach(property => {
            let name = property.name.toUpperCase();
            let value = property.value;

            if (!value) {
                return;
            }
            value = value.toLowerCase();

            let mainFeatureOptions = UI_FEATURE_SIDEBAR_TABS[name]
            let partFeatureOptions = null;//UI_PART_FEATURE_SIDEBAR_TABS[name];

            if (!mainFeatureOptions && !partFeatureOptions) return;

            let featureOptions = mainFeatureOptions || partFeatureOptions;

            let isEnable = (value == "enable" || value == "enabled" || value == "true");
            //if feature is disable then check if its for part feature, if its for partfeature then let it proceed
            if (isEnable || partFeatureOptions) {
                let empty = isEmpty(featureOptions)
                if (empty) {
                    set(this.propertiesForShowHide, name, isEnable)
                } else if (value) {
                    this._handleHierarchy(isEnable, featureOptions);
                }
            }
        });

        this._handleHierarchy(true, UI_DEFAULT_FEATURE_SIDEBAR_TABS);

        let list = permissionCheckerUtil.getUISidebarAndTabsDenyList();
        if (list) {
            list.forEach(property => {
                let uiProperty = featurePermissionUIMap[property];
                if (uiProperty && uiProperty.propertyForShowHide) {
                    this.hideUIForProperty(uiProperty.propertyForShowHide);
                }
            })
        }
        // evalMenuItems.setProperties(this.propertiesForShowHide);
        // await evalMenuItems.checkAllConditions();

        //sidebar show hide property check
        this._getSidebarList();
        return this.propertiesForShowHide;
    }
    getPropertiesForShowHide() {
        return this.propertiesForShowHide;
    }
    _createDefaultProperties() {
        let sidebarMenuItems = Object.keys(SIDEBAR_MENU_ITEMS);
        let properties = {}

        sidebarMenuItems.forEach(menuitemKey => {
            let property = {};
            property = this._createProperty(SIDEBAR_MENU_ITEMS[menuitemKey], property);
            properties[menuitemKey] = property;
        })
        this.propertiesForShowHide = properties;
    }
    _createProperty(menuItems = {}, property) {
        let tabs;
        if (menuItems.TABS) {
            tabs = menuItems.TABS;
        } else if (menuItems.SUBMENU) {
            let keys = Object.keys(menuItems.SUBMENU);
            keys.forEach(key => {
                property[key] = this._createProperty(menuItems.SUBMENU[key], {});
            });
        }

        if (tabs) {
            tabs.forEach(tab => property[tab] = false);
        }
        return isEmpty(property) ? false : property;
    }
    getSidebarList() {
        return this.sideBarList;
    }
    _getSidebarList() {
        let list = [];
        // if (!this.sideBarList.length) {
        SIDEBAR_MENU.forEach(sideMenu => {
            let menu = {...sideMenu};
            let menuOption = this.propertiesForShowHide[menu.sidebar.toUpperCase()];
            if (typeof menuOption == "boolean" && menuOption) {
                list.push(menu);
            }
            if (typeof menuOption == "object") {
                if (menu.child) {
                    //this is sub menu, filter out sub menu

                    menu.child = sideMenu.child.filter(childMenu => {
                        let child = menuOption[childMenu.sidebar.toUpperCase()]
                        if (child == undefined) {
                            return false;
                        }
                        if (typeof child == 'boolean') {
                            return child;
                        }
                        //has tabs
                        if (typeof child == "object") {
                            return this._isTabsVisible(child);
                        }
                    })
                    if (menu.child.length) {
                        list.push(menu);
                    }
                } else if (this._isTabsVisible(menuOption)) {
                    //this has tab
                    list.push(menu);
                }
            }
            return false;
        });
        // }
        this.sideBarList = list;
        return this.sideBarList;
    }
    _isTabsVisible(menuOption) {
        return Object.values(menuOption).some(menu => {
            if (typeof menu == 'object') {
                return this._isTabsVisible(menu);
            }
            return menu;
        });
    }
    filterTabsList(name, list) {
        let property = this.getProperty(name);
        if (property) {
            list = list.filter(view => {
                let isNested = view.tab.split('.').length > 1;
                if (isNested) {
                    return this.getProperty(view.tab, property);
                }
                return property[view.tab];
            })
        }
        return list;
    }
    getProperty(name, properties = this.propertiesForShowHide) {
        if (!name) {
            return;
        }
        if (Array.isArray(name)) {
            name = name.join('.');
        }
        let foundProperty = get(properties, name);
        if (!foundProperty) {
            return;
        }
        return foundProperty;
    }
    _handleHierarchy(propertyValue, featureOptions, key = "") {
        let sidebarList = Object.keys(featureOptions);
        sidebarList.forEach(sidebarKey => {
            let sidebarOption = featureOptions[sidebarKey]
            if (sidebarOption && sidebarOption.TABS) {
                sidebarOption.TABS.forEach(sidebarOpt => {
                    let hierarchyKey = key + `${sidebarKey}.${sidebarOpt}`;
                    if (hasIn(this.propertiesForShowHide, hierarchyKey)) {
                        set(this.propertiesForShowHide, hierarchyKey, propertyValue)
                    }
                })
            } else if (isEmpty(sidebarOption)) {
                let hierarchyKey = key + `${sidebarKey}`;
                set(this.propertiesForShowHide, hierarchyKey, propertyValue)
            } else if (sidebarOption) {
                this._handleHierarchy(propertyValue, sidebarOption, `${sidebarKey}.`);
            }
        })
    }
    hideUIForProperty(property) {
        if (!Array.isArray(property)) {
            property = [property];
        }
        property.forEach(p => {
            let prop = get(this.propertiesForShowHide, p);
            if (prop) {
                if (typeof prop == 'object') {
                    Object.keys(prop).forEach(key => {
                        if (prop[key] == 'object') {

                        } else {
                            prop[key] = false;
                        }
                    })
                } else if (typeof prop == 'boolean') {
                    set(this.propertiesForShowHide, p, false);
                }
            }
        })
    }

    isSidebarVisibleFor = (sidebar) => {
        let property = this.getProperty(sidebar);
        if (typeof property == 'object') {
            property = this._isTabsVisible(property);
        }
        return property;
    }
    hasAccess = (sidebar) => {
        if (!sidebar) {
            return true
        }
        return this.isSidebarVisibleFor(sidebar);
    }
}

const featurePermissionUIMap = {
    'portal.dashboard': {
        propertyForShowHide: [`${PAIG_LENS}.${DASHBOARD}`]
    },
    'governance.evaluation_config': {
        propertyForShowHide: [`${PAIG_LENS}.${EVALUATION_CONFIG}`]
    },
    'governance.evaluation_reports': {
        propertyForShowHide: [`${PAIG_LENS}.${EVALUATION_REPORTS}`]
    },
    'audits.security': {
        propertyForShowHide: [`${PAIG_LENS}.${SECURITY}`]
    },
    "portal.reports": {
        propertyForShowHide: [`${PAIG_LENS}.${BUILT_IN_REPORTS}`, `${PAIG_LENS}.${SAVED_REPORTS}`]
    },
    'compliance.admin_audits':{
        propertyForShowHide: [`${PAIG_LENS}.${ADMIN_AUDITS}`]
    },
    'portal.docs': {
        propertyForShowHide: [DOCS]
    },
    'governance.ai_applications': {
        propertyForShowHide: [`${PAIG_NAVIGATOR}.${AI_APPLICATIONS}.${AI_APPLICATIONS}`, `${PAIG_NAVIGATOR}.${AI_APPLICATIONS}.${AI_APPLICATIONS_PERMISSIONS}`]
    },
    'governance.vector_db': {
        propertyForShowHide: [`${PAIG_NAVIGATOR}.${VECTOR_DB}.${VECTOR_DB}`, `${PAIG_NAVIGATOR}.${VECTOR_DB}.${VECTOR_DB_PERMISSIONS}`]
    },
    'account.shield_configuration': {
        propertyForShowHide: [`${SETTINGS}.${SHIELD_CONFIGURATION}`]
    },
    'account.user': {
        propertyForShowHide: [`${SETTINGS}.${USERS}.${PORTAL_USERS}`, `${SETTINGS}.${USERS}.${PORTAL_GROUPS}`]
    },
    'account.sensitive_data': {
        propertyForShowHide: [`${PAIG_GUARD}.${SENSITIVE_DATA}`]
    },
    'account.meta_data': {
        propertyForShowHide: [`${PAIG_GUARD}.${META_DATA}`]
    }
}

const uiSidebarTabsUtil = new UISidebarTabsUtil();  

export default uiSidebarTabsUtil;
export {
	SIDEBAR_MENU_ITEMS,
	UI_FEATURE_SIDEBAR_TABS
}
