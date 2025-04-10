import commonUtils from "../common/common_utils";
import applicationUtils from "./ai_applications_utils";

describe("Test AI Application page", () => {

  before(() => {
    cy.login();
  });

  beforeEach(() => {
    cy.visit('/#/dashboard');
    cy.visit('/#/ai_applications')
  });

  after(() => {
    cy.clearSession();
  });

  const appName = generateUniqueName();
  const appDesc = `Description for ${appName}`;
  const apiKeyName = `${appName}-API-Key`;
  const apiKeyDesc = `Description for ${apiKeyName}`;
  const apiKeyNameExpiry = `${appName}-Expiry-API-Key`;
  const apiKeyDescExpiry = `Description for ${apiKeyNameExpiry}`;

  function generateUniqueName() {
    const prefix = "TestApp";
    const timestamp = Date.now();
    return `${prefix}_${timestamp}`;
  }

    function verifyListing() {
      cy.request("governance-service/api/ai/application?size=15&sort=createTime,desc").then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property("content");

        if(response.body.content.length > 0){
          let applications = response.body.content;
          let defaultAppIndex = applications.findIndex(app => app.default);
          if (defaultAppIndex > -1) {
              let defaultApp = applications.splice(defaultAppIndex, 1)[0];
              applications.unshift(defaultApp);
          }
          applications.forEach((app,i) => {
            if (i !== 0 || !app.default) {
              cy.get('[data-testid="app-card"]').eq(i).should('contain.text', app.name);

              const truncatedDescription = app.description.length > 470 ? `${app.description.slice(0, 470)}...` : app.description;
              cy.get('[data-testid="app-card"]').eq(i).find('[data-testid="app-desc"]').should('contain.text', truncatedDescription);
            }
          });

        }
        // else{
        //     cy.get('[data-testid="table-noData"]').should('be.visible');
        // }
      });
    }

    function createApplication(appName, appDesc, status, vectorDBName) {
      cy.get('button[data-test="add-btn"]').filter(':contains("CREATE APPLICATION")').click();
      cy.url().should("include", "/ai_application/create");
      cy.get('[data-testid="app-name"]').type(appName);
      cy.get('[data-testid="app-desc"]').type(appDesc);
      if(status === "off") {
        cy.get('[data-testid="app-status"]').click(); // turn off status use .uncheck()
        cy.get('[data-testid="app-status"]').should('not.be.checked');  // verify status is off
      }
      if (vectorDBName) {
        cy.get('input[placeholder="Select Vector DB"]').click();
        cy.get('input[placeholder="Select Vector DB"]').type(vectorDBName);
        cy.get('[data-testid="select-option-item"]').contains(vectorDBName).click();
      }
      cy.get('[data-testid="create-app-btn"]').click();
      cy.get('#notistack-snackbar', { timeout: 10000 }).should('contain.text', 'The AI Application created successfully');
      cy.get('[data-testid="snackbar-close-btn"]').click();
      cy.get('#notistack-snackbar').should('not.be.visible');
      cy.get('[data-test="back-btn"]').click();
    }

    function createVectorDB(name, desc, type = "", status = "") {
      cy.get('[data-test="add-btn"]').should("have.text", "CREATE VECTOR DB").click();
      cy.url().should("include", "/vector_db/create");
      if (type !== "") {
        selectType(type);        
      }
      cy.get('[data-testid="name"] [data-testid="input-field"]').type(name);
      cy.get('[data-testid="desc"] [data-testid="input-field"]').type(desc);  
      if(status === "off") {
        cy.get('[data-testid="toggle-switch"]').click();
        cy.get('[data-testid="toggle-switch"]').should('not.be.checked');
      } 
      cy.get('[data-testid="create-app-btn"]').click();
      cy.get('#notistack-snackbar', { timeout: 10000 }).should('contain.text', 'The Vector DB created successfully');
      cy.get('[data-testid="snackbar-close-btn"]').click();
      cy.get('#notistack-snackbar').should('not.be.visible');
      cy.get('[data-test="back-btn"]').click();
    }

    function verifyAccessOnHover(dataTestId, titleText, uniqueData) {
      // Trigger hover on the badge
      cy.get(`[data-testid=${dataTestId}]`).trigger('mouseover'); // Trigger hover
  
      // Verify the tooltip title
      cy.get(`[data-testid="tooltip-title"]`).should('contain.text', titleText);
  
      // Verify the badge content count
      if (uniqueData.length > 0) {
          cy.get(`[data-testid=${dataTestId}] .MuiBadge-badge`).should('contain.text', uniqueData.length);
  
          // Verify each tag chip content
          cy.get(`[data-testid="tagchip"]`).each(($chip, index) => {
              cy.wrap($chip).should('contain.text', uniqueData[index].trim());
          });
      }
  
      // Dismiss the hover
      cy.get('body').trigger('mouseout');
    }

    function editApplication(appName, appDesc, status) {
      cy.get('[data-test="edit"]').should('be.visible').click();

      if(appName !== "") {
        cy.get('[data-testid="app-name"] [data-testid="input-field"]').clear().type(appName);
      }

      if(appDesc !== "") {
        cy.get('[data-testid="app-desc"] [data-testid="input-field"]').clear().type(appDesc);
      }

      if(status === "off") {
        cy.get('[data-testid="app-status"]').click(); // turn off status use .uncheck()
        cy.get('[data-testid="app-status"]').should('not.be.checked');  // verify status is off
      }

      cy.get('[data-testid="edit-save-btn"]').click();
      cy.get('#notistack-snackbar', { timeout: 10000 }).should('contain.text', 'The AI Application updated successfully');
      cy.get('[data-testid="snackbar-close-btn"]').click();
      cy.get('#notistack-snackbar').should('not.be.visible');
      if(appName !== "") {
        cy.get('[data-testid="app-name-text"]').should('contain.text', appName);
      }
      if(appDesc !== "") {
        cy.get('[data-testid="app-desc-text"]').should('contain.text', appDesc);
      }
      if(status === "off") {
        //check status is unchecked
        cy.get('[data-testid="toggle-switch"] ').should('not.be.checked');
      }
    }

    function verifyContentRestriction(dataTestId, count){
      cy.get(`[data-testid="sim-icon"]`).should(`be.visible`);
      if(count > 0){
        cy.get(`[data-testid=${dataTestId}] .MuiBadge-badge`).should('contain.text', count);
      }else{
        cy.get(`[data-testid=${dataTestId}] .MuiBadge-badge`).should('not.be.visible');
      }
    }

    function verifyAppNameAndDesc(appName, appDesc){
      cy.contains(`[data-testid="app-card"]`, appName).should('be.visible');
      cy.contains(`[data-testid="app-card"]`, appDesc).should('be.visible');
    }

    function setupAndVerifyPermissionTab(appName) {
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');
      // Iterate over each app card and click on the one with the matching app name
      cy.get('[data-testid="app-card"]').each(($card) => {
        cy.wrap($card).within(() => {
          cy.get('[data-testid="app-name"]').then(($appName) => {
            if ($appName.text().trim() === appName) {
              cy.wrap($card).as('selectedCard');
            }
          });
        });
      });   
      cy.get('@selectedCard').click();     
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');
      cy.get('[data-testid="application-permissions-tab"]').click();    
      // Assert that the AI Application Access card exists
      cy.get('[data-testid="ai-app-access-card"]').should('exist');
    }

    function verifyAccessOnHoverCount(dataTestId, popoverTitle, count) {
      // Trigger hover on the badge
      cy.get(`[data-testid="permission-card"] [data-testid=${dataTestId}]`).trigger('mouseover'); // Trigger hover
  
      // Verify the tooltip title
      cy.get(`[data-testid="tooltip-title"]`).should('contain.text', popoverTitle);

      // Verify the badge content count
      if (count > 0) {
        cy.get(`[data-testid=${dataTestId}] .MuiBadge-badge`).should('contain.text', count);
      }

      // Dismiss the hover
      cy.get('body').trigger('mouseout');
    }

    function saveChangesAndVerifySuccessMessage() {
      cy.get('[data-testid="ai-app-access-card"]').find('[data-testid="edit-save-btn"]').click();
      cy.get('#notistack-snackbar').should('contain.text', 'Restriction updated successfully');
      cy.get('[data-testid="snackbar-close-btn"]').click();
      cy.get('#notistack-snackbar').should('not.be.visible');
    }
    
    function deleteApp(appName) {
      cy.contains(`[data-testid="app-card"]`, appName).should('be.visible').within(() => {
        cy.get('[data-test="delete"]').click();
      });
      cy.get('[data-testid="dialog-content"]').contains( `Are you sure you want to delete ${appName} application?`);
      cy.get('[data-test="confirm-yes-btn"]').click();
      cy.get('#notistack-snackbar').should('contain.text', `The AI Application ${appName} deleted successfully`);
      cy.get('[data-testid="snackbar-close-btn"]').click();
    }

    function handleAction(keyName, actionType) {
      cy.contains('[data-testid="table-row"]', keyName, { matchCase: true }).within(() => {
        cy.get(`[data-testid="${actionType}-api-key"]`).click();
      });
      cy.get('[data-testid="custom-dialog"]').should('be.visible');
      cy.get('[data-testid="confirm-dialog-title"]').should('contain.text', `${actionType === 'delete' ? 'Delete' : 'Revoke'} API Key`);
      cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to ${actionType} ${keyName} API Key?`);
      if (actionType === 'revoke') {
        cy.get('[data-testid="dialog-content"]').should('contain.text', 'This action cannot be reversed.');
      }
      if (actionType === 'revoke') {
        cy.intercept('PUT', `/account-service/api/apikey/disableKey/*`).as('revokeApiKey');
      } else if (actionType === 'delete') {
        cy.intercept('DELETE', `/account-service/api/apikey/*`).as('deleteApiKey');
      }
      cy.get('[data-test="confirm-yes-btn"]').click();
      if (actionType === 'delete') {
        cy.wait('@deleteApiKey').then((interception) => {
          expect(interception.response.statusCode).to.eq(200);
          cy.get('#notistack-snackbar').should('contain.text', 'API Key Deleted Successfully');
          cy.get('[data-testid="snackbar-close-btn"]').click();
          cy.get('#notistack-snackbar').should('not.be.visible');
          cy.get('[data-testid="custom-dialog"]').should("not.exist");
        });
      } else if (actionType === 'revoke') {
        cy.wait('@revokeApiKey').then((interception) => {
          expect(interception.response.statusCode).to.eq(200);
          cy.get('#notistack-snackbar').should('contain.text', 'API Key Revoked Successfully');
          cy.get('[data-testid="snackbar-close-btn"]').click();
          cy.get('#notistack-snackbar').should('not.be.visible');
          cy.get('[data-testid="custom-dialog"]').should("not.exist");
        });
      }
    }

    it("should create application, cancel creation, verify on update page and listing, edit, and delete", () => {
      const appName = generateUniqueName();
      const appDesc = `Description for ${appName}`;
      const updatedAppName = `${appName}_edited`;
      const updatedAppDesc = `${appDesc} edited`;
      
      // Cancel Application create
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');
      cy.get('button[data-test="add-btn"]').filter(':contains("CREATE APPLICATION")').click();
      cy.url().should("include", "/ai_application/create");
      cy.get('[data-testid="cancel-btn"]').click();
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');

      cy.wait(5000);
      // Validate Required Fields in Application create
      cy.get('button[data-test="add-btn"]').filter(':contains("CREATE APPLICATION")').click();
      cy.url().should("include", "/ai_application/create");
      cy.wait(5000);
      cy.get('[data-testid="create-app-btn"]').click();
      cy.get('.Mui-error').should('contain.text', 'Required');
      cy.get('[data-testid="app-name"]').type(appName);
      cy.get('.Mui-error').should('not.exist');
      cy.get('[data-testid="app-name"] input[data-testid="input-field"]').clear();
      cy.get('.Mui-error').should('contain.text', 'Required');
      cy.get('[data-testid="cancel-btn"]').click();

      // Create Application
      createApplication(appName, appDesc, "on");

      // Verify Application
      verifyAppNameAndDesc(appName, appDesc);

      // Edit Application  
      cy.contains(`[data-testid="app-card"]`, appName).click();
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');  
      editApplication(updatedAppName, updatedAppDesc, "off");
      
      // Verify Edited Application
      cy.get('[data-test="back-btn"]').click();
      verifyAppNameAndDesc(updatedAppName, updatedAppDesc);

      // Delete Application
      deleteApp(updatedAppName);
    });

    it("should create application, verify sensitive data, and verify permission card data and also navigate to permission tab through manage button", () => {
      const appName = generateUniqueName();
      const appDesc = `Description for ${appName}`;

      // Intercept API calls
      cy.intercept('/governance-service/api/ai/application?size=15&sort=createTime,desc').as('getAppList');
      cy.intercept('/governance-service/api/ai/application/*/policy?size=1&status=1').as('getAllPolicies');

      // Create Application
      createApplication(appName, appDesc, "on");
      cy.get('[data-testid="header-refresh-btn"]').click();
      // Wait for application list and get the first application
      cy.wait('@getAppList').then((interception) => {
        const response = interception.response;
        expect(response.statusCode).to.equal(200);
        expect(response.body).to.have.property("content");

        if (response.body.content.length > 0) {

          cy.contains(`[data-testid="app-card"]`, appName).click();

          // Wait for all policies API call
          cy.wait('@getAllPolicies').then((interception) => {
            const response = interception.response;
            const contentRestriction = response.body.totalElements;

            expect(response.statusCode).to.equal(200);
            expect(response.body).to.have.property("content");
            const {content} = response.body;

            const permissionRows = applicationUtils.setPermissionRows(content);
            const allowAccess = applicationUtils.processPermissionRows(permissionRows, 'allow');
            const deniedAccess = applicationUtils.processPermissionRows(permissionRows, 'deny');

            cy.get('[data-testid="permission-card"]').should('contain.text', 'Application Access Control Summary');
            cy.get('[data-testid="permission-card"]  [data-testid="allow-access-row"]').should('contain.text', 'Granted Access Count');
            cy.get('[data-testid="permission-card"]  [data-testid="deny-access-row"]').should('contain.text', 'Access Denials Enforced');
            cy.get('[data-testid="permission-card"]  [data-testid="cont-rest-row"]').should('contain.text', 'Active Content Restrictions');

            verifyAccessOnHover("allow-access-users", "Users", allowAccess.users);
            verifyAccessOnHover("allow-access-groups", "Groups", allowAccess.groups);
            verifyAccessOnHover("allow-access-roles", "Roles", allowAccess.roles);
            verifyContentRestriction("cont-rest-row", contentRestriction);
            verifyAccessOnHover("deny-access-users", "Users", deniedAccess.users);
            verifyAccessOnHover("deny-access-groups", "Groups", deniedAccess.groups);
            verifyAccessOnHover("deny-access-roles", "Roles", deniedAccess.roles);
          });

          // Click on the "Manage" button to navigate to the permission tab
          cy.get('[data-testid="permission-card"] [data-testid="manage-permission-btn"]').click();
          // Check for the additional card and its content
          cy.get('[data-testid="ai-app-access-card"]').should('exist');
          cy.get('[data-testid="ai-app-access-card"]').contains('AI Application Access');
          cy.get('[data-testid="ai-app-access-card"]').contains('Allow access to AI Application for Users/Groups');
          cy.get('[data-testid="ai-app-access-card"]').contains('Deny access to AI Application for Users/Groups');
        }
      });
      // Delete app
      cy.get('[data-test="back-btn"]').click();
      deleteApp(appName);
    });

    it("should click refresh and verify AI Applications listing", () => {
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');
      cy.get('[data-testid="header-refresh-btn"]').click();
      verifyListing();
    });

    it("should successfully create VectorDB and associate it with an application", () => {
      const vectorDBName = generateUniqueName();
      const vectorDBDesc = `Description for ${vectorDBName}`;
      cy.get('[data-testid="vector_db_submenu"]').should('exist').should('be.visible').click();
      cy.get('[data-testid="page-title"]').should('have.text', 'Vector DB');
      createVectorDB(vectorDBName, vectorDBDesc, "", "on");
      cy.contains(`[data-testid="card"]`, vectorDBName).should('be.visible');
      cy.contains(`[data-testid="card"]`, vectorDBDesc).should('be.visible');
  
      // Navigate to the Applications page
      cy.visit('/#/ai_applications');
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');
      
      // Create a new application and associate the vector database
      const appName = generateUniqueName("TestApp");
      const appDesc = `Description for ${appName}`;
      createApplication(appName, appDesc, "on", vectorDBName);
      cy.contains(`[data-testid="app-card"]`, appName).click();
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');

      // Assert that VectorDB permissions are displayed correctly
      cy.get('[data-testid="vector-db-permission-card"]').should('exist');
      cy.get('[data-testid="cont-rest-row"]').eq(0).should('exist');
      cy.get('[data-testid="cont-rest-row"]').eq(1).should('exist');
      
      // Navigate back to VectorDB details page
      cy.contains('[data-testid="vector-db-permission-card"] h2', vectorDBName).should('exist').click();
      cy.get('[data-testid="page-title"]').should('contain.text', 'VectorDB Details');

      // Navigate back to the Applications page and delete app
      cy.visit('/#/ai_applications');
      deleteApp(appName);
    });

    it("should navigate to permissions page through an application and verify AI Application Access card content and Content Restriction content", () => {
      // Intercept API call to fetch AI application details
      cy.intercept('GET', '/governance-service/api/ai/application*').as('getAIApplication');
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');
      // Click the refresh button to fetch AI application details
      cy.get('[data-testid="header-refresh-btn"]').click();

      // Wait for the API call to complete
      cy.wait('@getAIApplication').then((interception) => {
        // Ensure that application content exists
        if (interception.response.body.content.length === 0) {
          cy.log('No AI applications found. Exiting test.');
          return;
        }
        // Filter out default application if present
        const applications = interception.response.body.content;
        const nonDefaultApp = applications.find(app => !app.default);
        let appName;
        let appDesc;
        let createdApp = false;

        // If no non-default application exists, create a new one
        if (!nonDefaultApp) {
          cy.log('No non-default AI applications found. Creating a new application.');
          appName = generateUniqueName();
          appDesc = `Description for ${appName}`;
          // Create a new application
          createApplication(appName, appDesc, "on");
          verifyAppNameAndDesc(appName, appDesc);
          createdApp = true;
        } else {
          appName = nonDefaultApp.name;
          appDesc = nonDefaultApp.description;
        }

        // Navigate to the application details
        cy.get('[data-testid="app-card"]').contains(appName).click();
        cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');
        cy.get('[data-testid="application-permissions-tab"]').click();

        // Assert that the AI Application Access card exists
        cy.get('[data-testid="ai-app-access-card"]').should('exist');
        
        // Assert the content within the AI Application Access card
        cy.get('[data-testid="ai-app-access-card"]').within(() => {
          cy.contains('p', 'AI Application Access').should('exist');
          cy.contains('[data-test="form"]', 'Allow access to AI Application for Users/Groups').should('exist');
          cy.contains('[data-test="form"]', 'Deny access to AI Application for Users/Groups').should('exist');
          cy.get('[data-test="edit"]').should('exist');
        });

        // Assert the content within the Content Restriction card
        cy.get('[data-test="searchBox"]').should('exist');
        cy.get('[data-testid="input-search-box"]').should('exist');
        cy.get('[data-testid="sensitive-data-filter"]').should('be.visible');
        cy.get('[data-testid="add-restriction-button"]').should('be.visible');

        const headers = ['Description', 'Users / Groups', 'Content Having Tags', 'Restrictions', 'Status', 'Actions'];
        headers.forEach((header, index) => {
          cy.get(`[data-testid="thead"] :nth-child(${index + 1})`).should('contain.text', header);
        });

        // Delete the created application if it was created during this test
        if (createdApp) {
          cy.get('[data-test="back-btn"]').click();
          deleteApp(appName);
        }
      });
    });

    it("should edit the AI Application allow and deny access card and verify permission summary", () => {
      // Create a new application and associate the vector database
      const appName = generateUniqueName("TestApp");
      const appDesc = `Description for ${appName}`;
      createApplication(appName, appDesc, "on");        
      setupAndVerifyPermissionTab(appName);
      // Edit the AI Application Access card
      cy.get('[data-testid="ai-app-access-card"] [data-test="edit"]').click();
  
      // Remove the Everyone chip
      cy.get('[data-testid="access-input"]').eq(1).click();
      cy.contains('[data-testid="select-option-item"]', 'Everyone').click();
      cy.get('[data-testid="access-input"]').eq(1).click();
      saveChangesAndVerifySuccessMessage();
      // Come back to tab 1
      cy.get('[data-testid="application-overview-tab"]').click();
      // Verify the content restriction summary
      //Granted Access Count
      verifyAccessOnHoverCount("allow-access-users", "Users", 0);
      verifyAccessOnHoverCount("allow-access-groups", "Groups", 1);
      verifyAccessOnHoverCount("allow-access-roles", "Roles", 0);
      //Access Denials Enforced
      verifyAccessOnHoverCount("deny-access-users", "Users", 0);
      verifyAccessOnHoverCount("deny-access-groups", "Groups", 1);
      verifyAccessOnHoverCount("deny-access-roles", "Roles", 0);
      cy.get('[data-test="back-btn"]').click();

      setupAndVerifyPermissionTab(appName);
      // Edit the AI Application Access card
      cy.get('[data-testid="ai-app-access-card"] [data-test="edit"]').click();
  
      // Remove the Everyone chip
      cy.get('[data-testid="access-input"]').eq(0).contains('Everyone');
      cy.get('[data-testid="access-input"]').eq(0)
        .within(() => {
          cy.get('.MuiChip-deleteIcon').click(); // Click on the delete icon to remove the chip
        });
      cy.get('[data-testid="access-input"]').eq(0).should('not.contain', 'Everyone');
      cy.get('[data-testid="access-input"]').eq(0).click();
      saveChangesAndVerifySuccessMessage();
      // Come back to tab 1
      cy.get('[data-testid="application-overview-tab"]').click();
      // Verify the content restriction summary
      //Granted Access Count
      verifyAccessOnHoverCount("allow-access-users", "Users", 0);
      verifyAccessOnHoverCount("allow-access-groups", "Groups", 0);
      verifyAccessOnHoverCount("allow-access-roles", "Roles", 0);
      //Access Denials Enforced
      verifyAccessOnHoverCount("deny-access-users", "Users", 0);
      verifyAccessOnHoverCount("deny-access-groups", "Groups", 0);
      verifyAccessOnHoverCount("deny-access-roles", "Roles", 0);
      cy.get('[data-test="back-btn"]').click();
      // Delete app
      deleteApp(appName);
    });

    it("should be able to search description and filter by sensitive data in AI Application Content Restriction content", () => {
      const appName = generateUniqueName();
      const appDesc = `Description for ${appName}`;
      createApplication(appName, appDesc, "on");

      // Intercept API call to fetch AI application details
      cy.intercept('GET', '/governance-service/api/ai/application*').as('getAIApplication');
      // Click the refresh button to fetch AI application details
      cy.get('[data-testid="header-refresh-btn"]').click();

      // Wait for the API call to complete
      cy.wait('@getAIApplication').then((interception) => {
        // Ensure that application content exists
        if (interception.response.body.content.length === 0) {
          cy.log('No AI applications found. Exiting test.');
          return;
        }
        // Filter out default application if present
        const applications = interception.response.body.content;
        const newApp = applications.find(app => app.name === appName);

        if (!newApp) {
          cy.log('New application not found in the list. Exiting test.');
          return;
        }

        const appId = newApp.id;

        cy.get('[data-testid="app-card"]').contains(appName).click();
        cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');
        cy.get('[data-testid="application-permissions-tab"]').click();

        // Intercept API call to fetch AI application policies without search parameters
        cy.intercept('GET', `/governance-service/api/ai/application/${appId}/policy?size=999&sort=createTime,desc`).as("searchAIApplication");
        
        // Intercept API call to fetch AI application policies with search parameters
        let searchContentRestriction = 'nonexisting' + commonUtils.generateRandomWord(5);
        cy.intercept('GET', `/governance-service/api/ai/application/${appId}/policy?size=999&sort=createTime,desc&description=${searchContentRestriction}`).as("searchAIApplicationWithParams");
    
        // Search for Content Restriction without parameters
        cy.get('[data-testid="ai-app-content-restriction-search"]').clear().type('{enter}');

        // Wait for the search to complete
        cy.wait('@searchAIApplication').then(interception => {
          const {content} = interception.response.body;
          expect(content.length).to.gt(0);
          cy.get('[data-testid="tbody-with-data"]').children().should('have.length', content.length);
          
          // Get a description from the existing content
          const existingDescription = content[0].description;

          // Intercept API call to fetch AI application policies with the existing description
          cy.intercept('GET', `/governance-service/api/ai/application/${appId}/policy?size=999&sort=createTime,desc&description=*`).as("searchAIApplicationWithExistingDescription");

          // Search for Content Restriction with the existing description
          cy.get('[data-testid="ai-app-content-restriction-search"]').type(existingDescription).type('{enter}');

          // Wait for the search to complete
          cy.wait('@searchAIApplicationWithExistingDescription').then(interception => {
            const {content} = interception.response.body;
            expect(content.length).to.gt(0);
            // Check if the table contains the searched description
            cy.get('[data-testid="tbody-with-data"]').children().each(($row) => {
              cy.wrap($row).should('contain.text', existingDescription);
            });                
          });
        });

        // Clear the search and search for Content Restriction with the generated search term
        cy.get('[data-testid="ai-app-content-restriction-search"]').within(() => {
          cy.get('[data-testid="input-search-box"]').clear().type(searchContentRestriction).type('{enter}');
        });

        // Wait for the searchAIApplicationWithParams alias
        cy.wait('@searchAIApplicationWithParams').then(interception => {
          const {content} = interception.response.body;
          expect(content.length).to.eq(0);
          // Verify the message for no matching records
          cy.get('[data-testid="table-noData"]').should('be.visible');
        });

        // Clear the search
        cy.get('[data-testid="ai-app-content-restriction-search"]').within(() => {
          cy.get('[data-testid="input-search-box"]').clear().type('{enter}');
        });

        // Wait for the searchAIApplication alias
        cy.wait('@searchAIApplication').then(interception => {
          const {content} = interception.response.body;
          expect(content.length).to.gt(0);
          cy.get('[data-testid="tbody-with-data"]').children().should('have.length', content.length);
        });
      });

      // Intercept API call to fetch sensitive data options
      cy.intercept('GET', '/account-service/api/tags?size=100').as('getSensitiveDataOptions');

      cy.get('[data-testid="application-overview-tab"]').click();  
      cy.get('[data-testid="application-permissions-tab"]').click();  
      cy.get('[data-testid="sensitive-data-filter"]').click();

      // Wait for the API call to complete and retrieve sensitive data options
      cy.wait('@getSensitiveDataOptions').then(interception => {
        const sensitiveDataOptions = interception.response.body.content;

        // Select a sensitive data option from the dropdown
        const randomIndex = Math.floor(Math.random() * sensitiveDataOptions.length);
        const selectedSensitiveDataValue = sensitiveDataOptions[randomIndex].name;
        cy.get('[data-testid="sensitive-data-filter"]').type(selectedSensitiveDataValue);

        // Intercept API call to fetch AI application policies with filter applied
        cy.intercept(
          'GET', `/governance-service/api/ai/application/*/policy?size=999&sort=createTime,desc&tag=${selectedSensitiveDataValue}`

        ).as("filterAIApplicationBySensitiveData");

        cy.get('[data-testid="select-option-item"]').contains(selectedSensitiveDataValue).click();

        // Verify that the correct sensitive data filter is applied
        cy.get('[data-testid="sensitive-data-filter"] input').should('have.value', selectedSensitiveDataValue);

        // Wait for the API call to complete and retrieve filtered AI application policies
        cy.wait('@filterAIApplicationBySensitiveData').then(interception => {
          const { content } = interception.response.body;
          if (content.length === 0) {
            cy.get('[data-testid="table-noData"]').should('be.visible');
          } else {
            cy.get('[data-testid="tbody-with-data"]').children().should('have.length', content.length);
          }
        });
      });

      // Delete app
      cy.get('[data-test="back-btn"]').click();
      deleteApp(appName);
    });

    it("should add, update, and delete a restriction to AI Application Content Restriction content", () => {
      const appName = generateUniqueName();
      const appDesc = `Description for ${appName}`;
      createApplication(appName, appDesc, "on");
      setupAndVerifyPermissionTab(appName);

      // Intercept API calls to fetch users, groups, and sensitive data options
      cy.intercept('GET', '/account-service/api/users*').as('getUsers');
      cy.intercept('GET', '/account-service/api/groups*').as('getGroups');
      cy.intercept('GET', '/account-service/api/tags*').as('getSensitiveData');
      
      cy.intercept('GET', `/governance-service/api/ai/application*`).as('getAIApplication');
      cy.intercept('GET', `/governance-service/api/ai/application/*/policy?size=999&sort=createTime,desc`).as("getAIApplicationPolicy");

      // Click on the "Add Restriction" button
      cy.get('[data-testid="add-restriction-button"]').click();

      // Wait for the modal to appear
      cy.get('[data-testid="customized-dialog-title"]').contains('Add Restriction');
      
      // Fill in the description input field
      cy.get('[data-testid="description"] input').type("Test Restriction Description");

      // Wait for the API calls to complete and retrieve options for users, groups, and sensitive data
      cy.wait(['@getUsers', '@getGroups', '@getSensitiveData']).then(() => {

        // Select a random user from the API response and click on it
        cy.get('[data-testid="user-group-restriction"] input').click();
        cy.get('@getUsers').then((interception)  => {
          const randomUser = Cypress._.sample(interception.response.body.content);
          cy.contains('[data-testid="select-option-item"]', randomUser.username).click();
          cy.get('[data-testid="user-group-restriction"] input').click();
        });
  
        // Select a random group from the API response and click on it
        cy.get('[data-testid="user-group-restriction"] input').click();
        cy.get('@getGroups').then((interception) => {
          if (interception.response.body.content.length > 0) {
            const randomGroup = Cypress._.sample(interception.response.body.content);
            cy.contains('[data-testid="select-option-item"]', randomGroup.name).click();
          }
        });
  
        // Select a random sensitive data from the API response and type it in
        cy.get('[data-testid="sensitive-data-restriction"] input').click();
        cy.get('@getSensitiveData').then((interception) => {
          const randomSensitiveData = Cypress._.sample(interception.response.body.content);
          cy.get('[data-testid="sensitive-data-restriction"] input').type(randomSensitiveData.name);
          cy.get('[data-testid="select-option-item"]').contains(randomSensitiveData.name).click();
        });
  
        // Click the "Save" button
        cy.get('[data-test="modal-ok-btn"]').click();
        cy.get('#notistack-snackbar').should('contain.text', 'Restriction added successfully.');
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();

        // Verify that the modal closes
        cy.get('[data-testid="customized-dialog-title"]').should('not.exist');
    
        cy.wait('@getAIApplicationPolicy').then(interception => {
          // Ensure that Content Restriction are found
          expect(interception.response.body.content.length).to.gt(0);

          cy.get('[data-testid="tbody-with-data"]').children().first().within(() => {
            cy.get('[data-test="edit"]').should('exist').click();
          })

          // Check that the custom dialog for adding Content Restriction is visible
          cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
            // Wait for the modal to appear
            cy.get('[data-testid="customized-dialog-title"]').contains('Edit Restriction');
            
            // Fill in the description input field
            cy.get('[data-testid="description"] input').type("Test Restriction Description Edited");
            // Change the "Prompt" field option
            cy.get('[data-testid="prompt-restriction"] input').type('Allow').type('{enter}'); 
            // Change the "Reply" field option
            cy.get('[data-testid="reply-restriction"] input').type('Redact').type('{enter}'); 

            // Click the "Save" button
            cy.get('[data-test="modal-ok-btn"]').click();
          });

          cy.get('#notistack-snackbar').should('contain.text', 'Restriction updated successfully.');
          cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();

          // Verify that the modal closes
          cy.get('[data-testid="customized-dialog-title"]').should('not.exist');
          cy.get('[data-testid="application-overview-tab"]').click();
        });

        // Intercept API call to fetch AI application policies without search parameters
        cy.intercept(
          'GET', `/governance-service/api/ai/application/*/policy?size=999&sort=createTime,desc`
        ).as("getAIApplicationPolicy");
        cy.get('[data-testid="application-permissions-tab"]').click();
        cy.wait('@getAIApplicationPolicy').then(interception => {
          const {content} = interception.response.body;
          // Ensure that Content Restriction are found
          expect(content.length).to.gt(0);

          // Select the first Content Restriction and open the delete dialog
          cy.get('[data-testid="tbody-with-data"]').children().first().within(() => {
            // Ensure that the 'Delete' button exists and click it
            cy.get('[data-test="delete"]').should('exist').click();
          });

          // Confirm the deletion
          cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
            // Ensure that the confirmation title contains appropriate text
            cy.get('[data-testid="confirm-dialog-title"]').contains('Confirm Delete');

            // Ensure that the confirmation content contains the Content Restriction to be deleted
            cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to Delete the "${content[0].description}" restriction?`);

            // Click the 'Delete' button to confirm deletion
            cy.get('[data-test="confirm-yes-btn"]').contains('Delete').click();
          });
          // Verify that a success message is displayed after deletion
          cy.get('#notistack-snackbar').should('contain.text', 'Restriction has been deleted.');
          cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();

          // Verify that the deleted Content Restriction is not present in the table
          cy.get('[data-testid="tbody-with-data"]').within(() => {
            // Ensure that the Content Restriction does not contain the deleted value
            cy.get('[data-testid="table-row"]').should('not.contain', content[0].description);
          });
        });
      });
      // Delete app
      cy.get('[data-test="back-btn"]').click();
      deleteApp(appName);
    });

    it("should add API Keys and verify it in listing", () => {
        // Create the application
        createApplication(appName, appDesc, "on");

        // Verify the page title
        cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');

        // Iterate over each app card and click on the one with the matching app name
        cy.get('[data-testid="app-card"]').each(($card) => {
            cy.wrap($card).within(() => {
                cy.get('[data-testid="app-name"]').then(($appName) => {
                    if ($appName.text().trim() === appName) {
                        cy.wrap($card).as('selectedCard');
                    }
                });
            });
        });   

        // Click on the selected card
        cy.get('@selectedCard').click();     
        cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');
        cy.get('[data-testid="api-keys-tab"]').click();

        // Intercept the generate API key request
        cy.intercept('POST', '/account-service/api/apikey/v2/generate').as('generateApiKey');

        // Generate API Key with Never Expire
        cy.get('[data-testid="generate-api-key"]').click();
        cy.get('[data-testid="name"] [data-testid="input-field"]').type(apiKeyName);
        cy.get('[data-testid="description"] [data-testid="input-field"]').type(apiKeyDesc);
        cy.get('[data-testid="never-expire"]').click();
        cy.get('[data-test="modal-ok-btn"]').contains('Generate Key').click();

        // Verify the generated API key
        cy.wait('@generateApiKey').then((interception) => {
            const apiKeyMasked = interception.response.body.apiKeyMasked;
            cy.get('[data-testid="modal-body"]').within(() => {
                cy.get('.MuiAlert-message').should('contain.text', 'This API key is shown only once. Make sure to copy and save it securely, as it cannot be viewed again.');
                cy.get('[data-testid="command-text"]').should('have.text', '•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••');
                // Click to reveal the command
                cy.get('[data-testid="toggle-visibility-button"]').click();
                cy.get('[data-testid="command-text"]').should('have.text', apiKeyMasked);
                // Click to copy the command
                cy.get('[data-testid="copy-button"]').click();
                // Verify that the command is copied to the clipboard
                cy.window().then((win) => {
                    cy.stub(win.navigator.clipboard, 'readText').resolves(apiKeyMasked);
                });
            });
        });
        cy.get('[data-test="modal-cancel-btn"]').click();

        // Verify API Key in the listing
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', apiKeyName);
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', apiKeyDesc);

        // Generate another API Key with Expiry Date
        cy.get('[data-testid="generate-api-key"]').click();
        cy.get('[data-testid="name"] [data-testid="input-field"]').type(apiKeyNameExpiry);
        cy.get('[data-testid="description"] [data-testid="input-field"]').type(apiKeyDescExpiry);
        cy.get('[data-test="modal-ok-btn"]').contains('Generate Key').click();

        // Verify the generated API key with expiry
        cy.wait('@generateApiKey').then((interception) => {
            const apiKeyMasked = interception.response.body.apiKeyMasked;
            cy.get('[data-testid="modal-body"]').within(() => {
                cy.get('.MuiAlert-message').should('contain.text', 'This API key is shown only once. Make sure to copy and save it securely, as it cannot be viewed again.');
                cy.get('[data-testid="command-text"]').should('have.text', '•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••');
                // Click to reveal the command
                cy.get('[data-testid="toggle-visibility-button"]').click();
                cy.get('[data-testid="command-text"]').should('have.text', apiKeyMasked);
                // Click to copy the command
                cy.get('[data-testid="copy-button"]').click();
            });
        });
        cy.get('[data-test="modal-cancel-btn"]').click();

        // Verify API Key with Expiry in the listing
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', apiKeyNameExpiry);
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', apiKeyDescExpiry);
        cy.get('[data-test="back-btn"]').click();
    });

    it("should be able to search name and description in API Keys tab", () => {
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');

      // Iterate over each app card and click on the one with the matching app name
      cy.get('[data-testid="app-card"]').each(($card) => {
        cy.wrap($card).within(() => {
          cy.get('[data-testid="app-name"]').then(($appName) => {
            if ($appName.text().trim() === appName) {
              cy.wrap($card).as('selectedCard');
            }
          });
        });
      });

      // Click on the selected card
      cy.get('@selectedCard').click();
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');

      // Intercept API call to fetch API Keys
      cy.intercept('GET', '/account-service/api/apikey/application/getKeys*').as('listApiKeys');

      // Navigate to the API Keys tab
      cy.get('[data-testid="api-keys-tab"]').click();
      
      // Intercept the API request
      cy.wait('@listApiKeys').then((interception) => {
        if (interception.response.statusCode === 200) {
          const { content } = interception.response.body;  
          const randomNum = Math.floor(Math.random() * content.length);
          const randomApiName = content[randomNum].apiKeyName;
          const randomDescription = content[randomNum].description;

          // Filter by Key Name
          cy.intercept("/account-service/api/apikey/application/getKeys**").as("searchNameRequest");
          cy.get('[data-testid="structured-filter-input"]').click();
          cy.get('[data-testid="filter-options"]').contains('Key Name').click({force: true});
          cy.get('[data-testid="structured-filter-input"]').type(randomApiName).type('{enter}');
          
          // Wait for the search request to complete and handle the response
          cy.wait('@searchNameRequest').then(interception => {
            if (interception.response.statusCode === 200) {

              const url = new URL(interception.request.url);
              const params = new URLSearchParams(url.search);
              expect(params.get('apiKeyName')).to.eq(randomApiName);

              interception.response.body.content.forEach((item, i) => {
                cy.get('[data-testid="tbody-with-data"] tr').eq(i).within(() => {
                  cy.get('td').eq(0).contains(randomApiName, { matchCase: false });
                });
              });
            }
          });

          // Filter by Description
          if (randomDescription) {
            cy.intercept("/account-service/api/apikey/application/getKeys**").as("searchNameDescRequest");
            cy.get('[data-testid="structured-filter-input"]').click();
            cy.get('[data-testid="filter-options"]').contains('Description').click({force: true});
            cy.get('[data-testid="structured-filter-input"]').type(randomDescription).type('{enter}');
            
            // Wait for the search request to complete and handle the response
            cy.wait('@searchNameDescRequest').then(interception => {
              if (interception.response.statusCode === 200) {

                const url = new URL(interception.request.url);
                const params = new URLSearchParams(url.search);
                expect(params.get('apiKeyName')).to.eq(randomApiName);

                interception.response.body.content.forEach((item, i) => {
                  cy.get('[data-testid="tbody-with-data"] tr').eq(i).within(() => {
                    cy.get('td').eq(0).contains(randomApiName, { matchCase: false });
                    if (randomDescription) {
                      cy.get('td').eq(2).should('contain.text', randomDescription);
                    }
                  });
                });
              }
            })
          }
        } else {
          console.error("Failed to intercept a response with status code 200.");
        } 
      });
    });

    it("should Revoke and Delete API Keys", () => {
      // Verify the page title
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Applications');

      // Iterate over each app card and click on the one with the matching app name
      cy.get('[data-testid="app-card"]').each(($card) => {
        cy.wrap($card).within(() => {
          cy.get('[data-testid="app-name"]').then(($appName) => {
            if ($appName.text().trim() === appName) {
              cy.wrap($card).as('selectedCard');
            }
          });
        });
      });

      // Click on the selected card
      cy.get('@selectedCard').click();
      cy.get('[data-testid="page-title"]').should('contain.text', 'AI Application Details');

      // Navigate to the API Keys tab
      cy.get('[data-testid="api-keys-tab"]').click();

      // Revoke the first API Key
      handleAction(apiKeyName, 'revoke');
      // Verify that the first API Key is revoked
      cy.contains('[data-testid="tbody-with-data"]', apiKeyName).within(() => {
        cy.get(`[data-testid="table-row"]`).should('contain.text', 'Revoked');
      });

      // Revoke the second API Key
      handleAction(apiKeyNameExpiry, 'revoke');
      // Verify that the second API Key is revoked
      cy.contains('[data-testid="tbody-with-data"]', apiKeyNameExpiry).within(() => {
        cy.get(`[data-testid="table-row"]`).should('contain.text', 'Revoked');
      });

      // Intercept the API call to fetch API Keys after the first delete
      cy.intercept('GET', '/account-service/api/apikey/application/getKeys*').as('listApiKeysAfterFirstDelete');

      // Delete the first API Key
      handleAction(apiKeyName, 'delete');
      cy.get('[data-testid="application-permissions-tab"]').click();  
        
      // Verify that the API Key is deleted
      cy.get('[data-testid="api-keys-tab"]').click();
      cy.wait('@listApiKeysAfterFirstDelete').then((interception) => {
        const response = interception.response.body.content;
        if (response.length === 0) {
          cy.get('[data-testid="table-nodata"]').should('be.visible');
        } else {
          cy.get(`[data-testid="tbody-with-data"]`).should('not.contain.text', apiKeyName);
        }
      });

      // Intercept the API call to fetch API Keys after the second delete
      cy.intercept('GET', '/account-service/api/apikey/application/getKeys*').as('listApiKeysAfterSecondDelete');

      // Delete the second API Key
      handleAction(apiKeyNameExpiry, 'delete');
      cy.get('[data-testid="application-permissions-tab"]').click();  
      
      // Verify that the API Key is deleted
      cy.get('[data-testid="api-keys-tab"]').click();
      cy.wait('@listApiKeysAfterSecondDelete').then((interception) => {
        const response = interception.response.body.content;
        if (response.length === 0) {
          cy.get('[data-testid="tbody-with-nodata"]').should('be.visible');
        } else {
          cy.get(`[data-testid="tbody-with-data"]`).should('not.contain.text', apiKeyNameExpiry);
        }
      });

      // Navigate back and delete the application
      cy.get('[data-test="back-btn"]').click();
      deleteApp(appName);
    });

});
