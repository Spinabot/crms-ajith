# GraphQL mutation to update a client in Jobber
update_client_mutation = """
mutation UpdateClient(
  $clientId: EncodedId!
  $firstName: String
  $lastName: String
  $companyName: String
  $emailsToEdit: [EmailUpdateAttributes!]
  $emailsToAdd: [EmailCreateAttributes!]
  $phonesToEdit: [PhoneNumberUpdateAttributes!]
  $phonesToAdd: [PhoneNumberCreateAttributes!]
  $phonesToDelete: [EncodedId!]
  $emailsToDelete: [EncodedId!]
  $billingAddress: AddressAttributes
) {
  clientEdit(
    clientId: $clientId
    input: {
      firstName: $firstName
      lastName: $lastName
      companyName: $companyName
      emailsToEdit: $emailsToEdit
      emailsToAdd: $emailsToAdd
      phonesToAdd: $phonesToAdd
      phonesToEdit: $phonesToEdit
      phonesToDelete: $phonesToDelete
      emailsToDelete: $emailsToDelete
      billingAddress: $billingAddress
    }
  ) {
    client {
      id
      firstName
      lastName
      companyName
      jobberWebUri
      emails {
        id
        address
      }
      phones {
        id
        number
      }
      balance
      defaultEmails
      clientProperties {
        nodes {
          address {
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
    userErrors {
      message
      path
    }
  }
}
"""