import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from strawberry.fastapi import GraphQLRouter
import uvicorn

from app import schema

# Create FastAPI app
app_api = FastAPI(title="Sensor Data GraphQL API")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Create GraphQL router
graphql_route = GraphQLRouter(
    schema,
    graphiql=True  # Enable GraphiQL interface
)

# Include GraphQL router
app_api.include_router(graphql_route, prefix="/graphql")

# Mount static files
app_api.mount("/static", StaticFiles(directory="static"), name="static")

@app_api.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the dashboard homepage."""
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app_api, host="0.0.0.0", port=8000)
