import commonUtils from "../common/common_utils";

const name = 'guardrails' + '_' + commonUtils.generateRandomSentence(3, 4).replace(/ /g, '_');
const description = 'Test Guardrail Description';

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

    it('should create connection provider for aws', () => {
        cy.visit('/#/guardrail_connection_provider/AWS');

        cy.get('[data-testid="add-connection-btn"]').click();

        cy.intercept('POST', 'guardrail-service/api/connection').as('addGuardrailConnectionProvider');

        cy.get('[data-testid="custom-dialog"]').within(() => {
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
        });
    })

    it('should render guardrail form with AWS provider steps', () => {
        cy.get('[data-testid="page-title"]').should('be.visible').and('contain', 'Create Guardrail');
        cy.get('[data-testid="guardrail-stepper"]').should('be.visible');

        cy.get('[data-testid="guardrail-provider-switch"]').click();

        cy.get('[data-testid^="step-"]:not([data-testid$="-title"]):not([data-testid$="-subtitle"])')
        .should('be.visible')
        .then((steps) => {
            cy.log(`Number of steps displayed: ${steps.length}`);
            expect(steps.length).to.equal(9);

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
            expect(steps.length).to.equal(18);
        });
    });

    it('should render guardrail form with aws provider fields and show validation message', () => {
        cy.get('[data-testid="step-0"]').click();

        cy.wait(3000);

        cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'CONTINUE').click();

        cy.get('[data-testid="basic-form"]').within(() => {
            cy.get('[data-testid="basic-form-title"]').should('be.visible').and('contain', 'Enter Guardrail Details');

            cy.get('[data-testid="name"]').within(() => {
                cy.get('input').should('be.visible').and('have.value', '');
                cy.get('[class*="-error"]').should('exist').and('contain', 'Name is required.');

                cy.get('input').type('Test-Guardrail-Name');
                cy.get('[class*="-error"]').should('not.exist');

                cy.get('input').type('!@#$%^&*() ')
                cy.get('[class*="-error"]').should('exist').and('contain', 'Name should contain only alphanumeric characters, underscores and hyphens.');

                cy.get('input').clear().type('Test-Guardrail-Name_-');
                cy.get('[class*="-error"]').should('not.exist');

                cy.get('input').clear().type('Test-Guardrail-Name-Test-Guardrail-0');
                cy.get('[class*="-error"]').should('exist').and('contain', 'Max 35 characters allowed!');

                cy.get('input').type('{backspace}');
                cy.get('[class*="-error"]').should('not.exist');
            });

            cy.get('[data-testid="description"]').within(() => {
                cy.get('textarea').should('be.visible').and('have.value', '');
                cy.get('[class*="-error"]').should('not.exist');

                cy.get('[data-testid="input-field"]').type('This is a test description that is exactly 201 characters long. It is used to test the input field for the guardrail form. The description should be long enough to ensure that the input field can handl');
                cy.get('[class*="-error"]').should('exist').and('contain', 'Max 200 characters allowed!');

                // remove 1 character
                cy.get('[data-testid="input-field"]').type('{backspace}');
                cy.get('[class*="-error"]').should('not.exist');
            })
        });

        cy.get('[data-testid="guardrail-provider-switch"]').click();

        cy.get('[data-testid="continue-button"]').should('be.visible').and('contain', 'CONTINUE').click();

        cy.get('[data-testid="connection-alert"]').should('be.visible').and('contain', 'Please select a connection from below enabled connection provider.');

        // Review step
        cy.get('[data-testid="step-6"]').click();
        cy.get('[data-testid="connection-alert"]').should('be.visible').and('contain', 'Please select a connection from below enabled connection provider.');

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

    it('should validate content moderation', () => {
        cy.get('[data-testid="step-0"]').click();
        cy.get('[data-testid="guardrail-provider-switch"]').click();

        cy.get('[data-testid="step-1"]').click();

        cy.get('[data-testid="header"]').should('be.visible').and('contain', 'Content Moderation');

        // should have skip to review button
        cy.get('[data-testid="skip-to-review"]').should('be.visible').and('contain', 'SKIP TO REVIEW');

        cy.get('[data-testid="enable-filter"]').click();

        cy.get('[data-testid="continue-button"]').click();

        // Check for elements with error class
        cy.get('[data-testid="step-1"]').within(() => {
            cy.get('[class*="-error"]').should('exist');
        });

        // Check for error alert
        cy.get('[data-testid="content-moderation-error-alert"]').should('be.visible').and('contain', 'Please add at least one content moderation filter.');

        cy.get('[data-testid="step-6"]').click();
        cy.get('[data-testid="content-moderation-alert"]').should('be.visible').and('contain', 'Please add at least one content moderation filter.');
        cy.get('[data-testid="content-moderation-header"]').should('be.visible').and('contain', 'Content Moderation').within(() => {
            cy.get('[data-testid="edit-button"]').should('be.visible').and('contain', 'EDIT').click();
        });

        cy.get('[data-testid="content-moderation-table"]').within(() => {
            cy.get('[data-testid="thead"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('th').should('have.length', 4);

                    cy.get('th').eq(0).should('be.visible').and('contain', 'Status');
                    cy.get('th').eq(1).should('be.visible').and('contain', 'Category');
                    cy.get('th').eq(2).should('be.visible').and('contain', 'Description');
                    cy.get('th').eq(3).should('be.visible').and('contain', 'Guardrail Strength');
                })
            });

            cy.get('[data-testid="tbody-with-data"]').within(() => {
                cy.get('tr').should('have.length', 5)
                cy.get('tr').eq(0).within(() => {
                    // Check for status checkbox
                    cy.get('td').eq(0).should('be.visible').within(() => {
                        cy.get('[data-testid="status"]').should('exist');
                    });
                    cy.get('td').eq(1).should('be.visible').and('not.be.empty')
                    cy.get('td').eq(2).should('be.visible').should('be.visible');
                    cy.get('td').eq(3).should('be.visible').within(() => {
                        cy.get('[data-testid="guardrail-strength"]').should('be.visible').find('input').and('have.value', 'High');
                        cy.get('[data-testid="custom-reply"]').should('be.visible').and('not.be.checked');
                        cy.get('[data-testid="guardrail-strength-response"]').should('not.exist');
                        cy.get('[data-testid="custom-reply"]').click()
                        cy.get('[data-testid="guardrail-strength-response"]').should('be.visible').find('input').and('have.value', 'High');

                        cy.get('[data-testid="guardrail-strength"]').find('input').type('Med').type('{enter}');
                        cy.get('[data-testid="guardrail-strength"]').find('input').and('have.value', 'Medium');
                        cy.get('[data-testid="guardrail-strength-response"]').find('input').and('have.value', 'High');

                        cy.get('[data-testid="custom-reply"]').click().and('not.be.checked');
                        cy.get('[data-testid="guardrail-strength-response"]').should('not.exist');
                        cy.get('[data-testid="custom-reply"]').click();
                        cy.get('[data-testid="guardrail-strength-response"]').should('be.visible').find('input').and('have.value', 'Medium');
                    })
                })

                cy.get('tr').eq(0).within(() => {
                    cy.get('[data-testid="status"]').click();
                })
            })
        });

        cy.get('[data-testid="continue-button"]').click();

        cy.get('[data-testid="header"]').and('not.contain', 'Content Moderation');

        // step should not have error class
        cy.get('[data-testid="step-1"]').within(() => {
            cy.get('[class*="-error"]').should('not.exist');
        });
    })

    it('should validate sensitive data filters', () => {
        cy.get('[data-testid="step-0"]').click();
        cy.get('[data-testid="guardrail-provider-switch"]').click();
        cy.get('[data-testid="step-2"]').click();

        cy.get('[data-testid="header"]').should('be.visible').and('contain', 'Sensitive Data Filters');

        // should have skip to review button
        cy.get('[data-testid="skip-to-review"]').should('be.visible').and('contain', 'SKIP TO REVIEW');

        cy.get('[data-testid="enable-filter"]').click();

        cy.get('[data-testid="elements-tab"]').should('be.visible');
        cy.get('[data-testid="regex-tab"]').should('be.visible');

        cy.get('[data-testid="continue-button"]').click();

        // Check for elements with error class
        cy.get('[data-testid="step-2"]').within(() => {
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

        // Review step
        cy.get('[data-testid="step-6"]').click();
        cy.get('[data-testid="sensitive-data-alert"]').should('be.visible').and('contain', 'Please add at least one data filter to proceed.');
        cy.get('[data-testid="step-2"]').click();

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
                    });
                });
            });
        });

        cy.get('[data-testid="regex-tab"]').click();

        cy.get('[data-testid="add-regex"]').should('be.visible').click();

        // Check for custom dialog
        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        //checking validation
        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="name"]').type('a'.repeat(101));
            cy.get('[class*="-error"]').should('exist').and('contain', 'Max 100 characters allowed!');

            cy.get('[data-testid="name"]').type('{backspace}');
            cy.get('[class*="-error"]').should('not.exist');

            cy.get('[data-testid="pattern"]').type('a').clear();
            cy.get('[class*="-error"]').should('exist').and('contain', 'Required!');
            cy.get('[data-testid="pattern"]').type('a'.repeat(501));
            cy.get('[class*="-error"]').should('exist').and('contain', 'Max 500 characters allowed!');
            cy.get('[data-testid="pattern"]').type('{backspace}');
            cy.get('[class*="-error"]').should('not.exist');

            cy.get('[data-testid="description"]').type('a'.repeat(1001));
            cy.get('[class*="-error"]').should('exist').and('contain', 'Max 1000 characters allowed!');
            cy.get('[data-testid="description"]').type('{backspace}');
            cy.get('[class*="-error"]').should('not.exist');

            //clear all fields
            cy.get('[data-testid="name"]').clear();
            cy.get('[data-testid="pattern"]').clear();
            cy.get('[data-testid="description"]').clear();
        });

        cy.get('[data-testid="custom-dialog"]').within(() => {
            // Check for title
            cy.get('[data-testid="customized-dialog-title"]').contains('Add Regex');

            // Check for input fields
            cy.get('[data-testid="name"]').type('Test Regex');

            cy.get('[data-testid="pattern"]').type('^[a-zA-Z0-9]*$');

            cy.get('[data-testid="action"]').click().type('Deny{enter}');

            cy.get('[data-testid="description"]').type('Test Regex Description');

            // Click on the save button
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        })

        cy.get('[data-testid="sensitive-data-regex-table"]').within(() => {
            cy.get('[data-testid="table-row"]').should('have.length', 1).within(() => {
                cy.get('td').should('have.length', 5);
                cy.get('td').eq(0).should('be.visible').and('not.be.empty');
                cy.get('td').eq(1).should('be.visible').and('not.be.empty');
                cy.get('td').eq(2).should('be.visible').and('not.be.empty');
                cy.get('td').eq(3).should('be.visible').and('not.be.empty');
                cy.get('td').eq(4).should('be.visible').within(() => {
                    cy.get('[data-test="edit"]').should('be.visible');
                    cy.get('[data-test="delete"]').should('be.visible');
                });
            });
        });

        cy.get('[data-testid="custom-dialog"]').should('not.exist');

        //find edit and open modal
        cy.get('[data-testid="sensitive-data-regex-table"]').within(() => {
            cy.get('[data-testid="table-row"]').eq(0).within(() => {
                cy.get('[data-test="edit"]').click();
            });
        });

        // Check for custom dialog
        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
           cy.get('[data-testid="customized-dialog-title"]').contains('Edit Regex');
           cy.get('[data-testid="name"]').should('be.visible').and('have.value', 'Test Regex').type(' Updated');

           cy.get('[data-testid="pattern"]').should('be.visible').and('have.value', '^[a-zA-Z0-9]*$');

           cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        });

        cy.get('[data-testid="sensitive-data-regex-table"]').within(() => {
            cy.get('[data-testid="table-row"]').eq(0).within(() => {
                cy.get('td').eq(0).should('be.visible').and('contain', 'Test Regex Updated');
            })
        });

        cy.get('[data-testid="custom-dialog"]').should('not.exist');

        // add new regex
        cy.get('[data-testid="add-regex"]').should('be.visible').click();

        // Check for custom dialog
        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="customized-dialog-title"]').contains('Add Regex');

            cy.get('[data-testid="name"]').type('Test Regex Updated');

            cy.get('[data-testid="pattern"]').type('^[a-zA-Z0-9]*$');

            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="snackbar"]').should('be.visible').and('contain', 'The email regex Test Regex Updated already exists');

        cy.get('[data-testid="snackbar-close-btn"]').should('be.visible').click({ multiple: true });

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="customized-dialog-title"]').contains('Add Regex');

            cy.get('[data-testid="name"]').clear().type('Test Regex 2');

            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="snackbar"]').should('be.visible').and('contain', 'The pattern ^[a-zA-Z0-9]*$ already exists');

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="customized-dialog-title"]').contains('Add Regex');

            cy.get('[data-testid="name"]').should('have.value', 'Test Regex 2');

            cy.get('[data-testid="pattern"]').clear().type('^[a-zA-Z0-91]*$');

            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="custom-dialog"]').should('not.exist');

        // Move to next step
        cy.get('[data-testid="continue-button"]').click();

        // Check for step header should not be sensitive data filters
        cy.get('[data-testid="header"]').and('not.contain', 'Sensitive Data Filters');

        // step should not have error class
        cy.get('[data-testid="step-2"]').within(() => {
            cy.get('[class*="-error"]').should('not.exist');
        });

        cy.get('[data-testid="step-6"]').click();
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

        cy.get('[data-testid="sensitive-data-regex-header"]').should('be.visible').and('contain', 'Regex');
        cy.get('[data-testid="sensitive-data-regex-table"]').should('be.visible').within(() => {
            cy.get('[data-testid="thead"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('th').should('have.length', 4);

                    cy.get('th').eq(0).should('be.visible').and('contain', 'Name');
                    cy.get('th').eq(1).should('be.visible').and('contain', 'Pattern');
                    cy.get('th').eq(2).should('be.visible').and('contain', 'Description');
                    cy.get('th').eq(3).should('be.visible').and('contain', 'Action');
                })
            });
        })

        // Go back to sensitive data filters
        cy.get('[data-testid="back-button"]').should('be.visible').click();

        // should not have sensitive-data-error-alert
        cy.get('[data-testid="sensitive-data-error-alert"]').should('not.exist');
    });

    it('should validate off-topic filters', () => {
        cy.get('[data-testid="step-0"]').click();
        cy.get('[data-testid="guardrail-provider-switch"]').click();
        cy.get('[data-testid="step-3"]').click();

        cy.get('[data-testid="header"]').should('be.visible').and('contain', 'Off Topic filters');

        // should have skip to review button
        cy.get('[data-testid="skip-to-review"]').should('be.visible').and('contain', 'SKIP TO REVIEW');

        cy.get('[data-testid="enable-filter"]').click();

        cy.get('[data-testid="continue-button"]').click();

        // Check for elements with error class
        cy.get('[data-testid="step-3"]').within(() => {
            cy.get('[class*="-error"]').should('exist');
        });

        // Check for error alert
        cy.get('[data-testid="off-topic-error-alert"]').should('be.visible').and('contain', 'Please add at least one off topic filter.');

        cy.get('[data-testid="step-6"]').click();
        cy.get('[data-testid="off-topic-alert"]').should('be.visible').and('contain', 'Please add at least one off topic filter.');
        cy.get('[data-testid="off-topic-header"]').should('be.visible').and('contain', 'Off-topic filters').within(() => {
            cy.get('[data-testid="edit-button"]').should('be.visible').and('contain', 'EDIT').click();
        });

        cy.get('[data-testid="off-topics-table"]').within(() => {
            cy.get('[data-testid="thead"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('th').should('have.length', 4);

                    cy.get('th').eq(0).should('be.visible').and('contain', 'Topic');
                    cy.get('th').eq(1).should('be.visible').and('contain', 'Definition');
                    cy.get('th').eq(2).should('be.visible').and('contain', 'Sample Phrases');
                    cy.get('th').eq(3).should('be.visible').and('contain', 'Actions');
                })
            });

            cy.get('[data-testid="tbody-with-nodata"]').should('be.visible').and('contain', 'No off topics found');
        });


        cy.get('[data-test="add-btn"]').should('be.visible').and('contain', 'Add Off topic').click();

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();

            cy.get('[data-testid="topic"]').should('contain.text', 'Required!');
            cy.get('[data-testid="definition"]').should('contain.text', 'Required!');
            cy.get('[data-testid="sample-phrases"]').should('not.contain.text', 'Required!');

            cy.get('[data-testid="topic"]').type('a'.repeat(101));
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
            cy.get('[data-testid="topic"]').should('contain.text', 'Max 100 characters allowed!');

            cy.get('[data-testid="topic"]').clear().type('Invalid@#$');
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
            cy.get('[data-testid="topic"]').should('contain.text', 'Only alphanumeric characters, spaces, underscores, hyphens, exclamation points, question marks, and periods are allowed!');

            cy.get('[data-testid="topic"]').clear().type('Test Topic');

            cy.get('[data-testid="definition"]').type('a'.repeat(201));
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
            cy.get('[data-testid="definition"]').should('contain.text', 'Max 200 characters allowed!');

            cy.get('[data-testid="definition"]').clear().type('Test Definition');

            cy.get('[data-testid="sample-phrases"]').type('a'.repeat(101));
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
            cy.get('[data-testid="sample-phrases"]').should('contain.text', 'Max 100 characters allowed!');

            cy.get('[data-testid="sample-phrases"]').clear().type('Test Sample Phrases');

            cy.get('[data-testid="topic"]').should('not.contain.text', 'Required!');
            cy.get('[data-testid="definition"]').should('not.contain.text', 'Required!');
            cy.get('[data-testid="sample-phrases"]').should('not.contain.text', 'Max 100 characters allowed!');

            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="custom-dialog"]').should('not.exist');

        cy.get('[data-testid="off-topics-table"]').within(() => {
            cy.get('[data-testid="tbody-with-data"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('td').should('have.length', 4);

                    cy.get('td').eq(0).should('be.visible').contains('Test Topic');
                    cy.get('td').eq(1).should('be.visible').contains('Test Definition');
                    cy.get('td').eq(2).should('be.visible').contains('Test Sample Phrases');
                    cy.get('td').eq(3).should('be.visible').within(() => {
                        cy.get('[data-test="edit"]').should('be.visible');
                        cy.get('[data-test="delete"]').should('be.visible');
                    });
                });
            });
        });

        cy.get('[data-testid="off-topics-table"]').within(() => {
            cy.get('[data-testid="tbody-with-data"]').within(() => {
                cy.get('tr').eq(0).within(() => {
                    cy.get('[data-test="edit"]').click();
                });
            });
        });

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="topic"]').type(' Updated');

            cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        });

        cy.get('[data-testid="custom-dialog"]').should('not.exist');

        cy.get('[data-testid="off-topics-table"]').within(() => {
            cy.get('[data-testid="tbody-with-data"]').within(() => {
                cy.get('tr').eq(0).within(() => {
                   cy.get('td').eq(0).and('contain', 'Test Topic Updated');
                });
            });
        });

        cy.get('[data-test="add-btn"]').and('contain', 'Add Off topic').click();

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="topic"]').type('Test Topic Updated');
            cy.get('[data-testid="definition"]').type('Test Definition');
            cy.get('[data-testid="sample-phrases"]').type('Test Sample Phrases');

            cy.get('[data-testid="topic"]').should('not.contain.text', 'Required!');
            cy.get('[data-testid="definition"]').should('not.contain.text', 'Required!');

            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="snackbar"]').should('contain', 'The topic Test Topic Updated already exists');

        cy.get('[data-testid="snackbar-close-btn"]').should('exist').click({ multiple: true });

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="topic"]').type(' 2');
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        });

        cy.get('[data-testid="custom-dialog"]').should('not.exist');

        cy.get('[data-testid="off-topics-table"]').within(() => {
            cy.get('[data-testid="tbody-with-data"]').within(() => {
                cy.get('tr').should('have.length', 2);
            });
        });

        cy.get('[data-testid="continue-button"]').click();

        cy.get('[data-testid="header"]').and('not.contain', 'Off Topic filters');

        // step should not have error class
        cy.get('[data-testid="step-3"]').within(() => {
            cy.get('[class*="-error"]').should('not.exist');
        });

        cy.get('[data-testid="step-6"]').click();

        cy.get('[data-testid="off-topic-alert"]').should('not.exist');

        cy.get('[data-testid="off-topic-header"]').within(() => {
            cy.get('[data-testid="edit-button"]').click();
        });

        cy.get('[data-testid="off-topic-error-alert"]').should('not.exist');
    });

    it('should validate denied terms filters', () => {
        cy.get('[data-testid="step-0"]').click();
        cy.get('[data-testid="guardrail-provider-switch"]').click();
        cy.get('[data-testid="step-4"]').click();

        cy.get('[data-testid="header"]').should('be.visible').and('contain', 'Denied Terms');

        // should have skip to review button
        cy.get('[data-testid="skip-to-review"]').should('be.visible').and('contain', 'SKIP TO REVIEW');

        cy.get('[data-testid="enable-filter"]').click();

        cy.get('[data-testid="profanity-filter"]').find('input').should('be.checked');

        cy.get('[data-testid="continue-button"]').click();

        // Check for elements with error class
        cy.get('[data-testid="step-4"]').within(() => {
            cy.get('[class*="-error"]').should('not.exist');
        });

        // Check for error alert
        cy.get('[data-testid="header"]').should('be.visible').and('not.contain', 'Denied Terms');

        cy.get('[data-testid="step-6"]').click();
        cy.get('[data-testid="denied-terms-alert"]').should('not.exist');
        cy.get('[data-testid="denied-terms-header"]').should('be.visible').and('contain', 'Denied Terms').within(() => {
            cy.get('[data-testid="edit-button"]').should('be.visible').and('contain', 'EDIT').click();
        });

        cy.get('[data-testid="denied-terms-table"]').within(() => {
            cy.get('[data-testid="thead"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('th').should('have.length', 2);

                    cy.get('th').eq(0).should('be.visible').and('contain', 'Phrases and Keywords');
                    cy.get('th').eq(1).should('be.visible').and('contain', 'Actions');
                })
            });

            cy.get('[data-testid="tbody-with-nodata"]').should('be.visible').and('contain', 'No data found');
        });

        cy.get('[data-testid="profanity-filter"]').click();

        cy.get('[data-testid="profanity-filter"]').find('input').should('not.be.checked');

        cy.get('[data-testid="continue-button"]').click();

        // Check for elements with error class
        cy.get('[data-testid="step-4"]').within(() => {
            cy.get('[class*="-error"]').should('exist');
        })

        // Check for error alert
        cy.get('[data-testid="denied-terms-error-alert"]').should('be.visible').and('contain', 'Please add at least one denied term, or enable profanity filter.');

        cy.get('[data-test="add-btn"]').should('be.visible').and('contain', 'Add').click();

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();

            cy.get('[data-testid="phrases-and-keywords"]').should('contain.text', 'Required!');
            cy.get('[data-testid="phrases-and-keywords"]').type('a'.repeat(101)).type('{enter}');
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();

            cy.get('[data-testid="phrases-and-keywords"]').should('contain.text', 'Each keyword can contain up to 100 characters');
            cy.get('[data-testid="phrases-and-keywords"]').click();
            cy.get('.MuiAutocomplete-clearIndicator').click();

            cy.wait(1000);

            cy.get('[data-testid="phrases-and-keywords"]').type('Test Phrases and Keywords').type('{enter}');

            cy.get('[data-testid="phrases-and-keywords"]').should('not.contain.text', 'Required!');
            cy.get('[data-testid="phrases-and-keywords"]').should('not.contain.text', 'Each keyword can contain up to 100 characters');

            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        })

        cy.get('[data-testid="custom-dialog"]').should('not.exist');

        cy.get('[data-testid="denied-terms-table"]').within(() => {
            cy.get('[data-testid="tbody-with-data"]').within(() => {
                cy.get('tr').should('have.length', 1).within(() => {
                    cy.get('td').should('have.length', 2);

                    cy.get('td').eq(0).should('be.visible').contains('Test Phrases and Keywords');
                    cy.get('td').eq(1).should('be.visible').within(() => {
                        cy.get('[data-test="delete"]').should('be.visible');
                        cy.get('[data-test="edit"]').should('be.visible').click();
                    });
                });
            })
        })

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-testid="phrases-and-keywords"]').type('Test Phrases and Keywords edit').type('{enter}');
            cy.get('[data-testid="phrases-and-keywords"]').click();
            cy.get('[data-test="modal-ok-btn"]').contains('Save').click();
        });

        cy.get('[data-test="add-btn"]').should('be.visible').and('contain', 'Add').click();

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-testid="custom-dialog"]').within(() => {
            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();

            cy.get('[data-testid="phrases-and-keywords"]').should('contain.text', 'Required');

            cy.get('[data-testid="phrases-and-keywords"]').type('Test Phrases and Keywords').type('{enter}');

            cy.get('[data-testid="phrases-and-keywords"]').should('not.contain.text', 'Required');

            cy.get('[data-test="modal-ok-btn"]').contains('Add').click();
        })

        cy.get('[data-testid="snackbar"]').should('be.visible').and('contain', 'The keywords Test Phrases and Keywords already exists');

        cy.get('[data-testid="snackbar-close-btn"]').should('be.visible').click({ multiple: true });

        cy.get('[data-testid="custom-dialog"]').should('be.visible');

        cy.get('[data-test="modal-cancel-btn"]').contains('Close').click();

        cy.get('[data-testid="continue-button"]').click();

        cy.get('[data-testid="header"]').and('not.contain', 'Denied Terms');

        // step should not have error class
        cy.get('[data-testid="step-4"]').within(() => {
            cy.get('[class*="-error"]').should('not.exist');
        });

        cy.get('[data-testid="step-6"]').click();

        cy.get('[data-testid="denied-terms-alert"]').should('not.exist');

        cy.get('[data-testid="denied-terms-header"]').within(() => {
            cy.get('[data-testid="edit-button"]').click();
        })
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

            cy.get('[data-testid="dialog-content"]').should('contain.text', `Are you sure you want to delete ${name} connection?`);

            cy.get('[data-test="confirm-yes-btn"]').should('be.visible').contains('Delete').click();
        });

        cy.wait('@deleteGuardrailConnectionProvider').then((interception) => {
            expect(interception.response.statusCode).to.eq(204);

            cy.get('[data-testid="custom-dialog"]').should('not.exist');

            cy.get('[data-testid="snackbar"]').should('contain', 'deleted successfully');

            cy.get('[data-testid="snackbar-close-btn"]').should('exist').click({ multiple: true });
        });
    });
});
