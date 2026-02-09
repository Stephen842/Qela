import graphene
from feed.graphql.queries import Query
from feed.graphql.mutations import Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)