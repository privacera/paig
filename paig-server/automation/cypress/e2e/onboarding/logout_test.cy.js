describe("Test logout", () => {
  it("should successfully logout after logging in", () => {
    const login = Cypress.env('login');

    cy.visit("/");
    cy.get("#userName").type(login.username);
    cy.get("#password").type(login.password);
    cy.get("#kc-form-buttons").click();
    cy.url().should("include", "/dashboard");

    cy.get('.MuiButton-label').click();
    cy.get('[data-testid="logout"]')
      .should('be.visible') // Ensure the element is visible
      .click();
    cy.url().should("include", "/login");
  });

//  it("should redirect to login page if tried to navigate to any index.html page", () => {
//    cy.visit("/#/dashboard");
//    cy.url().should("include", "/login#/dashboard");
//  });
});