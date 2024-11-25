describe('Test securechat', () => {
  it.only('Check URL is up', () => {
    cy.visit("/")
    cy.get('#loginButton').should('be.enabled')
  })

  it.only('Login into App', () => {
    cy.visit("/")
    cy.get('#userNameField').type('test')
    cy.get('#loginButton').click()
    cy.get('#newConversationBtn').click()
    cy.get('#hover-menu').should('length', 1)
  })

  it.only('Ask Prompt', () => {
    cy.visit("/")
    cy.get('#userNameField').type('test')
    cy.get('#loginButton').click()
    cy.get('#textInput').type('Is Equinox Technologies a prospect?')
    cy.get('#sendMsgBtn').click()
//    cy.wait(5000)
    cy.get('.css-1smoasd > p').should('not.be.empty')
  })
})
