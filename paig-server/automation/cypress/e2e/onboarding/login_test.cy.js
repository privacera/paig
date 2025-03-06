
describe("Positive test cases for login page", () => {
  const login = Cypress.env('login');

  beforeEach(() => {
    cy.visit("/");
  });

  after(() => {
    cy.clearSession();
  });

  it("should be on the login page ", () => {
    cy.url().should("include", "/login");
    cy.get("#kc-page-title").should("contain.text", "Login");
    cy.get("form").should("exist");
  });

  it("should successfully login ", () => {
    cy.get("#userName").type(login.username);
    cy.get("#password").type(login.password);
    cy.get("#kc-form-buttons").click();
    cy.url().should("include", "/dashboard");
  });
});

describe("Negative test cases for login page", () => {
  const login = Cypress.env('login');
  const invalidCred = Cypress.env('invalidCred');

  beforeEach(() => {
    cy.visit("/");
  });

  after(() => {
    cy.clearSession();
  });

  it("should trigger browser validation for empty username and password", () => {
    cy.get('#userName').clear();
    cy.get("#password").clear();
    cy.get("#kc-form-buttons").click();
    cy.get('#userName:invalid') // Check for invalid input state
    .should('have.length', 1);
    cy.get('#password:invalid') // Check for invalid input state
    .should('have.length', 1);
  });

  it('should trigger browser validation for empty username', () => {
    cy.get('#userName').clear();
    cy.get("#kc-form-buttons").click();
    cy.get('#userName:invalid') // Check for invalid input state
    .should('have.length', 1);
  });

  it("should trigger browser validation for empty password", () => {
    cy.get("#password").clear();
    cy.get("#kc-form-buttons").click();
    cy.get('#password:invalid') // Check for invalid input state
    .should('have.length', 1);
  });

  it("should show error message when we enter invalid credentials in fields", () => {
    cy.get("#userName").type(invalidCred.username);
    cy.get("#password").type(invalidCred.password);
     cy.get("#kc-form-buttons").click();
    cy.get("#login-page-error-box").contains(
      "Invalid user credentials"
    );
  });
});
