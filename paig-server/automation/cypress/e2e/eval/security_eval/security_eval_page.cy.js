


describe('Evaluation Config Main Tabs', () => {
    before(() => {
        cy.login();
    });

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/eval_configs');
    });

    it('should display the Configuration and Endpoints tabs', () => {
        // Check if the Configuration tab is present
        cy.get('[data-testid="eval-config-tab"]').should('exist').and('contain.text', 'CONFIGURATION');

        // Check if the Endpoints tab is present
        cy.get('[data-testid="eval-endpoint-tab"]').should('exist').and('contain.text', 'ENDPOINTS');
    });

    it('should click on Configuration tab and check if table exists', () => {
        // Click on the Configuration tab
        cy.get('[data-testid="eval-config-tab"]').click();

        // Check if the table exists
        cy.get('table').should('exist');
         //verify table headers
         cy.get('[data-testid="thead"] th').eq(0).should('contain.text', 'Name');
         cy.get('[data-testid="thead"] th').eq(1).should('contain.text', 'Applications');
         cy.get('[data-testid="thead"] th').eq(2).should('contain.text', 'Evaluation Purpose');
         cy.get('[data-testid="thead"] th').eq(3).should('contain.text', 'Created');
         cy.get('[data-testid="thead"] th').eq(4).should('contain.text', 'Created By');
         cy.get('[data-testid="thead"] th').eq(5).should('contain.text', 'Runs');
         cy.get('[data-testid="thead"] th').eq(6).should('contain.text', 'Actions');
    });

    it('should click on Endpoint tab and check if table exists', () => {
        // Click on the Configuration tab
        cy.get('[data-testid="eval-endpoint-tab"]').click();

        // Check if the table exists
        cy.get('table').should('exist');
         //verify table headers
        cy.get('[data-testid="thead"] th').eq(0).should('contain.text', 'Name');
        cy.get('[data-testid="thead"] th').eq(1).should('contain.text', 'Details');
        cy.get('[data-testid="thead"] th').eq(2).should('contain.text', 'Actions');

        // Click on the "Add New" button
        cy.get('[data-test="add-btn"]').click();

        // Fill out the form
        cy.get('[data-testid="name-input"]').should('exist').then(($input) => {
            const randomName = `Endpoint_${Math.random().toString(36).substring(2, 10)}`;
            cy.wrap($input).clear().type(randomName).invoke('val').then((value) => {
                cy.wrap(value).as('storedValue');
            });
        });   cy.get('[data-testid="endpoint-url"]').type('http://127.0.0.1:3535/securechat/api/v1/conversations/prompt');
        cy.get('[data-testid="method"]').click();
        cy.get('[role="option"]').contains('POST').click();
        cy.get('[data-testid="name-input-username"]').type('New Username');
        cy.get('[data-testid="request-body"]').type('{"ai_application_name": "sales_model","prompt": "prompt"}', { parseSpecialCharSequences: false });
        cy.get('[data-testid="response-transform"]').type('json.messages && json.messages.length > 0 ? (json.messages.find(message => message.type === "reply") || {}).content || "No reply found." : "No response from the server."');
        // Click the submit button
        cy.get('[data-test="modal-ok-btn"]').click().debug();

        // Verify the new entry is added to the table
        cy.get('@storedValue').then((storedValue) => {
            cy.get('table').contains('td', storedValue).should('exist');
        });

        });

    after(() => {
        cy.clearSession();
    });
    
})