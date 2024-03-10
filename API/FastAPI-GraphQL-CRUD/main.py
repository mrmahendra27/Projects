import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from config import db

import strawberry
from GraphQL.query import Query
from GraphQL.mutation import Mutation
from strawberry.fastapi import GraphQLRouter


def init_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Add all tables to the db if not exists
        await db.create_all()
        yield
        # Close the database connection
        await db.close()

    apps = FastAPI(
        title="FastAPI GraphQL CRUD",
        description="CRUD operation using Fast API and GraphQL",
        lifespan=lifespan,
        # version=""
    )

    @apps.get("/")
    def home():
        return "Welcome User!"

    schema = strawberry.Schema(query=Query, mutation=Mutation)
    graphql_app = GraphQLRouter(schema)

    apps.include_router(graphql_app, prefix="/graphql")

    return apps


app = init_app()

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=8000, reload=True)
