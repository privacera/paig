import commonUtils from "../common/common_utils";

const name = 'guardrails' + '_' + commonUtils.generateRandomSentence(10, 5);
const description = commonUtils.generateRandomSentence(15, 5);

describe('Guardrail Connection Provider', () => {
    before(() => {
        cy.login();
    });

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/guardrail_connection_provider');
    });

    after(() => {
        cy.clearSession();
    });

    it('should render guardrail aws connected provider listing page', () => {
        cy.visit('/#/guardrail_connection_provider/AWS');

        cy.get('[data-testid="connection-header"]').should('be.visible').and('contain', 'AWS Bedrock');

        cy.get('[data-testid="add-connection-btn"]').should('be.visible').and('contain', 'ADD CONNECTION');

        cy.intercept('GET', 'guardrail-service/api/connection?size=15&guardrailsProvider=AWS').as('getGuardrailConnectionProvider');

        cy.wait(3000);

        cy.get('[data-testid="header-refresh-btn"]').should('be.visible').click();

        cy.wait('@getGuardrailConnectionProvider').then((interception) => {
            expect(interception.response.statusCode).to.eq(200);

            cy.get('[data-test="table"]').within(() => {
                cy.get('[data-testid="loader"]').should('not.exist');
            });

            const responseData = interception.response.body;

            cy.get('[data-testid="thead"]').within(() => {
                cy.get('th').eq(0).should('contain', 'Name');
                cy.get('th').eq(1).should('contain', 'Description');
                cy.get('th').eq(2).should('contain', 'Action');
            });

            if (responseData.content.length === 0) {
                cy.get('[data-testid="table-noData"]').should('be.visible').and('contain', 'No guardrails provider connection');
            } else {
                responseData.content.forEach((item, index) => {
                    cy.get('[data-testid="table-row"]').eq(index).within(() => {
                        cy.get('td').eq(0).should('contain', item.name);
                        cy.get('td').eq(1).should('contain', item.description);
                        cy.get('td').eq(2).within(() => {
                            cy.get('[data-test="edit"]').should('be.visible');
                            cy.get('[data-test="delete"]').should('be.visible');
                        });
                    });
                });
            }
        });
    });

    it('validate aws provider form for validation error', () => {
        cy.visit('/#/guardrail_connection_provider/AWS');

        cy.get('[data-testid="add-connection-btn"]').click();

        cy.get('[data-testid="customized-dialog-title"]').contains('Add Connection');

        cy.get('[data-testid="connector-name"]').should('be.visible').and('contain', 'AWS Bedrock');

        cy.wait(1000);

        // Click on the save button
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click();

        // Check for validation errors
        cy.get('[data-testid="name"]').should('be.visible').and('contain', 'Required!');

        cy.get('[data-testid="config-type"]').should('be.visible').find('input').eq(0).should('have.value', 'IAM_ROLE').and('be.checked');
        cy.get('[data-testid="iam-role"]').should('be.visible').and('contain', 'Required!');
        cy.get('[data-testid="region"]').should('be.visible').and('contain', 'Required!');
        cy.get('[data-testid="access-key"]').should('not.exist');
        cy.get('[data-testid="secret-key"]').should('not.exist');
        cy.get('[data-testid="session-token"]').should('not.exist');

        // Enter the name
        cy.get('[data-testid="name"]').find('input').type('Test Connection');
        cy.get('[data-testid="name"]').should('not.contain', 'Required!');

        // Enter the IAM Role
        cy.get('[data-testid="iam-role"]').find('input').type('arn:aws:iam::123456789012:role/role-name');
        cy.get('[data-testid="iam-role"]').should('not.contain', 'Required!');

        // Enter the region
        cy.get('[data-testid="region"]').find('input').type('us-east-1');
        cy.get('[data-testid="region"]').should('not.contain', 'Required!');

        cy.get('[data-testid="config-type"]').should('be.visible').find('input').eq(1).click();
        cy.get('[data-testid="config-type"]').should('be.visible').find('input').eq(1).should('have.value', 'ACCESS_SECRET_KEY').and('be.checked');

        // Click on the save button
        cy.get('[data-test="modal-ok-btn"]').contains('Save').click();

        cy.get('[data-testid="iam-role"]').should('not.exist');
        cy.get('[data-testid="access-key"]').should('be.visible').and('contain', 'Required!');
        cy.get('[data-testid="secret-key"]').should('be.visible').and('contain', 'Required!');
        cy.get('[data-testid="session-token"]').should('be.visible').and('not.contain', 'Required!');
        cy.get('[data-testid="region"]').should('exist');

        cy.get('[data-testid="config-type"]').should('be.visible').find('input').eq(2).click();
        cy.get('[data-testid="config-type"]').should('be.visible').find('input').eq(2).should('have.value', 'INSTANCE_ROLE').and('be.checked');

        cy.get('[data-testid="iam-role"]').should('not.exist');
        cy.get('[data-testid="region"]').should('not.exist');
        cy.get('[data-testid="access-key"]').should('not.exist');
        cy.get('[data-testid="secret-key"]').should('not.exist');
        cy.get('[data-testid="session-token"]').should('not.exist');

        cy.get('.Mui-error').should('not.exist');

        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        // Check that the dialog is closed
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
    });

    it('should be able to add a new AWS connection provider', () => {
        cy.visit('/#/guardrail_connection_provider/AWS');

        cy.get('[data-testid="add-connection-btn"]').click();

        cy.intercept('POST', 'guardrail-service/api/connection').as('addGuardrailConnectionProvider');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="customized-dialog-title"]').contains('Add Connection');

            // Enter the name
            cy.get('[data-testid="name"]').find('input').type(name);

            // Enter the description
            cy.get('[data-testid="description"]').within(() => {
                cy.get('[data-testid="input-field"]').type(description);
            });

            // Enter the IAM Role
            cy.get('[data-testid="iam-role"]').find('input').type('arn:aws:iam::123456789012:role/role-name');

            // Enter the region
            cy.get('[data-testid="region"]').find('input').type('us-east-1');

            // Click on the save button
            cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        });

        cy.wait('@addGuardrailConnectionProvider').then((interception) => {
            expect(interception.response.statusCode).to.eq(201);

            cy.get('[data-testid="custom-dialog"]').should('not.exist');

            cy.get('[data-testid="snackbar"]').should('contain', 'added successfully');

            cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();

            cy.get('[data-testid="tbody-with-data"]').should('exist');
            cy.get('[data-testid="table-row"]').should('have.length.greaterThan', 0);
        });
    });

    it('should be able to edit a new AWS connection provider', () => {
        cy.visit('/#/guardrail_connection_provider/AWS');

        cy.intercept('GET', 'guardrail-service/api/connection?size=15&guardrailsProvider=AWS').as('getGuardrailConnectionProvider');

        cy.wait(3000);

        cy.get('[data-testid="header-refresh-btn"]').should('be.visible').click();

        cy.wait('@getGuardrailConnectionProvider').then((interception) => {
            expect(interception.response.statusCode).to.eq(200);

            cy.get('[data-test="table"]').within(() => {
                cy.get('[data-testid="loader"]').should('not.exist');
            });

            const responseData = interception.response.body;

            expect(responseData.content.length).to.be.greaterThan(0);

            // find new added connection from table
            const index = responseData.content.findIndex((item) => item.name === name);

            expect(index).to.be.greaterThan(-1);

            cy.get('[data-testid="table-row"]').eq(index).within(() => {
                cy.get('[data-test="edit"]').click();
            });

            cy.intercept('PUT', 'guardrail-service/api/connection/*').as('updateGuardrailConnectionProvider');

            cy.get('[data-testid="custom-dialog"]').within(() => {
                cy.get('[data-testid="customized-dialog-title"]').contains('Edit Connection');

                // Enter the name
                cy.get('[data-testid="name"]').find('input').type(' - Updated');

                // check current selected Connection Type
                cy.get('[data-testid="config-type"]').should('be.visible').find('input').eq(0).should('have.value', 'IAM_ROLE').and('be.checked');

                // Click on the save button
                cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
            })

            cy.wait('@updateGuardrailConnectionProvider').then((interception) => {
                expect(interception.response.statusCode).to.eq(200);

                cy.get('[data-testid="custom-dialog"]').should('not.exist');

                cy.get('[data-testid="snackbar"]').should('contain', 'updated successfully');

                cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();

                cy.get('[data-testid="tbody-with-data"]').should('exist');
                cy.get('[data-testid="table-row"]').should('have.length.greaterThan', 0);
            });
        });
    });

    it('should be able to delete a new AWS connection provider', () => {
        cy.visit('/#/guardrail_connection_provider/AWS');

        cy.intercept('GET', 'guardrail-service/api/connection?size=15&guardrailsProvider=AWS').as('getGuardrailConnectionProvider');

        cy.wait(3000);

        cy.get('[data-testid="header-refresh-btn"]').should('be.visible').click();

        cy.wait('@getGuardrailConnectionProvider').then((interception) => {
            expect(interception.response.statusCode).to.eq(200);

            cy.get('[data-test="table"]').within(() => {
                cy.get('[data-testid="loader"]').should('not.exist');
            });

            const responseData = interception.response.body;

            expect(responseData.content.length).to.be.greaterThan(0);

            // find new added connection from table
            const index = responseData.content.findIndex((item) => item.name.includes(name));

            expect(index).to.be.greaterThan(-1);

            cy.get('[data-testid="table-row"]').eq(index).within(() => {
                cy.get('[data-test="delete"]').click();
            });
        });

        cy.get('[data-testid="custom-dialog"]').should('exist');

        cy.intercept('DELETE', 'guardrail-service/api/connection/*').as('deleteGuardrailConnectionProvider');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="confirm-dialog-title"]').should('be.visible').contains('Confirm Delete');

            cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete ${name} - Updated connection?`);

            cy.get('[data-test="confirm-yes-btn"]').should('be.visible').contains('Delete').click();
        });

        cy.wait('@deleteGuardrailConnectionProvider').then((interception) => {
            expect(interception.response.statusCode).to.eq(204);

            cy.get('[data-testid="custom-dialog"]').should('not.exist');

            cy.get('[data-testid="snackbar"]').should('contain', 'deleted successfully');

            cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();

            cy.get('[data-testid="tbody-with-data"]').should('exist');
        });
    });
})