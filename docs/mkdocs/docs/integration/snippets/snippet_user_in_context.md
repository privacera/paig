If it is a chatbot application or an application where the user is prompted for input, then you need to pass the
username of the user to the create_shield_context method. Privacera Shield will use this username to check access for
the user. If it is a batch application, then you can pass the username for the service account, which could be any 
unique name e.g. document_summarizer. The policies will be checked against this username.

