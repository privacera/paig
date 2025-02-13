import commonUtils from "../common/common_utils";

const name = 'guardrails' + '_' + commonUtils.generateRandomSentence(5, 5);

describe('Guardrail Form PAIG provider', () => {
    before(() => {
        cy.login();
    });

    beforeEach(() => {
        cy.visit('/#/dashboard');
        cy.visit('/#/guardrails/create');
    });

    after(() => {
        cy.clearSession();
    });

    it('should render guardrail form with PAIG provider steps', () => {
        cy.get('[data-testid="page-title"]').should('be.visible').and('contain', 'Create Guardrail');
        cy.get('[data-testid="guardrail-stepper"]').should('be.visible');

        cy.get('[data-testid^="step-"]:not([data-testid$="-title"]):not([data-testid$="-subtitle"])')
        .should('be.visible')
        .then((steps) => {
            cy.log(`Number of steps displayed: ${steps.length}`);
            expect(steps.length).to.equal(5);

            steps.each((index, step) => {
                cy.wrap(step).within(() => {
                    cy.get('[data-testid$="-title"]').should('be.visible').and('not.be.empty');
                    cy.get('[data-testid$="-subtitle"]').should('not.exist');
                });
            });
        });

        cy.get('[data-testid^="step-"]').should('be.visible')
        .then((steps) => {
            cy.log(`Number of steps with title: ${steps.length}`);
            expect(steps.length).to.equal(10);
        });
    });

    it('should render guardrail form with PAIG provider fields and show validation message', () => {
        cy.get('[data-testid="sticky-action-buttons"]').should('be.visible');
        cy.wait(3000);
        cy.scrollTo('bottom');
        cy.get('[data-testid="sticky-action-buttons"]').should('be.visible');

        cy.get('[data-testid="step-0"]').click();

        // should not have back button
        cy.get('[data-testid="back-button"]').should('not.exist');

        // should have cancel button
        cy.get('[data-testid="cancel-button"]').should('be.visible').and('contain', 'CANCEL');

        cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'CONTINUE').click();

        // Check for elements with error class
        cy.get('[data-testid="step-0"]').within(() => {
            cy.get('[class*="-error"]').should('exist');
        })

        cy.get('[data-testid="basic-form"]').within(() => {
            cy.get('[data-testid="basic-form-title"]').should('be.visible').and('contain', 'Enter Guardrail Details');

            cy.get('[data-testid="name"]').within(() => {
                cy.get('input').should('be.visible').and('have.value', '');
                cy.get('[class*="-error"]').should('exist').and('contain', 'Name is required.');

                cy.get('input').type('Test Guardrail Name');
                cy.get('[class*="-error"]').should('not.exist');

                cy.get('input').clear();
            });

            cy.get('[data-testid="description"]').within(() => {
                cy.get('textarea').should('be.visible').and('have.value', '');
                cy.get('[class*="-error"]').should('not.exist');
            })
        });

        cy.get('[data-testid="default-guardrail-title"]').should('be.visible').and('contain', 'Default Guardrails');
        cy.get('[data-testid="default-guardrail"]').should('be.visible').within(() => {
            cy.get('[data-testid="default-guardrail-info"]').should('be.visible').and('contain', 'Always Enabled');
        });

        cy.get('[data-testid="step-2"]').click();
        cy.get('[data-testid="guardrail-basic-alert"]').should('be.visible').and('contain', 'Name is required.');

        cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'SAVE AND CONTINUE');

        cy.get('[data-testid="basic-info"]').within(() => {
            cy.get('[data-testid="edit-button"]').should('be.visible').and('contain', 'EDIT').click();
        });

        cy.get('[data-testid="basic-form"]').within(() => {
            cy.get('[data-testid="basic-form-title"]').should('be.visible').and('contain', 'Enter Guardrail Details');
        });

        cy.get('[data-testid="cancel-button"]').should('be.visible').and('contain', 'CANCEL').click();

        // check url should be /guardrails
        cy.url().should('include', '/guardrails');
    });

    it('should render guardrail form with PAIG provider fields and validate sensitive data filters', () => {
        cy.get('[data-testid="step-1"]').click();

        cy.get('[data-testid="header"]').should('be.visible').and('contain', 'Sensitive Data Filters');

        // should have skip to review button
        cy.get('[data-testid="skip-to-review"]').should('be.visible').and('contain', 'SKIP TO REVIEW');

        cy.get('[data-testid="enable-filter"]').click();

        cy.get('[data-testid="elements-tab"]').should('be.visible');
        cy.get('[data-testid="regex-tab"]').should('not.exist');

        cy.get('[data-testid="continue-button"]').click();

        // Check for elements with error class
        cy.get('[data-testid="step-1"]').within(() => {
            cy.get('[class*="-error"]').should('exist');
        });

        // Check for error alert
        cy.get('[data-testid="sensitive-data-error-alert"]').should('be.visible').and('contain', 'Please add at least one data filter to proceed.');

        cy.get('[data-testid="sensitive-data-table"]').within(() => {
            cy.get('[data-testid="thead"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('th').should('have.length', 4);

                    cy.get('th').eq(0).should('be.visible').and('contain', 'Name');
                    cy.get('th').eq(1).should('be.visible').and('contain', 'Description');
                    cy.get('th').eq(2).should('be.visible').and('contain', 'Action');
                    cy.get('th').eq(3).should('be.visible').and('contain', '');
                })
            });

            cy.get('[data-testid="tbody-with-nodata"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('[data-testid="table-noData"]').should('be.visible').and('contain', 'No elements found');
                })
            })
        });

        cy.get('[data-testid="step-2"]').click();
        cy.get('[data-testid="sensitive-data-alert"]').should('be.visible').and('contain', 'Please add at least one data filter to proceed.');
        cy.get('[data-testid="back-button"]').should('be.visible').click();

        // Add sensitive data element
        cy.get('[data-testid="add-sensitive-data-element"]').should('be.visible').click();

        // Check for custom dialog
        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            // Check for title
            cy.get('[data-testid="customized-dialog-title"]').contains('Add Sensitive Data Element');

            // Check for input fields
            cy.get('[data-testid="checkbox"]').eq(0).click();

            // Click on the save button
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="sensitive-data-table"]').within(() => {
            cy.get('[data-testid="tbody-with-data"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('td').should('have.length', 4);

                    cy.get('td').eq(0).should('be.visible').and('not.be.empty')
                    cy.get('td').eq(1).should('be.visible').and('not.be.empty')
                    cy.get('td').eq(2).should('be.visible').within(() => {
                        cy.get('[data-testid="sensitive-data-action"]').click().type('Deny{enter}');
                    });
                    cy.get('td').eq(3).should('be.visible').within(() => {
                        cy.get('[data-test="edit"]').should('not.exist');
                        cy.get('[data-test="delete"]').should('be.visible');
                    })
                });
            });
        });

        // Move to next step
        cy.get('[data-testid="continue-button"]').click();

        // Check for step header should not be sensitive data filters
        cy.get('[data-testid="header"]').should('not.exist');

        // step should not have error class
        cy.get('[data-testid="step-1"]').within(() => {
            cy.get('[class*="-error"]').should('not.exist');
        });

        cy.get('[data-testid="sensitive-data-header"]').should('be.visible').and('contain', 'Sensitive Data Filters');
        cy.get('[data-testid="sensitive-data-element-header"]').should('be.visible').and('contain', 'Elements');
        cy.get('[data-testid="sensitive-data-element-table"]').should('be.visible').within(() => {
            cy.get('[data-testid="thead"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('th').should('have.length', 3);

                    cy.get('th').eq(0).should('be.visible').and('contain', 'Name');
                    cy.get('th').eq(1).should('be.visible').and('contain', 'Description');
                    cy.get('th').eq(2).should('be.visible').and('contain', 'Action');
                })
            });

            cy.get('[data-testid="tbody"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('td').should('have.length', 3);

                    cy.get('td').eq(0).should('be.visible').and('not.be.empty');
                    cy.get('td').eq(1).should('be.visible');
                    cy.get('td').eq(2).should('be.visible').and('contain', 'DENY');
                });
            });
        });

        cy.get('[data-testid="sensitive-data-regex-header"]').should('not.exist');
        cy.get('[data-testid="sensitive-data-regex-table"]').should('not.exist');

        // Go back to sensitive data filters
        cy.get('[data-testid="back-button"]').should('be.visible').click();

        // should not have sensitive-data-error-alert
        cy.get('[data-testid="sensitive-data-error-alert"]').should('not.exist');
    })

    it('should validate the test guardrail step, show validation message, and disable the save button', () => {
        cy.get('[data-testid="step-3"]').click();

        cy.get('[data-testid="header"]').should('be.visible').and('contain', 'Test Guardrails');
        cy.get('[data-testid="save-guardrail-alert"]').should('be.visible').and('contain', 'Please save the guardrail on review step to test it.');

        cy.get('[data-testid="test-text"]').should('be.visible').and('have.value', '').should('be.disabled');

        cy.get('[data-testid="test-guardrail"]').should('be.visible').and('contain', 'TEST INPUT').and('be.disabled');;

        cy.get('[data-testid="test-output"]').should('not.exist');

        cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'CONTINUE').and('be.disabled');
    });

    it('should validate AI application listing on the last step', () => {
       cy.get('[data-testid="step-4"]').click();

       cy.get('[data-testid="ai-application-step"]').should('be.visible').within(($content) => {
            if ($content.find('[data-testid="ai-application-header"]').length) {
                // Do something if the element exists
                cy.get('[data-testid="ai-application-header"]').should('be.visible').and('contain', 'Select AI Application');
                cy.get('[data-testid="thead"]').within(() => {
                    cy.get('tr').should('have.length', 1).within(() => {
                        cy.get('th').should('have.length', 3);

                        cy.get('th').eq(0).should('be.visible').and('contain', '');
                        cy.get('th').eq(1).should('be.visible').and('contain', 'Name');
                        cy.get('th').eq(2).should('be.visible').and('contain', 'Description');
                    })
                })

                cy.get('[data-testid="tbody-with-data"]').then(($tbody) => {
                    if ($tbody.length) {
                        // Do something if the element exists
                        cy.get('[data-testid="tbody-with-data"]').within(() => {
                            cy.get('tr').should('have.length', 1).within(() => {
                                cy.get('td').should('have.length', 3);

                                cy.get('td').eq(0).find('[data-testid="checkbox"]').should('exist');
                                cy.get('td').eq(1).should('be.visible').and('not.be.empty');
                                cy.get('td').eq(2).should('be.visible');
                            });
                        });
                    } else {
                        cy.get('[data-testid="tbody-with-nodata"]').should('be.visible').and('contain', 'No matching records found.');
                    }
                });
            } else {
                cy.get('[data-testid="no-ai-app-connected"]').should('be.visible').and('contain', 'No AI Application Connected');
                cy.get('[data-testid="no-ai-app-desc"]').should('be.visible').and('contain', 'Currently, no AI applications are connected. You may save the guardrail now and return to this step later to connect applications.');
            }
       });
    });

    it('should create a guardrail with PAIG provider steps', () => {
        cy.get('[data-testid="basic-form"]').within(() => {
            cy.get('[data-testid="name"]').type(name);
            cy.get('[data-testid="description"]').type('Test Guardrail Description');
        });

        cy.get('[data-testid="continue-button"]').click();

        cy.get('[data-testid="enable-filter"]').click();

        cy.get('[data-testid="add-sensitive-data-element"]').click();

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="checkbox"]').eq(0).click();
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="continue-button"]').click();

        // intercept post request
        cy.intercept('POST', '/guardrail-service/api/guardrail*').as('createGuardrail');

        cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'SAVE AND CONTINUE').click();

        cy.wait('@createGuardrail').then((interception) => {
            cy.get('[data-testid="snackbar"]').should('contain', 'created successfully');
            cy.wait(5000);

            cy.get('[data-testid="test-text"]').type('Test Guardrail Text');
            cy.get('[data-testid="test-guardrail"]').should('be.visible').and('contain', 'TEST INPUT').click();

            cy.wait(5000);
            cy.get('[data-testid="test-output"]').should('be.visible').and('not.be.empty');

            cy.get('[data-testid="continue-button"]').click();

            cy.get('[data-testid="ai-application-step"]').within(() => {
                cy.get('[data-testid="tbody-with-data"]').within(() => {
                    cy.get('tr').eq(0).within(() => {
                        cy.get('[data-testid="checkbox"]').click();
                    });
                });
            });

            cy.intercept('PUT', '/guardrail-service/api/guardrail/*').as('updateGuardrail');

            cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'FINISH').click();

            cy.wait('@updateGuardrail').then((interception) => {
                cy.get('[data-testid="snackbar"]').should('contain', 'updated successfully');

                cy.url().should('include', '/guardrails');
            });
        })
    })

    it('should edit a guardrail with PAIG provider steps', () => {
        // go to listing page
        cy.visit('/#/guardrails');
        cy.wait(2000);

        cy.intercept('GET', 'guardrail-service/api/guardrail?size=15&name=*').as('getGuardrails');

        // find last created guardrail using name
        cy.get('[data-testid="guardrail-search"]').type(name).type('{enter}');

        cy.wait('@getGuardrails').then((interception) => {
            cy.get('[data-testid="loader"]').should('not.exist');

            expect(interception.response.statusCode).to.eq(200);

            let {totalElements} = interception.response.body;

            expect(totalElements).to.eq(1);

            cy.get('[data-testid="table-row"]').eq(0).within(() => {
                cy.get('[data-test="edit"]').click();
            });
        })

        cy.url().should('match', /\/guardrails\/edit\/\d+/);

        cy.get('[data-testid="step-0"]').click();


        cy.get('[data-testid="basic-form"]').within(() => {
            cy.get('[data-testid="name"]').type(' - Updated');
        });

        cy.get('[data-testid="continue-button"]').click();

        //skip to review
        cy.get('[data-testid="skip-to-review"]').click();

        cy.intercept('PUT', '/guardrail-service/api/guardrail/*').as('updateGuardrail');

        cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'SAVE AND CONTINUE').click();

        cy.wait('@updateGuardrail').then((interception) => {
            cy.get('[data-testid="snackbar"]').should('contain', 'updated successfully');
        });

        // go to listing page
        cy.visit('/#/guardrails');

        cy.intercept('GET', 'guardrail-service/api/guardrail?size=15&name=*').as('getGuardrails');

        // find last created guardrail using name
        cy.get('[data-testid="guardrail-search"]').type(name + ' - Updated').type('{enter}');

        cy.wait('@getGuardrails').then((interception) => {
            cy.get('[data-testid="loader"]').should('not.exist');

            expect(interception.response.statusCode).to.eq(200);

            let {totalElements} = interception.response.body;

            expect(totalElements).to.eq(1);

            cy.get('[data-testid="table-row"]').eq(0).within(() => {
                // check if the name is updated
                cy.get('td').eq(0).should('contain', name + ' - Updated');
            });
        })
    });

    it('should delete created guardrail', () => {
        cy.visit('/#/guardrails');

        cy.intercept('GET', 'guardrail-service/api/guardrail?size=15&name=*').as('getGuardrails');

        // find last created guardrail using name
        cy.get('[data-testid="guardrail-search"]').type(name + ' - Updated').type('{enter}');

        cy.wait('@getGuardrails').then((interception) => {
            cy.get('[data-testid="loader"]').should('not.exist');

            expect(interception.response.statusCode).to.eq(200);

            let {totalElements} = interception.response.body;

            expect(totalElements).to.eq(1);

            cy.get('[data-testid="table-row"]').eq(0).within(() => {
                // check if the name is updated
                cy.get('td').eq(0).should('contain', name + ' - Updated');

                cy.get('[data-test="delete"]').click();
            });

            cy.intercept('DELETE', 'guardrail-service/api/guardrail/*').as('deleteGuardrails');

            cy.get('[data-testid="custom-dialog"]').within(() => {
                cy.get('[data-testid="confirm-dialog-title"]').should('be.visible').contains('Confirm Delete');

                cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete ${name + ' - Updated'} guardrail?`);

                cy.get('[data-test="confirm-yes-btn"]').should('be.visible').contains('Delete').click();
            });

            cy.wait('@deleteGuardrails').then((interception) => {
                cy.get('[data-testid="snackbar"]').should('contain', 'deleted successfully');
            });
        });
    })
})