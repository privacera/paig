


describe('Evaluation Report Main Tab', () => {
    before(() => {
        cy.login();
    });

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/eval_reports');
    });
    it('should click on Report tab and check if table exists', () => {
        // Check if the table exists
        cy.get('table').should('exist');
         //verify table headers
         cy.get('[data-testid="thead"] th').eq(0).should('contain.text', 'Report Name');
         cy.get('[data-testid="thead"] th').eq(1).should('contain.text', 'Eval');
         cy.get('[data-testid="thead"] th').eq(2).should('contain.text', 'Applications');
         cy.get('[data-testid="thead"] th').eq(3).should('contain.text', 'Report Status');
         cy.get('[data-testid="thead"] th').eq(4).should('contain.text', 'Score');
         cy.get('[data-testid="thead"] th').eq(5).should('contain.text', 'Created');
         cy.get('[data-testid="thead"] th').eq(6).should('contain.text', 'Actions');
        });

    after(() => {
        cy.clearSession();
    });
    
})