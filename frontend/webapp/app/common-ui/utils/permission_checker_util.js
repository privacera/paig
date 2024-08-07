import {map, each, includes} from 'lodash';

import {FEATURE_PERMISSIONS, PERMISSIONS} from 'utils/globals';
import UiState from 'data/ui_state';
import {Utils} from 'common-ui/utils/utils';
import {USER_ACCOUNT_PERMISSIONS} from 'common-ui/utils/globals';

class PermissionCheckerUtil {
    rolesWithPermission=[];
    featurePermissionList = [];
    featureDenyListUISidebarAndTabs = [];
    featurePermissionDenyList = new Set();

    rangerEnums={}
    rangerUiState={}
    configProperties={}

    unifiedFeaturePermission=[];
    rangerFeaturePermission=[];
    cryptoFeaturePermission=[];

    constructor() {
        // this.setUp();
    }
    setUnifiedFeaturePermission(permission=[]) {
        this.unifiedFeaturePermission = permission;
    }
    getUnifiedFeaturePermission() {
        return this.unifiedFeaturePermission;
    }
    setRangerFeaturePermission(permission=[]) {
        this.rangerFeaturePermission = permission;
    }
    getRangerFeaturePermission() {
        return this.rangerFeaturePermission;
    }
    setCryptoFeaturePermission(permission=[]) {
        this.cryptoFeaturePermission = permission;
    }
    getCryptoFeaturePermission() {
        return this.cryptoFeaturePermission;
    }
    setRangerEnums(enums={}) {
        this.rangerEnums = enums;
    }
    getRangerEnums() {
        return this.rangerEnums;
    }
    setRangerUiState(uiState={}) {
        this.rangerUiState = uiState;
    }
    getRangerUiState() {
        return this.rangerUiState;
    }
    setConfigProperties(configProperties) {
        this.configProperties = configProperties
    }
    getConfigProperties() {
        return this.configProperties;
    }
    setUp() {
        this.featurePermissionList = this.createFeaturePermissionList({
            ...FEATURE_PERMISSIONS,
            ...this.getUnifiedFeaturePermission(),
            ...this.getRangerFeaturePermission(),
            ...this.getCryptoFeaturePermission()
        });
    }
    createFeaturePermissionList(featurePermissionMap={}) {
        let componentKeys = Object.keys(featurePermissionMap);
        let featurePermissionList = [];
        let permissions = Object.values(PERMISSIONS);

        componentKeys.forEach(componentKey => {
            let component = featurePermissionMap[componentKey] || {};
            let featureKeys = Object.keys(component);
            featureKeys.forEach(feature => {
                let property = component[feature];
                if(property && property.PROPERTY) {
                    permissions.forEach(permission => {
                        featurePermissionList.push(`${property.PROPERTY}.${permission}`)
                    });
                }
            });
        });
        return featurePermissionList;
    }
    clear() {
        this.featurePermissionList = [];
    }
    clearDenyProperties() {
        this.featurePermissionDenyList.clear();
    }
    setRolesWithPermission(rolesWithPermission) {
      this.rolesWithPermission = rolesWithPermission;
    }
    setUserRolesWithPermission(rolesWithPermission=[], rangerUserProfile=null ) {
        this.setRolesWithPermission(rolesWithPermission);
        this.setupRangerModulesWithPermission(rangerUserProfile);
        this.createFeaturePermissionDenyList();
    }
    createFeaturePermissionDenyList() {
        let allDenyList = [];
        let allowList = [];
        this.clearDenyProperties();
        this.featureDenyListUISidebarAndTabs = [];
        this.rolesWithPermission.forEach(roleWithPermission => {
            let {permissions} = roleWithPermission;
            if (permissions) {
                let allow = [];
                let deny = [];
                permissions.forEach(permission => {
                    if (permission.type == "allow") {
                        allow.push(permission.expression);
                    } else if (permission.type == "deny") {
                        deny.push(permission.expression);
                    }
                })
                allDenyList.push(deny);
                allowList.push(allow);
            }
        });

        if (!allDenyList.length && !allowList.length) {
            return;
        }
        let allDenyListLength = allDenyList.length
        this.featurePermissionList.forEach(featurePermission => {
            let denyCount = 0;
            let allowCount = 0;
            allDenyList.forEach((denyList, i) => {
                if (this.checkPermissionMatch(denyList, featurePermission)) {
                    ++denyCount;
                } else if (this.checkPermissionMatch(allowList[i], featurePermission)) {
                    ++allowCount;
                }
            });
            if (allDenyListLength && allDenyListLength == denyCount) {
                //all deny then deny these permission
                this.featurePermissionDenyList.add(featurePermission);
                this.addToUISidebarTabsDenyList(featurePermission, allDenyList, allowList);
            } else {
                //check for any allow, if not match then deny
                // if (!this.checkPermissionMatch(allowList, featurePermission)) {
                if (!allowCount) {
                    this.featurePermissionDenyList.add(featurePermission);
                    this.addToUISidebarTabsDenyList(featurePermission, allDenyList, allowList);
                }
            }
        });
    }
    setupRangerModulesWithPermission(profile) {
        let ranger_modules = (this.getRangerUiState()?.isCloudEnv?.()) ? this.getRangerModulesWithPermission(profile) : this.getRangerModulesWithPermissionForPlatform(profile);
        if (this.rolesWithPermission && this.rolesWithPermission.length > 0) {
            this.rolesWithPermission.forEach(rwp => {
                rwp.permissions = rwp.permissions.concat(ranger_modules);
            });
        } else {
            this.setRolesWithPermission([{
                'permissions': ranger_modules
            }]);
        }
    }
    getRangerModulesWithPermission(profile) {
        let ranger_modules;
        if (profile) {
          let rangerAllowModules = map(profile.userPermList, o => o.moduleName );
          if(profile.groupPermissions && profile.groupPermissions.length){
            const groupPermissions = new Set(map(profile.groupPermissions, o => o.moduleName));
            rangerAllowModules = [...new Set([...rangerAllowModules,...[...groupPermissions]])]
          }
          rangerAllowModules.push('Policy List');
          if(profile.userRoleList[0] == 'ROLE_SYS_ADMIN'){
            rangerAllowModules.push(...['Permission', 'Tag Management']);
          }
          if (this.getConfigProperties()?.isPegServiceActive?.()) {
            rangerAllowModules.push('Scheme Policies');
          }
          rangerAllowModules.push('Service Explorer');
          // if (profile.userRoleList[0] === 'ROLE_SYS_ADMIN' || profile.userRoleList[0] === 'ROLE_ADMIN_AUDITOR') {
            rangerAllowModules.push('Entitlement');
          // }
           ranger_modules = [{ 'expression': 'ranger.*' , type: "allow"}];
          each(this.getRangerEnums().RANGER_MODULE_MAPPING, (val, key) => {
            if(profile.userRoleList[0] == 'ROLE_USER' && (val == 'resource_based_policies' || val == 'tag_based_policies' || val == 'scheme_based_policies')){
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.update' , type: "deny"});
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.delete' , type: "deny"});
            } else if((profile.userRoleList[0] == 'ROLE_KEY_ADMIN' || profile.userRoleList[0] == 'ROLE_USER') && val == 'user_group'){
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.update' , type: "deny"});
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.delete' , type: "deny"});
              // if (val == 'user_group') {
              //   ranger_modules.push({ 'expression': 'ranger.'+ val + '.ranger_roles.read' , type: "deny"});
              // }
            }else if((profile.userRoleList[0] == 'ROLE_ADMIN_AUDITOR' || profile.userRoleList[0] == 'ROLE_USER') && val == 'security_zone'){
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.update' , type: "deny"});
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.delete' , type: "deny"});
            }else if(profile.userRoleList[0] == 'ROLE_USER' && val == 'policy_list'){
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.read' , type: "allow"});
            } if((profile.userRoleList[0] == 'ROLE_KEY_ADMIN' || profile.userRoleList[0] == 'ROLE_USER') && val == 'service_explorer') {
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.*' , type: "deny"});
                // ranger_modules.push({ 'expression': 'ranger.'+ val+ '.delete' , type: "deny"});
                // ranger_modules.push({ 'expression': 'ranger.'+ val+ '.update' , type: "deny"});
            } else if(profile.userRoleList[0] == 'ROLE_ADMIN_AUDITOR'){
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.update' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.delete' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.read' , type: "allow"});
                // if (val == 'user_group') {
                //     ranger_modules.push({ 'expression': 'ranger.' + val + '.ranger_roles.read', type: "deny" });
                // }
            }
            if(!includes(rangerAllowModules, key)){
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.*' , type: "deny"});
            }
          });
        }else{
          ranger_modules =[{ 'expression': 'ranger.*' , type: "deny"}];
        }
        return ranger_modules;
    }
    getRangerModulesWithPermissionForPlatform(profile) {
        let ranger_modules;
        if (profile) {
          let rangerAllowModules = map(profile.userPermList, o => o.moduleName );
          if(profile.groupPermissions && profile.groupPermissions.length){
            const groupPermissions = new Set(map(profile.groupPermissions, o => o.moduleName));
            rangerAllowModules = [...new Set([...rangerAllowModules,...[...groupPermissions]])]
          }
          rangerAllowModules.push('Policy List');
          if(profile.userRoleList[0] == 'ROLE_SYS_ADMIN'){
              rangerAllowModules.push(...['Permission', 'Tag Management']);
            }
            const {user, rangerUser={}} = UiState;
            let portalUserRoleList = user.roleNames.split(',');
            const rangerUserRoleList = rangerUser.userRoleList || [];
            if(portalUserRoleList.includes('ROLE_KEY_ADMIN') || !rangerUserRoleList.includes('ROLE_KEY_ADMIN')) {
                rangerAllowModules.push('Service Explorer');
            }
          if(portalUserRoleList.indexOf('ROLE_SYS_ADMIN') > -1 ||
            portalUserRoleList.indexOf('ROLE_ACCESS_APPROVER') > -1 ||
            portalUserRoleList.indexOf('ROLE_USER') > -1) {
            rangerAllowModules.push('Access Request');
          }
          if (portalUserRoleList.indexOf('ROLE_SYS_ADMIN') > -1 || 
            portalUserRoleList.indexOf('ROLE_ADMIN') > -1 || 
            portalUserRoleList.indexOf('ROLE_USER') > -1 ||
            portalUserRoleList.indexOf('ROLE_ENCRYPTION_ALL') > -1 || 
            portalUserRoleList.indexOf('ROLE_ENCRYPTION_READ') > -1 ||
            portalUserRoleList.indexOf('ROLE_POLICY_AUDITOR') > -1) {
            rangerAllowModules.push('Scheme Policies');
          }
          if(portalUserRoleList.indexOf('ROLE_KEY_ADMIN') > -1 || profile.userRoleList[0].indexOf('ROLE_KEY_ADMIN') > -1) {
            rangerAllowModules.push('Key Manager');
          }
          if(portalUserRoleList.indexOf('ROLE_SYS_ADMIN') > -1 || portalUserRoleList.indexOf('ROLE_ACCESS_APPROVER') > -1) {
            rangerAllowModules.push('Access Grant');
          }
          // if(portalUserRoleList.indexOf('ROLE_SYS_ADMIN') > -1 || portalUserRoleList.indexOf('ROLE_ADMIN_AUDITOR') > -1
          //     || portalUserRoleList.indexOf('ROLE_POLICY_AUDITOR') > -1) {
            rangerAllowModules.push('Entitlement');
          // }
           ranger_modules = [{ 'expression': 'ranger.*' , type: "allow"}];
          each(this.getRangerEnums().RANGER_MODULE_MAPPING, (val, key) => {
            if((profile.userRoleList[0] == 'ROLE_USER' || rangerUserRoleList.includes('ROLE_KEY_ADMIN_AUDITOR'))  && (val == 'resource_based_policies' || val == 'tag_based_policies')){
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.update' , type: "deny"});
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.delete' , type: "deny"});
            }else if((profile.userRoleList[0] == 'ROLE_USER') && val == 'user_group'){
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.update' , type: "deny"});
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.delete' , type: "deny"});
              // if (val == 'user_group') {
              //   ranger_modules.push({ 'expression': 'ranger.'+ val + '.ranger_roles.read' , type: "deny"});
              // }
            }else if((profile.userRoleList[0] == 'ROLE_KEY_ADMIN' || portalUserRoleList.includes('ROLE_KEY_ADMIN')) && val == 'user_group' ) {
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.update' , type: "allow"});
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.delete' , type: "deny"});
                // ranger_modules.push({ 'expression': 'ranger.'+ val + '.ranger_roles.read' , type: "deny"});
            }else if(profile.userRoleList[0] == 'ROLE_KEY_ADMIN_AUDITOR' || rangerUserRoleList.includes('ROLE_KEY_ADMIN_AUDITOR') && val == 'user_group' ) {
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.update' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.delete' , type: "deny"});
                // ranger_modules.push({ 'expression': 'ranger.'+ val + '.ranger_roles.read' , type: "deny"});
            }
            else if((profile.userRoleList[0] == 'ROLE_ADMIN_AUDITOR' || profile.userRoleList[0] == 'ROLE_USER') && val == 'security_zone'){
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.update' , type: "deny"});
              ranger_modules.push({ 'expression': 'ranger.'+ val +'.delete' , type: "deny"});
            }else if(profile.userRoleList[0] == 'ROLE_USER' && val == 'policy_list'){
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.read' , type: "allow"});
            }else if((
                profile.userRoleList[0] == 'ROLE_ADMIN_AUDITOR' ||
                profile.userRoleList[0] == 'ROLE_KEY_ADMIN' ||
                profile.userRoleList[0] == 'ROLE_USER'
            ) && val == 'service_explorer') {
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.delete' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.update' , type: "deny"});
            }else if(profile.userRoleList[0] == 'ROLE_ADMIN_AUDITOR'){
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.update' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.delete' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.read' , type: "allow"});
                // if (val == 'user_group') {
                //     ranger_modules.push({ 'expression': 'ranger.'+ val + '.ranger_roles.read' , type: "deny"});
                // }
            }else if (profile.userRoleList[0] == 'ROLE_USER' && val == 'reports' && portalUserRoleList.includes('ROLE_READ_ONLY')) {
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.update' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.delete' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.export' , type: "deny"});
            } else if (profile.userRoleList[0] == 'ROLE_USER' && val == 'audit') {
                ranger_modules.push({ 'expression': 'ranger.'+ val +'.export' , type: "deny"});
            } else if(profile.userRoleList[0] == 'ROLE_ADMIN_AUDITOR'){
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.update' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.delete' , type: "deny"});
                ranger_modules.push({ 'expression': 'ranger.'+ val+ '.read' , type: "allow"});
            }
            if(!includes(rangerAllowModules, key)){
              ranger_modules.push({ 'expression': 'ranger.'+ val+ '.*' , type: "deny"});
            }
          });
        }else{
          ranger_modules =[{ 'expression': 'ranger.*' , type: "deny"}];
        }
        return ranger_modules;
    }
    readPermission = [PERMISSIONS.META_READ, PERMISSIONS.READ]
    addToUISidebarTabsDenyList(featurePermission, allDenyList, allowList) {
        if (this.getRangerUiState()?.isCloudEnv?.()) {
            if (featurePermission.endsWith(PERMISSIONS.READ)) {
                this.featureDenyListUISidebarAndTabs.push(featurePermission.substr(0, featurePermission.lastIndexOf('.')));
            }
            return;
        }

        if (!featurePermission.endsWith(PERMISSIONS.META_READ) && !featurePermission.endsWith(PERMISSIONS.READ)) {
            return;
        }
        const str = featurePermission.substr(0, featurePermission.lastIndexOf('.'));
        if (this.featureDenyListUISidebarAndTabs.includes(str)) {
            return;
        }
        //if permission deny is for ranger then dont do further check for meta or read check, just deny that permission
        if (str.startsWith('ranger')) {
            this.featureDenyListUISidebarAndTabs.push(str);
            return;
        }
        //check for read if permission is metaread or vice versa
        let checkForPermissionName = this.readPermission[+!this.readPermission.indexOf(featurePermission.slice(featurePermission.lastIndexOf('.') + 1))];
        checkForPermissionName = featurePermission.slice(0, featurePermission.lastIndexOf('.') + 1) + checkForPermissionName;

        let denyCount = 0;
        allDenyList.forEach((denyList, i) => {
            if (this.checkPermissionMatch(denyList, checkForPermissionName)) {
                ++denyCount;
            } else if (!this.checkPermissionMatch(allowList[i], checkForPermissionName)) {
                ++denyCount;
            }
        });
        // if read and metaread both permission is denied then denied permission
        if (allDenyList.length == denyCount) {
            this.featureDenyListUISidebarAndTabs.push(str);
        }
    }
    checkPermissionMatch = (list, featurePermission) => {
        return list.some(permission => {
            return Utils.wildcardMatch(permission, featurePermission)
        })
    }
    getUISidebarAndTabsDenyList() {
        return this.featureDenyListUISidebarAndTabs;
    }
    getPermissions(property) {
        let permission = {
            metaread: permissionCheckerUtil.hasMetaReadPermission(property),
            read: permissionCheckerUtil.hasReadPermission(property),
            update: permissionCheckerUtil.hasUpdatePermission(property),
            delete: permissionCheckerUtil.hasDeletePermission(property),
            export: permissionCheckerUtil.hasExportPermission(property)
        };
        return permission;
    }
    hasPermissions(property, permission) {
        if (this.getRangerUiState()?.isCloudEnv?.()) {
            //checking deny list if property available then return false else true
            return this.featurePermissionDenyList.size > 0 && !this.featurePermissionDenyList.has(`${property}.${permission}`);
        }
        return !this.featurePermissionDenyList.has(`${property}.${permission}`);
    }
    hasMetaReadPermission(property) {
        return this.hasPermissions(property, PERMISSIONS.META_READ);
    }
    hasReadPermission(property) {
        return this.hasPermissions(property, PERMISSIONS.READ);
    }
    hasUpdatePermission(property) {
        return this.hasPermissions(property, PERMISSIONS.UPDATE);
    }
    hasDeletePermission(property) {
        return this.hasPermissions(property, PERMISSIONS.DELETE);
    }
    hasExportPermission(property) {
        return this.hasPermissions(property, PERMISSIONS.EXPORT);
    }
    checkHasMetaReadPermission(permission={}) {
        return permission.metaread;
    }
    checkHasReadPermission(permission={}) {
        return permission.read;
    }
    checkHasUpdatePermission(permission={}) {
        return permission.update;
    }
    checkHasExportPermission(permission={}) {
        return permission.export;
    }
    checkHasDeletePermission(permission={}) {
        return permission.delete;
    }
    hasReadOrUpdatePermission(permission={}) {
        return permission.read || permission.update;
    }
    hasUpdateOrDeletePermission(permission={}) {
        return permission.update || permission.delete;
    }
    getPermissionForUserAccount = (permission, accountId, userAccountPermissions) => {
        if (!permission || !accountId || !userAccountPermissions) {
            return permission;
        }
        let newPermission = {...permission};
        if (userAccountPermissions.get(accountId) !== USER_ACCOUNT_PERMISSIONS.READ_WRITE.NAME) {
            newPermission.update = false;
            newPermission.delete = false;
        }
        return newPermission;
    }
}

const permissionCheckerUtil = new PermissionCheckerUtil();
export {
    permissionCheckerUtil
}
