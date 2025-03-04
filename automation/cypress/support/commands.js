// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
Cypress.Commands.add('login', (username, password) => {
    console.log('Browser', Cypress.browser);
    cy.clearSession();
    cy.visit("/");

    if (Cypress.env('isLocal')) {
        let login = Cypress.env('login');
        console.log('login', login);

        cy.get("#userName").type(login.username);
        cy.get("#password").type(login.password);
        cy.get("#kc-form-buttons").click();
        cy.url().should("include", "/dashboard");
    }
});

Cypress.Commands.add('clearSession', () => {
    cy.clearAllLocalStorage();
    cy.clearAllSessionStorage();
    cy.clearAllCookies();
})