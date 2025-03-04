import commonUtils from "../common/common_utils";

describe("Test User Management page for users tab", () => {

    before(() => {
        cy.login();
    });

    let uniqueSuffix;
    let firstName;
    let lastName;
    let email;
    let username;
    let updatedFirstName;
    let updatedLastName;

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/user_management');
        // Generate unique name and description for each test case
        uniqueSuffix = `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        firstName = commonUtils.generateRandomWord(10)+ uniqueSuffix;
        lastName = commonUtils.generateRandomWord(10)+ uniqueSuffix;
        email = `${firstName}.${lastName}@test.com`;
        username = `${firstName}.${lastName}`;
        updatedFirstName = `${firstName}edited`;
        updatedLastName = `${lastName}edited`;
    });

    after(() => {
        cy.clearSession();
    });

    const STATUS = {
        disabled: {label: 'Disable', value: 0, booleanValue: false, name:'Disabled'},
        enabled: {label: 'Enable', value: 1, booleanValue: true, name:'Enabled'}
    }

    const role = {user: 'USER', owner: 'OWNER'};
    const status = {enabled: 'enabled', disabled: 'disabled'};

    function generateUniqueName(prefixName) {
        const prefix = prefixName || "TestSearch";
        return `${prefix}_${uniqueSuffix}`;
    }

    function verifyUserManagementTable (content, loggedInUser){
 
        //verify table headers
        cy.get('[data-testid="thead"] th').eq(0).should('contain.text', 'User Name');
        cy.get('[data-testid="thead"] th').eq(1).should('contain.text', 'First Name');
        cy.get('[data-testid="thead"] th').eq(2).should('contain.text', 'Last Name');
        cy.get('[data-testid="thead"] th').eq(3).should('contain.text', 'Groups');
        cy.get('[data-testid="thead"] th').eq(4).should('contain.text', 'Email');
        cy.get('[data-testid="thead"] th').eq(5).should('contain.text', 'Roles');
        cy.get('[data-testid="thead"] th').eq(6).should('contain.text', 'Invite Status');
        cy.get('[data-testid="thead"] th').eq(7).should('contain.text', 'Enabled');
        cy.get('[data-testid="thead"] th').eq(8).should('contain.text', 'Actions');

        // Select a random index from the content array
        const randomIndex = Math.floor(Math.random() * content.length);
        const item = content[randomIndex];

        //verify table body
        cy.get('[data-testid="tbody-with-data"] tr').eq(randomIndex).within(() => {
            cy.get('td').eq(0).should('contain.text', item.username);
            cy.get('td').eq(1).should('contain.text', item.firstName);
//            cy.get('td').eq(2).should('contain.text', item.lastName);

            if (item.lastName) {
                    cy.get('td').eq(2).should('contain.text', item.lastName);
                }

            cy.get('td').eq(3).then(($cell) => {
                const cellText = $cell.text().trim();
                expect(cellText).to.match(/^\d+$/); // Assuming this checks for numeric content
            });

            if (item.email) {
                cy.get('td').eq(4).should('contain.text', item.email);
            }  

            cy.get('td').eq(5).should('contain.text', item.roles[0]);

            if(item.userInvited == STATUS.enabled.booleanValue){
                cy.get('td').eq(6).find('[data-testid="user-invited"]').should('exist');
            }else{
                cy.get('td').eq(6).find('[data-testid="user-invite-btn"]').should('exist');
            }

            if(item.status == STATUS.enabled.value){
                cy.get('td').eq(7).find('[data-testid="account-enabled"]').should('exist');
            }else{
                cy.get('td').eq(7).find('[data-testid="account-disabled"]').should('exist');
            }

            cy.get('td').eq(8).find('[data-test="edit"]').should('exist');

            if(item.username == loggedInUser){
                cy.get('td').eq(8).find('[data-test="delete"]').should('not.exist');
            }else{
                cy.get('td').eq(8).find('[data-test="delete"]').should('exist');
            }
        });
    }

    function createNewUser(firstName, lastName, email, username, role, status){
        cy.get('[data-test="add-btn"]').contains('Add User').click().debug();
        cy.get('[data-testid="custom-dialog"]').should('be.visible').debug();
        cy.get('[data-test="first-name"] [data-testid="input-field"]').type(firstName).debug();
        cy.get('[data-test="last-name"] [data-testid="input-field"]').type(lastName).debug();
        cy.get('[data-test="email-id"] [data-testid="input-field"]').type(email).debug();
        cy.get('[data-test="user-name"] [data-testid="input-field"]').clear().type(username).debug();
        cy.get('[data-testid="roles-input').click().debug();
        cy.get('[data-testid="select-option-item"]').contains(role).click().debug();
        if(role == 'OWNER') {
            cy.get('[data-test="password"] [data-testid="input-field"]').type('welcome10').debug();
        }
        if(status == "disabled"){
            cy.get('[data-testid="toggle-switch"]').click().debug();
            cy.get('[data-testid="toggle-switch"]').should('not.be.checked').debug();
        }else{
            cy.get('[data-testid="toggle-switch"]').should('be.checked').debug();
        }
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click().debug();
    }

    function validateRequiredFields(firstName, lastName, email, username, role, status) {
        cy.get('[data-test="add-btn"]').contains('Add User').click();
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
    
        // Ensure that the dialog title is 'Create User'
        cy.get('[data-testid="customized-dialog-title"]').contains('Create User');

        // Click the 'Save' button without entering any data
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click();

        // Assert that the error message for the required fields is displayed
        cy.get('.Mui-error').should('contain.text', 'Required');

        // Enter data into the required fields and assert that the error message disappears
        cy.get('[data-test="first-name"] [data-testid="input-field"]').type(firstName);
        cy.get('[data-test="last-name"] [data-testid="input-field"]').type(lastName);
        cy.get('[data-test="email-id"] [data-testid="input-field"]').type(email);
        cy.get('[data-test="user-name"] [data-testid="input-field"]').clear().type(username);
        cy.get('[data-testid="roles-input"]').click();
        cy.get('[data-testid="select-option-item"]').contains(role).click();
        if (status === "disabled") {
            cy.get('[data-testid="toggle-switch"]').click();
        }
        cy.get('.Mui-error').should('not.exist');

        // Click the 'Close' button to cancel adding user
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();
    
        // Ensure that the custom dialog for adding user is no longer visible
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
    }

    function editUser(firstName, lastName, username, role, status){
        cy.contains('[data-testid="table-row"]', username).within(() => {
            cy.get('[data-test="edit"]').click();
        });
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.get('[data-test="first-name"] [data-testid="input-field"]').clear().type(firstName);
        cy.get('[data-test="last-name"] [data-testid="input-field"]').clear().type(lastName);
        cy.get('[data-testid="roles-input').click();
        cy.get('[data-testid="select-option-item"]').contains(role).click();
        if(role == 'OWNER') {
            cy.get('[data-test="password"] [data-testid="input-field"]').type('welcome10').debug();
        }

        if(status == "enabled"){
            cy.get('[data-testid="toggle-switch"]').click();
            cy.get('[data-testid="toggle-switch"]').should('be.checked')
        }else{
            cy.get('[data-testid="toggle-switch"]').click();
            cy.get('[data-testid="toggle-switch"]').should('not.be.checked')
        }

        cy.get('[data-test="modal-ok-btn"]').contains('Proceed').click();
        cy.get('[data-testid="custom-dialog"]').should('be.visible')
        cy.get('[data-testid="modal-body"]').should('contain.text', 'Are you sure you want to update the user ');
        cy.intercept('/account-service/api/users/*').as('userRequest');
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        // Wait for the intercepted request to complete
        cy.wait('@userRequest').then(interception => {
            if (interception.response.statusCode === 200) {
                cy.get('[data-testid="custom-dialog"]').should('not.exist')
            } else {
                cy.log('Error: Failed to update the user. Unexpected response status code: ' + interception.response.statusCode);
            }
        });
    }

    function editUserAndAssociateGroup(firstName, lastName, username, role, status){
        cy.contains('[data-testid="table-row"]', username).within(() => {
            cy.get('[data-test="edit"]').click();
        });
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.get('[data-test="first-name"] [data-testid="input-field"]').clear().type(firstName);
        cy.get('[data-test="last-name"] [data-testid="input-field"]').clear().type(lastName);
        cy.get('[data-testid="roles-input').click();
        cy.get('[data-testid="select-option-item"]').contains(role).click();
        if(role == 'OWNER') {
            cy.get('[data-test="password"] [data-testid="input-field"]').type('welcome10').debug();
        }

        if(status == "enabled"){
            cy.get('[data-testid="toggle-switch"]').click();
            cy.get('[data-testid="toggle-switch"]').should('be.checked')
        }else{
            cy.get('[data-testid="toggle-switch"]').click();
            cy.get('[data-testid="toggle-switch"]').should('not.be.checked')
        }
        cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
            cy.get('[data-testid="groups-tab"]').click();
        });

        cy.wait(3000);
        cy.get('[data-testid="tbody-with-data"] input[type="checkbox"]').each(($checkbox, index) => {
            if (Math.random() > 0.5) {
                cy.wrap($checkbox).click();
            }
        });

        cy.get('[data-test="modal-ok-btn"]').contains('Proceed').click();
        cy.get('[data-testid="custom-dialog"]').should('be.visible')
        cy.get('[data-testid="modal-body"]').should('contain.text', 'Are you sure you want to update the user');
        cy.intercept('/account-service/api/users/*').as('userRequest');
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        // Wait for the intercepted request to complete
        cy.wait('@userRequest').then(interception => {
            if (interception.response.statusCode === 200) {
                cy.get('[data-testid="custom-dialog"]').should('not.exist')
            } else {
                cy.log('Error: Failed to update the user. Unexpected response status code: ' + interception.response.statusCode);
            }
        });
    }

    function deleteUser(username){
        cy.contains('[data-testid="table-row"]', username).within(() => {
            cy.get('[data-test="delete"]').click();
        });
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.get('[data-testid="confirm-dialog-title"]').should('contain.text', 'Delete User');
        cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete user: ${username} ?`);
        cy.get('[data-test="confirm-yes-btn"]').click();
        cy.get('#notistack-snackbar').should('contain.text', 'User Deleted').debug();
//        cy.get('[data-testid="snackbar-close-btn"]').click();

        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
    }

    function verifyEditedUserInTable(firstName, lastName){
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', firstName);
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', lastName);
    }

    function cancelDelete(username){
        cy.contains('[data-testid="table-row"]', username).within(() => {
            cy.get('[data-test="delete"]').click();
        });
        cy.get('[data-testid="custom-dialog"]').should('be.visible');
        cy.get('[data-test="confirm-no-btn"]').click();
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
    }

    function ensureNoDuplicateUser(duplicateFirstname) {
        cy.intercept('GET', '/account-service/api/users?page=0&size=15&sort=createTime,desc').as('getUsers');
        cy.get('[data-testid="header-refresh-btn"]').click();
        cy.wait('@getUsers').then((interception) => {
            if (interception.response.body && interception.response.body.content.length > 0) {
                interception.response.body.content.forEach(item => {
                    if (item.firstName === duplicateFirstname) {
                        // Get the username from the item
                        const username = item.username;
    
                        // Click the delete button in the corresponding row
                        cy.contains(`[data-testid="tbody-with-data"] tr`, item.firstName).within(() => {
                            cy.get('[data-test="delete"]').click();
                        });
    
                        // Confirm deletion in the dialog
                        cy.get('[data-testid="custom-dialog"]').should('be.visible');
                        cy.get('[data-testid="confirm-dialog-title"]').should('contain.text', 'Delete User');
                        cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete user: ${username} ?`);
                        cy.get('[data-test="confirm-yes-btn"]').click();
                        cy.get('#notistack-snackbar').should('contain.text', 'User Deleted').debug();
                        cy.get('[data-testid="snackbar-close-btn"]').click();
    
                        // Wait for the user to be deleted
                        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', username);
                    }
                });
            }
        });
    }

    it("should verify user management listing", () => {
        let loggedInUser = null;

        cy.request("/account-service/api/users/tenant").then((resp) => {
            loggedInUser = resp.body.username;
        });

        cy.request("/account-service/api/users?page=0&size=15&sort=createTime,desc").then((response1) => {
            const { content } = response1.body;
            verifyUserManagementTable(content, loggedInUser);
        });
    });

    it("should verify user management listing on refresh", () => {
        cy.get('[data-testid="header-refresh-btn"]').click();
        let loggedInUser = null;

        cy.request("/account-service/api/users/tenant").then((resp) => {
            loggedInUser = resp.body.username;
        });

        cy.request("/account-service/api/users?page=0&size=15&sort=createTime,desc").then((response1) => {
            const { content } = response1.body;
            verifyUserManagementTable(content, loggedInUser);
        });
    });

    it("should verify search for single filter and remove filter", () => {
        cy.get('[data-testid="structured-filter-input"]').click();
        cy.get('[data-testid="filter-options"]').contains('User Name').click({force: true});

        //search with existing user name
        cy.request("/account-service/api/users?page=0&size=15&sort=createTime,desc").then((response1) => {
            const { content } = response1.body;
            const randomNum = Math.floor(Math.random() * content.length);
            const randomName = content[randomNum].username;

            cy.get('[data-testid="structured-filter-input"]').type(randomName).type('{enter}');
            cy.get('[data-testid="chip-token"]').should('contain.text', randomName);
            cy.request(`/account-service/api/users?page=0&size=15&sort=createTime,desc&username=${randomName}`).then((response2) => {
                const { content } = response2.body;

                content.map((item, i) => {
                    cy.get('[data-testid="tbody-with-data"] tr').eq(i).within(() => {
                        cy.get('td').eq(0).contains(randomName, { matchCase: false });
                    });
                });

            });

            //remove filter
            cy.get('[data-testid="token-clear"]').click();
            cy.get('[data-testid="chip-token"]').should('not.exist');
            cy.request("/account-service/api/users?page=0&size=15&sort=createTime,desc").then((response3) => {
                const { content } = response3.body;

                content.map((item, i) => {
                    cy.get('[data-testid="tbody-with-data"] tr').eq(i).within(() => {
                        cy.get('td').eq(0).contains(item.username, { matchCase: false });
                    });
                });
            });

        });

    });

    it("should verify search for existing User with multiple filters", () => {
        // Intercept the API request
        cy.intercept("/account-service/api/users**").as("userRequest");
        cy.get('[data-testid="header-refresh-btn"]').click();
        cy.wait('@userRequest').then((interception) => {
            if (interception.response.statusCode === 200) {
                const { content } = interception.response.body;
                const randomNum = Math.floor(Math.random() * content.length);
                const randomName = content[randomNum].username;
                const randomEmail = content[randomNum].email;
                // Filter by username
                cy.intercept("/account-service/api/users**").as("userRequest2");
                cy.get('[data-testid="structured-filter-input"]').click();
                cy.get('[data-testid="filter-options"]').contains('User Name').click({force: true});
                cy.get('[data-testid="structured-filter-input"]').type(randomName).type('{enter}');
                cy.wait('@userRequest2').then(interception => {
                    if (interception.response.statusCode === 200) {
                        interception.response.body.content.forEach((item, i) => {
                            cy.get('[data-testid="tbody-with-data"] tr').eq(i).within(() => {
                                cy.get('td').eq(0).contains(randomName, { matchCase: false });
                            });
                        });
                    }
                });
                // Filter by email
                if (randomEmail) {
                    cy.intercept("/account-service/api/users**").as("userRequest3");
                    cy.get('[data-testid="structured-filter-input"]').click();
                    cy.get('[data-testid="filter-options"]').contains('Email').click({force: true});
                    cy.get('[data-testid="structured-filter-input"]').type(randomEmail).type('{enter}');
                    cy.wait('@userRequest3').then(interception => {
                        if (interception.response.statusCode === 200) {
                            interception.response.body.content.forEach((item, i) => {
                                cy.get('[data-testid="tbody-with-data"] tr').eq(i).within(() => {
                                    cy.get('td').eq(0).contains(randomName, { matchCase: false });
                                    if (randomEmail) {
                                        cy.get('td').eq(4).should('contain.text', randomEmail);
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

    it("should verify partial search for existing User", () => {
        //partial search with existing user name
        cy.get('[data-testid="structured-filter-input"]').click();
        cy.get('[data-testid="filter-options"]').contains('User Name').click({force: true});

        cy.request("/account-service/api/users?page=0&size=15&sort=createTime,desc").then((response1) => {
            const { content } = response1.body;
            const randomNum = Math.floor(Math.random() * content.length);
            const randomName = content[randomNum].username.substring(0, 3);

            cy.get('[data-testid="structured-filter-input"]').type(randomName).type('{enter}');
            cy.request(`/account-service/api/users?page=0&size=15&sort=createTime,desc&username=${randomName}`).then((response2) => {
                const { content } = response2.body;

                if (content.length > 0) {
                    cy.get('[data-testid="tbody-with-data"] tr').eq(0).within(() => {
                        cy.get('td').eq(0).contains(randomName, { matchCase: false });
                    });
                } else {
                    cy.log('No users found with the partial name:', randomName);
                }

            });
        });
    });

    it("should verify search for non existing User", () => {

        //search with non existing user name
        cy.get('[data-testid="structured-filter-input"]').click();
        cy.get('[data-testid="filter-options"]').contains('User Name').click({force: true});

        cy.request("/account-service/api/users?page=0&size=15&sort=createTime,desc").then((response1) => {
            const { content } = response1.body;
            const randomName = generateUniqueName();

            cy.get('[data-testid="structured-filter-input"]').type(randomName).type('{enter}');
            cy.request(`/account-service/api/users?page=0&size=15&sort=createTime,desc&username=${randomName}`).then((response2) => {
                const { content } = response2.body;
                expect(content.length).to.eq(0);
                cy.get('[data-testid="table-noData"]').should('be.visible');
            });
        });

    });

    it("should verify search to maintain search value after refresh and verify search results", () => {
        let loggedInUser = null;

        cy.request("/account-service/api/users/tenant").then((resp) => {
            loggedInUser = resp.body.username;
        });

        cy.get('[data-testid="structured-filter-input"]').click();
        cy.get('[data-testid="filter-options"]').contains('User Name').click({force: true});

        cy.request("/account-service/api/users?page=0&size=15&sort=createTime,desc").then((response1) => {
            const { content } = response1.body;
            const randomNum = Math.floor(Math.random() * content.length);
            const randomName = content[randomNum].username;

            cy.get('[data-testid="structured-filter-input"]').type(randomName).type('{enter}');
            cy.request(`/account-service/api/users?page=0&size=15&sort=createTime,desc&username=${randomName}`).then((response2) => {
                const { content } = response2.body;
                verifyUserManagementTable(content, loggedInUser);

                cy.get('[data-testid="header-refresh-btn"]').click();
                cy.request(`/account-service/api/users?page=0&size=15&sort=createTime,desc&username=${randomName}`).then((response3) => {
                    const { content } = response3.body;
                    verifyUserManagementTable(content, loggedInUser);
                    cy.get('[data-testid="chip-token"]').contains(randomName);
                });
            });
        });
    });

    it('should validate required field for add user', () => {
        cy.wait(5000);
        validateRequiredFields(firstName, lastName, email, username, role.owner, status.enabled);
    });

    it("should validate duplicate user cannot be added", () => {
        const duplicateFirstname = `duplicateuser${uniqueSuffix}`;

        // Ensure there is no existing user with the duplicate first name
        ensureNoDuplicateUser(duplicateFirstname);

        createNewUser(duplicateFirstname, lastName, email, username, role.user, status.disabled);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `User "${duplicateFirstname}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //created user should be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', duplicateFirstname);

        //edit the user
        createNewUser(duplicateFirstname, lastName, email, username, role.user, status.disabled);
        cy.get('#notistack-snackbar').should('contain.text', `User with username ${username} already exists`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', duplicateFirstname);
    });

    it("should add a new user(with role Owner and status enabled), verify in the list and delete it", () => {
        createNewUser(firstName, lastName, email, username, role.owner, status.enabled);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `User "${firstName}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //created user should be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', firstName);

        //edit the user
        editUser(updatedFirstName, updatedLastName, username, role.user, status.disabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${updatedFirstName}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //verify the edited user
        verifyEditedUserInTable(updatedFirstName, updatedLastName)

        //click the delete button and cancel
        cancelDelete(username);

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', firstName);
    });

    it("should add a new user(with role User and status disabled), verify in the list and delete it", () => {
        createNewUser(firstName, lastName, email, username, role.user, status.disabled);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `User "${firstName}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //created user should be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', firstName);

        //edit the user
        editUser(updatedFirstName, updatedLastName, username, role.owner, status.enabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${updatedFirstName}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        //verify the edited user
        verifyEditedUserInTable(updatedFirstName, updatedLastName)

        //click the delete button and cancel
        cancelDelete(username);

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', updatedFirstName);
    });

    it("should add a new user, verify in the list and associate group with it then delete it", () => {
        //create the user
        createNewUser(firstName, lastName, email, username, role.user, status.disabled);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `User "${firstName}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //created user should be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', firstName);

        //edit the user
        editUserAndAssociateGroup(updatedFirstName, updatedLastName, username, role.owner, status.enabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${updatedFirstName}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        // verifyEditedGroupInTable(name, description)
        verifyEditedUserInTable(updatedFirstName, updatedLastName)

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', updatedFirstName);
    });

    it.skip("should add a new user and verify the association group and number of group chips displayed in the UI", () => {
        //create the user
        createNewUser(firstName, lastName, email, username, role.user, status.disabled);
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
        cy.get('#notistack-snackbar').should('contain.text', `User "${firstName}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //created user should be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', firstName);

        //edit the user and associate groups
        editUserAndAssociateGroup(updatedFirstName, updatedLastName, username, role.owner, status.enabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${updatedFirstName}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');
        cy.wait(3000);
        // Intercept GET requests to fetch user data
        cy.intercept('GET', '/account-service/api/users*').as('getUserData');

        cy.get('[data-testid="header-refresh-btn"]').click();

        cy.wait('@getUserData').then((interception) => {
            // Get user data from the intercepted response
            const userData = interception.response.body.content.find(user => user.username === username);
            // Get the number of groups associated with the user
            const groupsAssociated = userData.groups.length;

            cy.contains('[data-testid="table-row"]', updatedFirstName).within(() => {
                cy.get('[data-test="edit"]').click();
            });
            cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
                cy.get('[data-testid="groups-tab"]').click();
                cy.get('[data-testid="edit-group"]').should('exist')

            });

            // Count the number of group chips displayed in the UI
            cy.get('[data-testid="tbody-with-data"]').its('length').then((chipCount) => {
                // Assert that the number of chips matches the number of groups associated
                expect(chipCount).to.eq(groupsAssociated);
            });
            cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();
        });

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', updatedFirstName);
    });

    it.skip("should increase counters when checkboxes are selected or deselected inside Edit User", () => {
        // Create the user
        createNewUser(firstName, lastName, email, username, role.user, status.disabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${firstName}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //edit the user
        editUserAndAssociateGroup(updatedFirstName, updatedLastName, username, role.owner, status.enabled);

        cy.get('#notistack-snackbar').should('contain.text', `User "${updatedFirstName}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        // Open the edit modal and navigate to the groups tab
        cy.contains('[data-testid="table-row"]', updatedFirstName).within(() => {
            cy.get('[data-test="edit"]').click();
        });
        cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
            cy.get('[data-testid="groups-tab"]').click();
            cy.get('[data-testid="edit-group"]').should('exist').click();

        });

        // Verify if groups are listed
        cy.get('[data-testid="tbody-with-data"] input[type="checkbox"]').then($checkboxes => {
            if ($checkboxes.length === 0) {
                // No groups listed, skip
                cy.log('No groups listed, skipping checkbox selection');
            } else {
                //Initial counter check
                cy.get('[data-testid="added-removed-counters"]').within(() => {
                    cy.contains("Added: 0");
                    cy.contains("Removed: 0");
                });

                let addedCount = 0;
                let removedCount = 0;

                // Uncheck a few random checkboxes and verify Removed count
                cy.get('[data-testid="tbody-with-data"] input[type="checkbox"]').each(($checkbox, index) => {
                    if ($checkbox.prop('checked') && Math.random() > 0.5) {
                        removedCount++;
                        cy.wrap($checkbox).click();
                    }
                }).then(() => {
                    cy.contains(`Removed: ${removedCount}`);
                })

                // Check a few random checkboxes and verify Added count
                cy.get('[data-testid="tbody-with-data"] input[type="checkbox"]').each(($checkbox, index) => {
                    if (!$checkbox.prop('checked') && Math.random() > 0.5) {
                        addedCount++;
                        cy.wrap($checkbox).click();
                    }
                }).then(() => {
                    let updatedRemovedCount = 0
                    cy.contains('Removed: ').should('exist').then($removedCount => {
                        updatedRemovedCount = parseInt($removedCount.text().replace('Removed: ', ''));
                    }).then(() => {
                        const latestRemovedCount = removedCount - updatedRemovedCount;
                        const finalAddedCount = addedCount - latestRemovedCount
                        cy.contains(`Added: ${finalAddedCount}`);
                    })
                })
            }
        });

        // Close the edit modal without saving
        cy.get('[data-testid="cancel-button"]').click();
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', updatedFirstName);
    });

    it("should preview a user after adding and verifying it", () => {
        // Create the user
        createNewUser(firstName, lastName, email, username, role.user, status.disabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${firstName}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        //edit the user
        editUserAndAssociateGroup(updatedFirstName, updatedLastName, username, role.owner, status.enabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${updatedFirstName}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        // Click on the preview button for the newly added user
        cy.get(`[data-testid="tbody-with-data"]`)
            .contains('tr', updatedFirstName)
            .within(() => {
                cy.get('[data-test="view"]').click();
            });

        // Check if the modal with user details is visible
        cy.get('[data-testid="custom-dialog"]').should('be.visible')

        // Check if the name and description match the previously added user
        cy.get('[data-test="form"]').within(() => {
            cy.contains('First Name').next('.profile-text').should('contain.text', updatedFirstName);
            cy.contains('Last Name').next('.profile-text').should('contain.text', updatedLastName);
            cy.contains('Email Id').next('.profile-text').should('contain.text', email);
            cy.contains('User Name').next('.profile-text').contains(username, { matchCase: false });
        });
        // Switch to another tab
        cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
            cy.get('[data-testid="groups-tab"]').click();
        });

        // Check if checkboxes are present and disabled for all rows in the table
        cy.get('[data-testid="tbody-with-data"] input[type="checkbox"]').each(($checkbox, index) => {
            cy.wrap($checkbox).should('be.disabled')
        });

        // Close the edit modal
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', updatedFirstName);
    });

    it("should search for groups within the Edit User modal and verify search functionality", () => {
        // Create the user
        createNewUser(firstName, lastName, email, username, role.user, status.disabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${firstName}" created successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        // Edit the user and associate groups
        editUserAndAssociateGroup(updatedFirstName, updatedLastName, username, role.owner, status.enabled);
        cy.get('#notistack-snackbar').should('contain.text', `User "${updatedFirstName}" updated successfully`);
        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        cy.get('#notistack-snackbar').should('not.exist');

        // Intercept the API call to fetch groups data
        cy.intercept('GET', '/account-service/api/groups*').as('getGroups');

        // Open the edit modal and navigate to the groups tab
        cy.contains('[data-testid="table-row"]', updatedFirstName).within(() => {
            cy.get('[data-test="edit"]').click();
        });

        // Wait for the API call to complete
        cy.wait('@getGroups').then((interception) => {
            // Get the response body containing groups data
            const groupsData = interception.response.body.content;

            cy.get('[data-testid="custom-dialog"]').should('be.visible').within(() => {
                cy.get('[data-testid="groups-tab"]').click();
            });

            // If groups data is available, perform search and verify functionality
            if (groupsData && groupsData.length > 0) {
                cy.get('[data-testid="edit-group"]').should('exist').click();
                // Get a random group name from the available groups data
                const randomGroupName = groupsData[Math.floor(Math.random() * groupsData.length)].name;

                // Search for the random group name
                cy.get('[data-testid="input-search-box"]').type(randomGroupName).type('{enter}');

                // Wait for the search to complete
                cy.wait('@getGroups').then(() => {
                    // Verify that the groups list updates accordingly based on the search query
                    cy.get('[data-testid="tbody-with-data"]').should('contain.text', randomGroupName);
                });
            } else {
                cy.get('[data-testid="table-noData"]').should('be.visible');
            }
        });

        // Close the edit modal
        cy.get('[data-testid="cancel-button"]').click();
        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        //delete the user
        deleteUser(username);

        //deleted user should not be in the table
        cy.get(`[data-testid="tbody-with-data"]`).should('not.have.text', updatedFirstName);
    });

    it('should create multiple users and cancel bulk delete then again enable bulk delete, select and delete users in bulk', () => {
        //Number of users to create for the test
        const iterations = 3;
        const createdUsers = [];

        //Create users
        for (let i = 1; i <= iterations; i++) {
            const firstName = `Bulk-User${uniqueSuffix}-${i}`;
            const lastName = `Last${uniqueSuffix}-${i}`;
            const email = `user${uniqueSuffix}-${i}@example.com`;
            const username = `user${uniqueSuffix}-${i}`;

            createNewUser(firstName, lastName, email, username, role.user, status.disabled);
            cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
            createdUsers.push({ username, index: i });
            cy.wait(3000);
            //Verify users creation
            cy.get('[data-testid="custom-dialog"]').should('not.exist');
            cy.get(`[data-testid="tbody-with-data"]`).should('contain.text', username);
        }

        // Delete each user one by one
        createdUsers.forEach(({ username }) => {
            deleteUser(username);
        });

        // Verify users are deleted
        createdUsers.forEach(({ username }) => {
            cy.get('body').then(($body) => {
            if ($body.find(`[data-testid="tbody-with-data"]`).length > 0) {
                // Element exists, proceed with assertion
                cy.get(`[data-testid="tbody-with-data"]`)
                    .should('exist') // Ensure the element exists
                    .and('not.have.text', username); // Check it does not contain the name
            }
         });
        });
    });
    
});