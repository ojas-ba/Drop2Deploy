from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
import firebase_admin
from firebase_admin import auth, initialize_app, credentials



class FireBaseAuthenticationMiddleware(BaseHTTPMiddleware):
    # First We intialize the middleware with the FastAPI app and a list of public routes
    def __init__(self, app, public_routes: list[str] = ["/docs","/auth","/openapi.json","/redoc","/favicon.ico"]):
        super().__init__(app)
        # First We Check if Firebase Admin SDK is already initialized otherwise we initialize it
        if not firebase_admin._apps:
            cred = credentials.Certificate("credentials.json")
            initialize_app(cred)
        self.public_routes = public_routes
    
    # The dispatch method is called for each request, where we check if the request is for a public route or if it has a valid Firebase token.
    # Authorization header is expected to be in the format "Bearer <token>", anything else Exception is raised.
    
    async def dispatch(self, request: Request, call_next):
        try:
            if request.method == "OPTIONS":
                return await call_next(request)
            if request.url.path in self.public_routes:
                return await call_next(request)
            
            auth_header = request.headers.get("Authorization")
            
            if not auth_header:
                raise HTTPException(status_code=401, detail="Authorization header missing")
            
            if not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Invalid authorization header format")
            
            token = auth_header.split("Bearer ")[1]
            
            try:
                decoded_token = auth.verify_id_token(token)
                request.state.user = decoded_token
            except Exception as e:
                raise HTTPException(status_code=401, detail="Invalid or expired token")

            return await call_next(request)
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code,detail=e.detail)


# Also One more important thing ; 
# request.state.user will contain the decoded token which can be used in the route handlers to access user information.
# For example, we can access the user ID with request.state.user['uid'], 'name' and other user information as per our Firebase configuration.
