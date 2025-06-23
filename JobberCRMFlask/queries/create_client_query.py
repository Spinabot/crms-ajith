# GraphQL mutation for creating a client
create_client_mutation = """
mutation CreateClient($input: ClientCreateInput!) {
  clientCreate(input: $input) {
    client {
      id
      firstName
      lastName
      companyName
      billingAddress {
        street1
        street2
        city
        province
        country
        postalCode
      }
      phones {
        number
        primary
      }
      emails {
        address
        primary
      }
    }
    userErrors {
      message
      path
    }
  }
}
"""