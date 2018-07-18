const { ApolloServer, gql } = require('apollo-server')
const grpc = require('grpc')
const notify = grpc.load('../grpc/defs/notify.proto')

const client = new notify.Notify(
  'localhost:50051',
  grpc.credentials.createInsecure()
)

const getUsers = params =>
  new Promise((resolve, reject) =>
    client.getUsers(params, (err, data) => (err ? reject(err) : resolve(data)))
  )

const servicesForUser = params =>
  new Promise((resolve, reject) =>
    client.servicesForUser(
      params,
      (err, data) => (err ? reject(err) : resolve(data))
    )
  )

getUsers({ user_id: 'a user. here it is' })
  .then(data => {
    console.log('we got the data.', data.users, data.users[1].id)
    return servicesForUser({ user_id: data.users[1].id }).then(sdata => {
      console.log('we got the services.', sdata)
      return sdata
    })
  })
  .catch(err => console.log('we got the error.', { err }))

const typeDefs = gql`
  schema {
    query: Query
  }

  type Permission {
    service: String
    permission: String
  }

  type Service {
    active: Boolean
    branding: String
    created_by: String
    email_from: String
    id: String
    name: String
    organisation_type: String
    rate_limit: Int
    annual_billing: [String!]
    permissions: [String!]
    user_to_service: [String!]
  }

  type User {
    name: String
    auth_type: String
    email_address: String
    failed_login_count: Int
    password_changed_at: String
    permissions: [Permission!]
    services: [Service!]
  }

  type Query {
    users(id: String!): [User!]
    hello: String!
  }
`

const flatMap = fx => xs => Array.prototype.concat(...xs.map(fx))

// Resolvers define the technique for fetching the types in the
// schema.  We'll retrieve books from the "books" array above.
const resolvers = {
  Query: {
    hello: () => 'hello world',
    users(root, { id }, context, info) {
      return new Promise((resolve, reject) =>
        client.getUsers(
          { user_id: id },
          (err, data) => (err ? reject(err) : resolve(data.users))
        )
      )
    },
  },

  User: {
    services(user) {
      return new Promise((resolve, reject) =>
        client.servicesForUser(
          { user_id: user.id },
          (err, data) => (err ? reject(err) : resolve(data.services))
        )
      )
    },

    permissions(user) {
      return flatMap(({ service, permissions }) =>
        permissions.map(permission => ({ service, permission }))
      )(
        Object.entries(user.permissions).map(([service, permissions]) => ({
          service,
          permissions: permissions.permissions,
        }))
      )
    },
  },
}

// In the most basic sense, the ApolloServer can be started
// by passing type definitions (schema) and the resolvers
// responsible for fetching the data for those types.
const server = new ApolloServer({ typeDefs, resolvers })

// This `listen` method launches a web-server.  Existing apps
// can utilize middleware options, which we'll discuss later.
server.listen().then(({ url }) => {
  console.log(`🚀  Server ready at ${url}`)
})
