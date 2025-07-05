# GraphQL query for getting client data with lead filtering
get_client_data = """
query GetBasicClientData($cursor: String) {
  clients(first: 15, after: $cursor, filter: {isLead: true, isArchived: false}) {
    nodes {
      id
      firstName
      lastName
      isLead
      isCompany
      companyName
      jobberWebUri
      phones {
        id
        description
        smsAllowed
        number
      }
      emails {
        id
        address
      }
      balance
      companyName
      defaultEmails
      clientProperties {
        nodes {
          address {
            id
            city
            country
            postalCode
          }
        }
      }
      sourceAttribution {
        sourceText
        metadata
        source {
          __typename
          ... on Application {
            id
            name
          }
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""