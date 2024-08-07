import configData from "../../fixtures/config.json";
import DashboardUtils from "../../../app/utils/dashboard_utils";

describe("Dashboard Test", () => {
  function login() {
    cy.visit("/");
    cy.get("#email").type(configData.login.email);
    cy.get("#password").type(configData.login.password);
    cy.get("#kc-login").click();
    cy.url().should("include", "/dashboard");
  }

  it("should verify Sensitive Data Accessed in Application's graph data on dashboard", () => {
    login();
    cy.url().should("include", "/dashboard");
    // cy.get('#page-title').should('contain.text', 'Dashboard');

    cy.get("#sensitive-data-title").should(
      "contain.text",
      "Sensitive Data Accessed in Applications"
    );

    cy.request(
      "/data-service/api/shield_audits/count?groupBy=traits,applicationName"
    ).then((response) => {
      expect(response.status).to.eq(200);

      if (response.body.traits) {
        DashboardUtils.formatSensitiveDataInApplications(response.body).map(
          (trait, i) => {
            cy.get(`.MuiTableBody-root .MuiTableRow-root`)
              .eq(i)
              .find(".MuiTableCell-root .MuiChip-root")
              .should("contain", trait.tag);

            cy.get(`.MuiTableBody-root .MuiTableRow-root`)
              .eq(i)
              .find(".MuiTableCell-root")
              .should("contain", trait.queries);

            cy.get(`.MuiTableBody-root .MuiTableRow-root  `)
              .eq(i)
              .find(
                `.MuiTableCell-root .highcharts-container .highcharts-root .highcharts-series-group .highcharts-bar-series .highcharts-point `
              )
              .should("have.length", trait.graphData.length + 1);
          }
        );
      } else {
        cy.get('[data-testid="noData"] > .MuiTypography-root').should(
          "contain.text",
          "No data to display"
        );
      }
    });
  });
});
