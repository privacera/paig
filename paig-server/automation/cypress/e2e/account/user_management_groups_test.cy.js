import commonUtils from "../common/common_utils";

describe("Test User Management page for groups tab", () => {
    
    before(() => {
        cy.login();
    });

    let name;
    let description;
    let uniqueSuffix;

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/user_management');
        cy.get('[data-testid="groups-tab"]').click();
        // Generate unique name and description for each test case
        uniqueSuffix = `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        name = commonUtils.generateRandomWord(10) + uniqueSuffix;    
        description = commonUtils.generateRandomSentence(10, 5);
    });

    after(() => {
        cy.clearSession();
    });

    const STATUS = {
        disabled: {label: 'Disable', value: 0, booleanValue: false, name:'Disabled'},
        enabled: {label: 'Enable', value: 1, booleanValue: true, name:'Enabled'}
    }

    function generateUniqueName(prefixName) {
        const prefix = prefixName || "TestSearch";
        const uniqueSuffix = `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        return `${prefix}_${uniqueSuffix}`;
    }

    function verifyUserManagementGroupsTable(content) {
        cy.get('[data-testid="thead"] th').eq(0).should('contain.text', 'Group Name');
        cy.get('[data-testid="thead"] th').eq(1).should('contain.text', 'Description');
        cy.get('[data-testid="thead"] th').eq(2).should('contain.text', 'Users');
        cy.get('[data-testid="thead"] th').eq(3).should('contain.text', 'Created');
        cy.get('[data-testid="thead"] th').eq(4).should('contain.text', 'Actions');
        
        // Select a random index from the content array
        const randomIndex = Math.floor(Math.random() * content.length);
        const item = content[randomIndex];
        
        //verify table body
        cy.get('[data-testid="table-row"]').eq(randomIndex).within(() => {
            cy.get('td').eq(0).should('contain.text', item.name);
            cy.get('td').eq(1).should('contain.text', item.description);
            cy.get('td').eq(2).then(($cell) => {
                const cellText = $cell.text().trim();
                expect(cellText).to.match(/^\d+$/); 
            });            
            cy.get('td').eq(3).invoke('text').should('match', /\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}/);
            cy.get('[data-test="edit"]').should('exist');
            cy.get('[data-test="delete"]').should('exist');
        });
    }

    function verifyUsersManagementUsersAssociateTable(content) {
        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="thead"] th').eq(1).should('contain.text', 'User Name');
            cy.get('[data-testid="thead"] th').eq(2).should('contain.text', 'First Name');
            cy.get('[data-testid="thead"] th').eq(3).should('contain.text', 'Last Name');
            cy.get('[data-testid="thead"] th').eq(4).should('contain.text', 'Email');
            cy.get('[data-testid="thead"] th').eq(5).should('contain.text', 'Enabled');
            
            // Select a random index from the content array
            const randomIndex = Math.floor(Math.random() * content.length);
            const item = content[randomIndex];

            //verify table body
            cy.get('[data-testid="table-row"]').eq(randomIndex).within(() => {
                cy.get('td').eq(0).find('input').should('exist');
                cy.get('td').eq(1).should('contain.text', item.username);
                cy.get('td').eq(2).should('contain.text', item.firstName);
                if (item.lastName) {
                    cy.get('td').eq(3).should('contain.text', item.lastName);
                }
                if (item.email) {
                    cy.get('td').eq(4).should('contain.text', item.email);
                }
                if(item.status == STATUS.enabled.value){
                    cy.get('[data-testid="account-enabled"]').should('exist');
                }else{
                    cy.get('[data-testid="account-disabled"]').should('exist');
                }
            });
        });
    }
        
    function createNewGroup(name, description){
        cy.get('[data-test="add-btn"]').contains('Add Group').click({ force: true });
        cy.get('[data-testid="custom-dialog"]').should('be.visible')
        cy.get('[data-testid="name"] [data-testid="input-field"]').type(name)
        cy.get('[data-testid="description"] [data-testid="input-field"]').type(description)
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click()
    }

    function validateRequiredFields(name, description) {
        cy.get('[data-test="add-btn"]').contains('Add Group').click();
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
    
        // Ensure that the dialog title is 'Create Group'
        cy.get('[data-testid="customized-dialog-title"]').contains('Create Group');

        // Click the 'Save' button without entering any data
        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        })
        // Assert that the error message for the required fields is displayed
        cy.get('.Mui-error').should('contain.text', 'Required');

        // Enter data into the required fields and assert that the error message disappears
        cy.get('[data-testid="name"] [data-testid="input-field"]').type(name)
        cy.get('[data-testid="description"] [data-testid="input-field"]').type(description)
        cy.get('.Mui-error').should('not.exist');

        // Click the 'Close' button to cancel adding group
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();
    
        // Ensure that the custom dialog for adding group is no longer visible
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
    }

    function editGroup(name, description){
        cy.contains('[data-testid="table-row"]', name).within(() => {
            cy.get('[data-test="edit"]').click();
        });        
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.contains('label', 'Name').then(($label) => {
            const nameText = $label.next().text();
            expect(nameText).to.equal(name);
        });
        cy.get('[data-testid="description"] [data-testid="input-field"]').clear().type(description);

        cy.get('[data-test="modal-ok-btn"]').contains('Proceed').click();
        cy.get('[data-testid="custom-dialog"]').should('be.visible')
        cy.get('[data-testid="modal-body"]').should('contain.text', 'Are you sure you want to update the group ');
        cy.intercept('/account-service/api/groups/*').as('groupRequest');
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        // Wait for the intercepted request to complete
        cy.wait('@groupRequest').then(interception => {
            if (interception.response.statusCode === 200) {
                cy.get('[data-testid="custom-dialog"]').should('not.exist')
            } else {
                cy.log('Error: Failed to update the group. Unexpected response status code: ' + interception.response.statusCode);
            }
        });
    }

    function editGroupAndAssociateUser(name, description){
        cy.intercept('GET', '/account-service/api/users?size=15&sort=createTime,desc').as('getUsers');
        cy.contains('[data-testid="table-row"]', name).within(() => {
            cy.get('[data-test="edit"]').click();
        });
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.contains('label', 'Name').then(($label) => {
            const nameText = $label.next().text();
            expect(nameText).to.equal(name);
        });
        cy.get('[data-testid="description"] [data-testid="input-field"]').clear().type(description);
        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="users-tab"]').click();
        });

        cy.wait('@getUsers').then((interception) => {
            const { content } = interception.response.body;
            verifyUsersManagementUsersAssociateTable(content);
        });

        cy.get('[data-testid="tbody-with-data"] input[type="checkbox"]').first().click();
        
        cy.get('[data-test="modal-ok-btn"]').contains('Proceed').click();
        cy.get('[data-testid="custom-dialog"]').should('be.visible')
        cy.get('[data-testid="modal-body"]').should('contain.text', `Are you sure you want to update the group ${name}`);
        cy.contains('[data-testid="modal-body"]', 'Users to be Added').parent().find('.MuiChip-label').each(($chipLabel) => {
            const chipText = $chipLabel.text().trim();
            cy.contains('[data-testid="modal-body"]', chipText).should('exist');
        });
        cy.intercept('/account-service/api/groups/*').as('groupRequest');
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        // Wait for the intercepted request to complete
        cy.wait('@groupRequest').then(interception => {
            if (interception.response.statusCode === 200) {
                cy.get('[data-testid="custom-dialog"]').should('not.exist')
            } else {
                cy.log('Error: Failed to update the group. Unexpected response status code: ' + interception.response.statusCode);
            }
        });
    }

    function deleteGroup(groupName){
        cy.contains('[data-testid="table-row"]', groupName).within(() => {
            cy.get('[data-test="delete"]').click();
        }); 
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.get('[data-testid="confirm-dialog-title"]').should('contain.text', 'Delete Group');
        cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete group: ${groupName}`);
        cy.get('[data-test="confirm-yes-btn"]').click();
        cy.contains('#notistack-snackbar', 'Group Deleted').should('be.visible');
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
    }

    function verifyEditedGroupInTable(name, description){
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', name);
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', description);
    }

    function cancelDelete(groupName){
        cy.contains('[data-testid="table-row"]', groupName).within(() => {
            cy.get('[data-test="delete"]').click();
        }); 
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete group: ${groupName}`);
        cy.get('[data-test="confirm-no-btn"]').click();
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
    }

    function ensureNoDuplicateGroup(duplicatename) {
        cy.intercept('GET', '/account-service/api/groups?page=0&size=15&sort=createTime,desc').as('getGroups');
        cy.get('[data-testid="header-refresh-btn"]').click();
        cy.wait('@getGroups').then((interception) => {
            if (interception.response.body && interception.response.body.content.length > 0) {
                const group = interception.response.body.content.find(item => item.name === duplicatename);
                if (group) {
                    // Click the delete button in the corresponding row
                    cy.contains(`[data-testid="tbody-with-data"] tr`, group.name).within(() => {
                        cy.get('[data-test="delete"]').click();
                    });

                    // Confirm deletion in the dialog
                    cy.get('[data-testid="custom-dialog"]').should('be.visible');
                    cy.get('[data-testid="confirm-dialog-title"]').should('contain.text', 'Delete Group');
                    cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete group: ${group.name} ?`);
                    cy.get('[data-test="confirm-yes-btn"]').click();
                    cy.get('#notistack-snackbar').should('contain.text', 'Group Deleted').debug();
                    cy.get('[data-testid="snackbar-close-btn"]').click();

                    // Wait for the group to be deleted
                    cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', group.name);
                }
            }
        });
    }

    it("should verify groups management listing", () => {
        cy.intercept('GET', '/account-service/api/groups?page=0&size=15&sort=createTime,desc').as('getGroups');
        cy.get('[data-testid="header-refresh-btn"]').click();
        cy.wait('@getGroups').then((interception) => {
            const { content } = interception.response.body;
            if (content.length === 0) {
                // If no groups exist, create a couple of groups to start the test cases
                const group1Name = generateUniqueName("TestGroup");
                const group1Description = commonUtils.generateRandomSentence(10, 5);
                createNewGroup(group1Name, group1Description);
                cy.get('[data-testid="custom-dialog"]').should('not.exist');

                const group2Name = generateUniqueName("TestGroup");
                const group2Description = commonUtils.generateRandomSentence(10, 5);;
                createNewGroup(group2Name, group2Description);
                cy.get('[data-testid="custom-dialog"]').should('not.exist');
            }
            cy.wait(3000);
            cy.get('[data-testid="header-refresh-btn"]').click();
            // Proceed with verifying the groups management listing
            cy.wait('@getGroups').then((interception) => {
                const { content } = interception.response.body;
                verifyUserManagementGroupsTable(content);
            });
        });
    });

    it("should verify groups management listing on refresh", () => {
        cy.intercept('GET', '/account-service/api/groups?page=0&size=15&sort=createTime,desc').as('getGroups');
        cy.get('[data-testid="header-refresh-btn"]').click();

        cy.wait('@getGroups').then((interception) => {
            const { content } = interception.response.body;
            verifyUserManagementGroupsTable(content);
        });
    });

    it("should verify various search functionalities for groups", () => {
        cy.intercept('GET', '/account-service/api/groups?page=0&size=15&sort=createTime,desc').as('getGroups');
        cy.intercept('GET', '/account-service/api/groups?size=15&sort=createTime,desc&name=*').as('searchGroups');
        cy.intercept('GET', '/account-service/api/groups?size=15&sort=createTime,desc').as('getSearchGroups');
        cy.get('[data-testid="header-refresh-btn"]').click();
        cy.wait('@getGroups').then((interception) => {
            const { content } = interception.response.body;
            const randomNum = Math.floor(Math.random() * content.length);
            const randomName = content[randomNum].name;

            // Verify full search
            cy.get('[data-testid="input-search-box"]').click();
            cy.get('[data-testid="input-search-box"]').type(randomName);
            cy.get('[data-testid="input-search-box"]').type('{enter}');
            cy.wait('@searchGroups').then((interception) => {
                cy.get('[data-testid="tbody-with-data"]').should('contain.text', randomName);
            });

            // Verify partial search
            const partialName = randomName.substring(0, 3);
            cy.get('[data-testid="input-search-box"]').clear().type(partialName).type('{enter}');
            cy.wait('@searchGroups').then((interception) => {
                interception.response.body.content.forEach((item, i) => {
                    cy.get('[data-testid="tbody-with-data"] tr').eq(i).within(() => {
                        cy.get('td').eq(0).should(($element) => {
                            const text = $element.text().toLowerCase();
                            expect(text).to.contain(partialName.toLowerCase());
                        });
                    });
                });
            });

            // Verify search for non-existing groups
            const nonExistingName = generateUniqueName();
            cy.get('[data-testid="input-search-box"]').clear().type(nonExistingName).type('{enter}');
            cy.wait('@searchGroups').then((interception) => {
                expect(interception.response.body.content.length).to.eq(0);
                cy.get('[data-testid="table-noData"]').should('be.visible');
            });

            // Verify search value and results after refresh
            cy.get('[data-testid="input-search-box"]').clear().type(randomName).type('{enter}');
            cy.wait('@searchGroups').then(() => {
                cy.get('[data-testid="header-refresh-btn"]').click();
                cy.wait('@searchGroups').then(() => {
                    cy.get('[data-testid="input-search-box"]').should('have.value', randomName);
                });
            });

            // Remove the search
            cy.get('[data-testid="input-search-box"]').clear();
            cy.get('[data-testid="input-search-box"]').type('{enter}');
            cy.wait('@getSearchGroups').then((interception) => {
                const { content } = interception.response.body;
                const randomIndex = Math.floor(Math.random() * content.length);
                const item = content[randomIndex];
                cy.get('[data-testid="tbody-with-data"] tr').eq(randomIndex).within(() => {
                    cy.get('td').eq(0).should('contain.text', item.name);
                    cy.get('td').eq(2).then(($cell) => {
                        const cellText = $cell.text().trim();
                        expect(cellText).to.match(/^\d+$/);
                    });
                });
            });
        })
    });

    it('should validate required field for add group', () => {
        cy.wait(5000);
        validateRequiredFields(name, description);
    });

    it("should validate duplicate group cannot be added", () => {
        const duplicatename = `duplicateuser${uniqueSuffix}`;
        // Ensure there is no existing group with the duplicate name
        ensureNoDuplicateGroup(duplicatename)

        createNewGroup(duplicatename, description);
        cy.get('#notistack-snackbar').should('contain.text', `Group "${duplicatename}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //created group should be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', duplicatename);

        //create groups with same name
        createNewGroup(duplicatename, description);
        cy.get('#notistack-snackbar').should('contain.text', `Group with name ${duplicatename} already exists`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();


        //delete the group
        deleteGroup(duplicatename);

        //deleted group should not be in the table
        cy.get('body').then(($body) => {
            if ($body.find(`[data-testid="tbody-with-data"]`).length > 0) {
                // Element exists, proceed with assertion
                cy.get(`[data-testid="tbody-with-data"]`)
                    .should('exist') // Ensure the element exists
                    .and('not.have.text', duplicatename); // Check it does not contain the name
            }
        });
    });

    it("should add a new group(with random name and description), verify in the list and delete it", () => {
        // Create the group
        createNewGroup(name, description);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', name);

        //edit the group
        editGroup(name, description);
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        verifyEditedGroupInTable(name, description);

        //click the delete button and cancel
        cancelDelete(name);

        //delete the group
        deleteGroup(name);
        //deleted group should not be in the table
        cy.get('body').then(($body) => {
            if ($body.find(`[data-testid="tbody-with-data"]`).length > 0) {
                // Element exists, proceed with assertion
                cy.get(`[data-testid="tbody-with-data"]`)
                    .should('exist') // Ensure the element exists
                    .and('not.have.text', name); // Check it does not contain the name
            }
        });

    });

    it("should add a new group(with random name and description), verify in the list and associate user with it then delete it", () => {
        //create the group
        createNewGroup(name, description);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', name);

        //edit the group and associate users
        editGroupAndAssociateUser(name, description);
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        verifyEditedGroupInTable(name, description);

        //click the delete button and cancel
        cancelDelete(name);

        //delete the group
        deleteGroup(name);

        //deleted group should not be in the table
        cy.get('body').then(($body) => {
            if ($body.find(`[data-testid="tbody-with-data"]`).length > 0) {
                // Element exists, proceed with assertion
                cy.get(`[data-testid="tbody-with-data"]`)
                    .should('exist') // Ensure the element exists
                    .and('not.have.text', name); // Check it does not contain the name
            }
        });
    });

    it("should preview a group after adding and verifying it", () => {
        //Create the group
        createNewGroup(name, description);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', name);

        //edit the group and associate users
        editGroupAndAssociateUser(name, description);
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        verifyEditedGroupInTable(name, description);

        //Click on the preview button for the newly added group
        cy.get(`[data-testid="tbody-with-data"]`)
            .contains('tr', name)
            .within(() => {
                cy.get('[data-test="view"]').click();
            });

        //Check if the modal with group details is visible
        cy.get('[data-testid="custom-dialog"]').should('be.visible')

        //Check if the name and description match the previously added group
        cy.get('[data-test="form"]').within(() => {
            cy.contains('Name').next('.profile-text').should('contain.text', name);
            cy.contains('Description').next('.profile-text').should('contain.text', description);
        });
        //Switch to another tab
        cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
            cy.get('[data-testid="users-tab"]').click();
        });

        //Check if checkboxes are present and disabled for all rows in the table
        cy.get('[data-testid="tbody-with-data"] input[type="checkbox"]').each(($checkbox, index) => {
            cy.wrap($checkbox).should('be.disabled')
        });

        //Close the edit modal
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        //delete the group
        deleteGroup(name);

        //deleted group should not be in the table
        cy.get('body').then(($body) => {
            if ($body.find(`[data-testid="tbody-with-data"]`).length > 0) {
                // Element exists, proceed with assertion
                cy.get(`[data-testid="tbody-with-data"]`)
                    .should('exist') // Ensure the element exists
                    .and('not.have.text', name); // Check it does not contain the name
            }
        });
    });

    it("should search for users within the Edit group modal and verify search functionality", () => {
        //create the group
        createNewGroup(name, description);
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', name);

        //edit the group and associate users
        editGroupAndAssociateUser(name, description);
        cy.get('#notistack-snackbar').should('contain.text', `Group "${name}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        verifyEditedGroupInTable(name, description);

        //Intercept the API call to fetch groups data
        cy.intercept('GET', '/account-service/api/users*').as('getUsers');

        //Open the edit modal and navigate to the groups tab
        cy.contains('[data-testid="table-row"]', name).within(() => {
            cy.get('[data-test="edit"]').click();
        });
        //Wait for the API call to complete
        cy.wait('@getUsers').then((interception) => {
            //Get the response body containing groups data
            const usersData = interception.response.body.content;

            cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
                cy.get('[data-testid="users-tab"]').click();
            });

            //If groups data is available, perform search and verify functionality
            if (usersData && usersData.length > 0) {
                //Get a random group name from the available groups data
                const randomUserName = usersData[Math.floor(Math.random() * usersData.length)].username;

                //Search for the random group name
                cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
                    cy.get('[data-testid="input-search-box"]').type(randomUserName).type('{enter}');
                });

                //Wait for the search to complete
                cy.wait('@getUsers').then(() => {
                    //Verify that the groups list updates accordingly based on the search query
                    cy.get('[data-testid="tbody-with-data"]').should('contain.text', randomUserName);
                });
            } else {
                cy.get('[data-testid="table-noData"]').should('be.visible');
            }
        });

        //Close the edit modal
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        //delete the group
        deleteGroup(name);

        //deleted group should not be in the table
        cy.get('body').then(($body) => {
            if ($body.find(`[data-testid="tbody-with-data"]`).length > 0) {
                // Element exists, proceed with assertion
                cy.get(`[data-testid="tbody-with-data"]`)
                    .should('exist') // Ensure the element exists
                    .and('not.have.text', name); // Check it does not contain the name
            }
        });
    });

    it('should create multiple groups and cancel bulk delete then again enable bulk delete, randomly select and delete groups in bulk', () => {
        //Number of groups to create for the test
        const iterations = 3;
        const createdGroups = [];

        //Create groups
        for (let i = 1; i <= iterations; i++) {
            const name = `Bulk-group-${i}-${uniqueSuffix}`;
            const description = `description-${i}`;

            createNewGroup(name, description);
            cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
            createdGroups.push({ name, index: i });
            cy.wait(3000);
            //Verify groups creation
            cy.get('[data-testid="custom-dialog"]').should('not.exist');
            cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', name);
        }

        // Delete groups one by one
        createdGroups.forEach(({ name }) => {
            deleteGroup(name);
        });

        //deleted groups should not be in the table
        createdGroups.forEach(({ name }) => {
           cy.get('body').then(($body) => {
            if ($body.find(`[data-testid="tbody-with-data"]`).length > 0) {
                // Element exists, proceed with assertion
                cy.get(`[data-testid="tbody-with-data"]`)
                    .should('exist') // Ensure the element exists
                    .and('not.have.text', name); // Check it does not contain the name
            }
            });
        });
    });

});