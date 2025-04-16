import commonUtils from "../common/common_utils";

const name = 'guardrails' + '_' + commonUtils.generateRandomSentence(10, 5);
const description = commonUtils.generateRandomSentence(15, 5);
const responseTemplateData = {
    name,
    description,
    updateName: name + ' - Updated',
    updateDescription: description + ' - Updated'
}

describe('Guardrail Response Template', () => {
    before(() => {
        cy.login();
    });

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/response_templates');
    });

    after(() => {
        cy.clearSession();
    });

    it('should display the response template listing with search, add button and table', () => {
        cy.get('[data-testid="response-template-search"]').should('be.visible').and('have.attr', 'placeholder', 'Search Response Template');
        cy.get('[data-testid="add-response-template-btn"]').should('be.visible').and('contain', 'Create Template');
        cy.get('[data-test="table"]').should('be.visible');
    });

    it('should verify predefined templates have disabled action buttons', () => {
        cy.wait(5000);

        // Intercept the listing API
        cy.intercept('GET', 'guardrail-service/api/response_templates?size=15').as('getResponseTemplates');

        // Click on the refresh button
        cy.get('[data-testid="header-refresh-btn"]').click();

        // Wait for the API call to complete
        cy.wait('@getResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            const {content} = interception.response.body;
            
            // Find any predefined templates
            content.forEach((item, index) => {
                if (item.type === 'SYSTEM_DEFINED') {
                    cy.get('[data-testid="table-row"]').eq(index).within(() => {
                        // Verify edit button is disabled
                        cy.get('[data-testid="edit-response-template"]').should('be.disabled');                        
                        
                        cy.get('[data-testid="delete-response-template"]').should('be.disabled');

                        // Verify tooltips by checking the title attribute
                        cy.get('[data-testid="edit-response-template"]').parent().should('have.attr', 'title', 'Predefined template cannot be edited');
                        
                        cy.get('[data-testid="delete-response-template"]').parent().should('have.attr', 'title', 'Predefined template cannot be deleted');
                    });
                }
            });
        });
    });

    it('should allow searching for response templates if any exist', () => {
        cy.wait(5000);

        // Intercept the listing API
        cy.intercept('GET', 'guardrail-service/api/response_templates?size=15').as('getResponseTemplates');

        // Click on the refresh button
        cy.get('[data-testid="header-refresh-btn"]').click();

        // Wait for the API call to complete
        cy.wait('@getResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            // Check the response data
            const responseData = interception.response.body;

            cy.get('[data-testid="thead"]').within(() => {
                cy.get('th').eq(0).should('contain', 'Response');
                cy.get('th').eq(1).should('contain', 'Description');
                cy.get('th').eq(2).should('contain', 'Actions');
            });

            if (responseData.content.length === 0) {
                cy.get('[data-testid="table-noData"]').should('be.visible').and('contain', 'No response template created');
            } else {
                responseData.content.forEach((item, index) => {
                    cy.get('[data-testid="table-row"]').eq(index).within(() => {
                        cy.get('td').eq(0).should('contain', item.response);
                        cy.get('td').eq(1).should('contain', item.description);
                        cy.get('td').eq(2).within(() => {
                            if (item.type === 'SYSTEM_DEFINED') {
                                cy.get('[data-testid="edit-response-template"]').should('be.disabled');
                                cy.get('[data-testid="delete-response-template"]').should('be.disabled');
                            } else {
                                cy.get('[data-testid="edit-response-template"]').should('be.visible').and('not.be.disabled');
                                cy.get('[data-testid="delete-response-template"]').should('be.visible').and('not.be.disabled');
                            }
                        });
                    });
                });
            }
        });
    });

    it('should check validation for creating a new response template', () => {
        cy.get('[data-testid="add-response-template-btn"]').click();

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="customized-dialog-title"]').contains('Add Response Template');

            // Click on the save button
            cy.get('[data-test="modal-ok-btn"]').contains('Save').click();

            // Enter the response template name
            cy.get('[data-testid="response-template"]').within(() => {
                // Check for validation errors
                // cy.get('.Mui-error').should('contain.text', 'Required');

                cy.get('[data-testid="response"]').type(responseTemplateData.name)
                // cy.get('.Mui-error').should('not.exist');

                // Clear the response field
                cy.get('[data-testid="response"]').clear();
                // cy.get('.Mui-error').should('contain.text', 'Required');
            })

            // Click on the cancel button
            cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();
        });

        // Check that the dialog is closed
        cy.get('[data-testid="custom-dialog"]').should('not.exist');
    });

    it('should allow creating a new response template', () => {
        cy.get('[data-testid="add-response-template-btn"]').click();

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            // Enter the same metadata name
            cy.get('[data-testid="response"]').type(responseTemplateData.name);

            // Enter the metadata description
            cy.get('[data-testid="description"]').type(responseTemplateData.description);

            // Click on the save button
            cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        });

        cy.wait(2000);
        cy.get('[data-testid="snackbar"]').should('contain', 'added successfully');

        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
    });

    it('should allow search and editing a response template', () => {
        // Intercept the listing API
        cy.intercept('GET', 'guardrail-service/api/response_templates?size=15&response=*').as('getResponseTemplates');

        cy.wait(2000);

        // search for the response template
        cy.get('[data-testid="response-template-search"]').type(responseTemplateData.name).type('{enter}');

        // Wait for the API call to complete
        cy.wait('@getResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            const {content} = interception.response.body;
            expect(content.length).to.be.greaterThan(0);

            // check table row length equal to content length
            cy.get('[data-testid="table-row"]').should('have.length', content.length);

            // Check that the updated response template is displayed using content and loop through the content
            content.forEach((item, index) => {
                if (item.response === responseTemplateData.name) {
                    cy.get('[data-testid="table-row"]').eq(index).within(() => {
                        // Skip editing if it's a system-defined template
                        if (item.type === 'SYSTEM_DEFINED') {
                            cy.get('[data-testid="edit-response-template"]').should('be.disabled');
                            return;
                        }
                        cy.get('[data-testid="edit-response-template"]').should('be.visible').and('not.be.disabled').click();
                    });
                }
            });
        });

        // Only proceed with edit if we found a non-system-defined template
        cy.get('[data-testid="custom-dialog"]').then(($dialog) => {
            if ($dialog.length > 0) {
                cy.get('[data-testid="custom-dialog"]').within(() => {
                    cy.get('[data-testid="customized-dialog-title"]').contains('Edit Response Template');

                    cy.get('[data-testid="response"]').should('have.value', responseTemplateData.name);
                    cy.get('[data-testid="description"]').should('have.value', responseTemplateData.description);

                    // Update the response template name
                    cy.get('[data-testid="response"]').type(' - Updated');

                    // Enter the description
                    cy.get('[data-testid="description"]').clear().type(responseTemplateData.description + ' - Updated');

                    // Click on the save button
                    cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
                });

                cy.wait(2000);

                cy.get('[data-testid="snackbar"]').should('contain', 'updated successfully');

                cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();

                // Check that the dialog is closed
                cy.get('[data-testid="custom-dialog"]').should('not.exist');
            }
        });
    });

    it('should search for existing data, then search for non-existent data and click refresh', () => {
        // Intercept the listing API for existing data
        cy.intercept('GET', 'guardrail-service/api/response_templates?size=15').as('getResponseTemplates');

        // Click on the refresh button
        cy.get('[data-testid="header-refresh-btn"]').click();

        // Wait for the API call to complete
        cy.wait('@getResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            const { content, totalElements} = interception.response.body;
            expect(content.length).to.be.greaterThan(0);

            cy.get('[data-testid="template-header"]').should('be.visible').and('contain', `Templates (${totalElements})`);

            // Check that the response template is displayed
            cy.get('[data-testid="table-row"]').should('have.length', content.length);
        });

        // Intercept the listing API for non-existent data
        cy.intercept('GET', 'guardrail-service/api/response_templates?size=15&response=nonexistent').as('getNonExistentResponseTemplates');

        // Search for a non-existent response template
        cy.get('[data-testid="response-template-search"]').clear().type('nonexistent');

        // Click on the refresh button
        cy.get('[data-testid="header-refresh-btn"]').click();

        // Wait for the API call to complete
        cy.wait('@getNonExistentResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            const { content, totalElements} = interception.response.body;

            expect(content.length).to.eq(0);

            cy.get('[data-testid="template-header"]').should('be.visible').and('contain', `Templates (${totalElements})`);

            // Check that the no data message is displayed
            cy.get('[data-testid="table-noData"]').should('be.visible').and('contain', 'No response template created');
        });

        // Search for the existing response template again
        cy.get('[data-testid="response-template-search"]').clear();

        // Click on the refresh button
        cy.get('[data-testid="header-refresh-btn"]').click();

        // Wait for the API call to complete
        cy.wait('@getResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            const { content, totalElements } = interception.response.body;
            expect(content.length).to.be.greaterThan(0);

            cy.get('[data-testid="template-header"]').should('be.visible').and('contain', `Templates (${totalElements})`);

            // Check that the response template is displayed
            cy.get('[data-testid="table-row"]').should('have.length', content.length);
        });
    });

    it('should allow deleting a response template', () => {
        cy.intercept('GET', 'guardrail-service/api/response_templates?size=15&response=*').as('getResponseTemplates');

        cy.wait(2000);

        // search for the response template
        cy.get('[data-testid="response-template-search"]').type(responseTemplateData.name).type('{enter}');

        // Wait for the API call to complete
        cy.wait('@getResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            const {content} = interception.response.body;
            expect(content.length).to.be.greaterThan(0);

            // check table row length equal to content length
            cy.get('[data-testid="table-row"]').should('have.length', content.length);

            cy.get('[data-testid="table-row"]').filter(`:contains(${responseTemplateData.updateName})`).find('[data-testid="delete-response-template"]').should('be.visible').click();

            cy.get('[data-testid="custom-dialog"]').should('exist');

            cy.get('[data-testid="custom-dialog"]').within(() => {
                cy.get('[data-testid="confirm-dialog-title"]').should('be.visible').contains('Confirm Delete');

                cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete ${responseTemplateData.updateName} response template?`);

                cy.get('[data-test="confirm-yes-btn"]').should('be.visible').contains('Delete').click();
            });

            cy.wait(2000);

            cy.get('[data-testid="snackbar"]').should('contain', 'deleted successfully');

            cy.get('[data-testid="snackbar-close-btn"]').should('exist').click();
        });
    });

    // test case to search for a response template that does not exist
    it('should display no data message when searching for a non-existent response template', () => {
        // Intercept the listing API
        cy.intercept('GET', 'guardrail-service/api/response_templates?size=15&response=nonexistent').as('getNonExistentResponseTemplates');

        // Search for a non-existent response template
        cy.get('[data-testid="response-template-search"]').type('nonexistent').type('{enter}');

        // Wait for the API call to complete
        cy.wait('@getNonExistentResponseTemplates').then((interception) => {
            // Check that the loader is no longer visible
            cy.get('[data-testid="loader"]').should('not.exist');

            // response status code
            expect(interception.response.statusCode).to.eq(200);

            // Check the response data
            const responseData = interception.response.body;
            expect(responseData.content.length).to.eq(0);

            // Check that the no data message is displayed
            cy.get('[data-testid="table-noData"]').should('be.visible').and('contain', 'No response template created');
        });
    });
});