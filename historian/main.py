import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from strawberry.fastapi import GraphQLRouter

from app import schema

# Create FastAPI app
app = FastAPI(title="Sensor Data GraphQL API")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Create GraphQL router
graphql_route = GraphQLRouter(
    schema,
    graphiql=True  # Enable GraphiQL interface
)

# Include GraphQL router
app.include_router(graphql_route, prefix="/graphql")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the dashboard homepage."""
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
