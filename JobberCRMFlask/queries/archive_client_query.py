# GraphQL mutation to archive a client in Jobber
archive_client_mutation = """
mutation ArchiveClient($clientId: EncodedId!) {
  clientArchive(clientId: $clientId) {
    client {
      id
      firstName
      lastName
      companyName
    }
    userErrors {
      message
      path
    }
  }
}
"""