import { observable, action, computed} from 'mobx';

import f from 'common-ui/utils/f';
import {permissionCheckerUtil} from 'common-ui/utils/permission_checker_util';
import UISidebarTabsUtil from 'utils/ui_sidebar_tabs_util';
import stores from 'data/stores/all_stores';

class UiState {

	@observable sidebarOpen = true;
	@observable user = null;
	@observable refreshProps = false;
	@observable refreshMenu = false;
	@observable menuToggle = {
        applications: false,
        audits: false,
        account: false,
        compliance: false,
        reports: false
	}

    uiStateStorage = {};

	routes = null;

	getRoutes() {
        return this.routes;
    }
    setRoutes(routes) {
        this.routes = routes;
    }

    @action toggleSideBar() {
      this.sidebarOpen = !this.sidebarOpen;
      document.body.className = this.sidebarOpen ? 'pace-done body-small' : 'pace-done body-small mini-navbar';
    }

    isSideBarOpen() {
       return this.sidebarOpen; 
    }

    saveState(name, data) {
        this.uiStateStorage[name] = data;
    }

    getStateData(name) {
        let data = this.uiStateStorage[name];
        return data && typeof data == "string" ? JSON.parse(data) : data;
    }

    getUserPermission() {
        return JSON.parse(JSON.stringify(this.user.rolePermissions));
    }

    getUserEmail() {
        return this.user.email;
    }

    getTenantId() {
        // TODO change this to select tenant when there are multiple tenants
        return this.user.tenants[0].tenantId;
    }

    getHeaderWithTenantIdAndEmail() {
        return {
            headers : {
                tenantId: this.getTenantId(),
                email: this.getUserEmail()
            }
        }
    }

    getHeaderWithTenantId() {
        return {
            headers: {
                tenantId: this.getTenantId()
            }
        }
    }

    setLoggedInUser(user) {
    	this.user = user;
    }
    getLoggedInUser() {
        return this.user;
    }
    getUnknownRoleWithDenyPermission() {
        return [{
            role: 'UNKNOWN',
            permissions: [{
                expression: '*',
                type: 'deny'
            }]
        }]
    }
    getUserRoleWithPermissionFromTenants(tenants=[]) {
        //TODO change this to select tenant when there are multiple tenants
        if (!tenants.length) {
            return this.getUnknownRoleWithDenyPermission();
        }
        let tenant = tenants[0];
        if (tenant && (!tenant.roles || !tenant.roles.length)) {
            return this.getUnknownRoleWithDenyPermission();
        }

        //TODO change permissions
        return tenant.roles.map(role => {
            if (role === 'USER') {
                return {
                    role,
                    permissions: [{
                        expression: 'portal.dashboard',
                        type: 'allow'
                    }, {
                       expression: 'portal.docs',
                       type: 'allow'
                    }]
                }
            }
            return {
                role,
                permissions: [{
                    expression: '*',
                    type: 'allow'
                }]
            }
        })
    }

    async fetch() {
        this.userPromiseObj = stores.userStore.getLoggedInUser();
        let user = await this.userPromiseObj;
        user.rolePermissions = this.getUserRoleWithPermissionFromTenants(user.tenants);

        try {
            const properties = await UISidebarTabsUtil.fetchProperties();

            this.setLoggedInUser(user);

            permissionCheckerUtil.setUserRolesWithPermission(this.getUserPermission());

            UISidebarTabsUtil._createDefaultProperties();
            await UISidebarTabsUtil.evalPropertiesForAccessControl();

            return user;
        } catch(e) {
            console.log(e);
        }
    }

    async refreshProperties() {
        try {
            /* remove this and use fetch method */
            this.userPromiseObj = stores.userStore.getLoggedInUser();
            const user = await this.userPromiseObj;

            const properties = await UISidebarTabsUtil.fetchProperties();

            this.setLoggedInUser(user);

            permissionCheckerUtil.setUserRolesWithPermission(this.getUserPermission());

            UISidebarTabsUtil._createDefaultProperties();
            await UISidebarTabsUtil.evalPropertiesForAccessControl();
        } catch(e) {
            console.error("Failed to refresh properties", e);
            return null;
        }
        return true;
    }

    getSideBarList() {
        return UISidebarTabsUtil.getSidebarList();
    }

    filterTabs(view, lists) {
        //to show hide ui tabs
        return UISidebarTabsUtil.filterTabsList(view, lists);
    }

    setRefreshProps(refresh) {
        this.refreshProps = refresh;
    }

	logout() {
        console.log('Logout called')
        location = '../logout';
    }
}

let singleton = new UiState();
export default singleton;