describe('Guardrail Listing', () => {
    before(() => {
        cy.login();
    });

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/guardrails');
    });

    after(() => {
        cy.clearSession();
    });

    it('should display the guardrail listing with search, add button and table', () => {
        //cy.get('[data-testid="guardrail-header"]').should('be.visible').and('contain', `Guardrails (${totalElements})`);
        cy.get('[data-testid="guardrail-search"]').should('be.visible').and('have.attr', 'placeholder', 'Search Guardrail');
        cy.get('[data-testid="add-guardrail-btn"]').should('be.visible').and('contain', 'Create Guardrail');
        cy.get('[data-test="table"]').should('be.visible');
    });

    it('should refresh and validate guardrail listing', () => {
        cy.wait(5000);

        cy.intercept('GET', 'guardrail-service/api/guardrail?size=15').as('getGuardrails');

        cy.get('[data-testid="header-refresh-btn"]').click();

        cy.wait('@getGuardrails').then((interception) => {
            cy.get('[data-testid="loader"]').should('not.exist');

            expect(interception.response.statusCode).to.eq(200);

            let {totalElements, content} = interception.response.body;

            cy.get('[data-testid="guardrail-header"]').should('be.visible').and('contain', `Guardrails (${totalElements})`);

            cy.get('[data-testid="thead"]').within(() => {
                cy.get('th').eq(0).should('contain', 'Name');
                cy.get('th').eq(1).should('contain', 'Description');
                cy.get('th').eq(2).should('contain', 'Guardrail Providers');
                cy.get('th').eq(3).should('contain', 'Actions');
            });

            if (content.length === 0) {
                cy.get('[data-testid="table-noData"]').should('be.visible').and('contain', 'No guardrails created');
            } else {
                content.forEach((item, index) => {
                    cy.get('[data-testid="table-row"]').eq(index).within(() => {
                        cy.get('td').eq(0).should('contain', item.name);
                        cy.get('td').eq(1).should('contain', item.description || '');
                        cy.get('td').eq(2).should('not.be.empty');
                        cy.get('td').eq(3).within(() => {
                            cy.get('[data-test="edit"]').should('be.visible');
                            cy.get('[data-test="delete"]').should('be.visible');
                        });
                    });
                });
            }
        })
    });

    it('should search and check api sending correct params', () => {
        cy.intercept('GET', 'guardrail-service/api/guardrail?size=15&name=*').as('getGuardrails');

        cy.get('[data-testid="guardrail-search"]').type('search non existing data');

        cy.get('[data-testid="header-refresh-btn"]').click();

        cy.wait('@getGuardrails').then((interception) => {
            cy.get('[data-testid="loader"]').should('not.exist');

            expect(interception.response.statusCode).to.eq(200);

            expect(interception.request.url).to.include('name=search+non+existing+data');

            let {totalElements} = interception.response.body;

            expect(totalElements).to.eq(0);

            cy.get('[data-testid="guardrail-header"]').should('be.visible').and('contain', `Guardrails (${totalElements})`);

            cy.get('[data-testid="table-noData"]').should('be.visible').and('contain', 'No guardrails created');
        })
    });

    it('should go to guardrail create page', () => {
        cy.get('[data-testid="add-guardrail-btn"]').click();

        //check url to redirect to add guardrail page
        cy.url().should('include', '/guardrails/create');
    });
})