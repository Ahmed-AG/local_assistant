"""
FastAPI-based MCP Server with SSE support
"""

import asyncio
import json
import logging
from typing import AsyncGenerator
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from mcp.server import Server

logger = logging.getLogger(__name__)

class FastAPIMCPServer:
    """FastAPI-based MCP Server implementation

    Exposes:
      - GET /sse  -> EventSource (SSE)
      - POST /sse -> accepts initialization POST then opens SSE
      - POST /call_tool -> calls registered MCP tool handler
      - GET  /list_tools -> returns list of tools
    """

    def __init__(self, mcp_server: Server, host: str = "localhost", port: int = 8080):
        self.mcp_server = mcp_server
        self.host = host
        self.port = port
        self.app = FastAPI()
        self._setup_routes()

    def _setup_routes(self):
        # add permissive CORS for local testing
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.get("/sse")
        async def sse_get(request: Request):
            async def event_generator() -> AsyncGenerator[str, None]:
                # initial ready event with server info
                init_data = {
                    "type": "ready",
                    "serverInfo": {
                        "name": "calendar-mcp",
                        "version": "1.0.0",
                        "capabilities": ["calendar-query", "availability-check"],
                    },
                }
                yield {"event": "ready", "data": json.dumps(init_data)}

                try:
                    while True:
                        if await request.is_disconnected():
                            logger.info("SSE client disconnected")
                            break
                        heartbeat = {"timestamp": int(asyncio.get_event_loop().time())}
                        yield {"event": "heartbeat", "data": json.dumps(heartbeat)}
                        await asyncio.sleep(30)
                except asyncio.CancelledError:
                    logger.info("SSE generator cancelled")
                    return

            return EventSourceResponse(event_generator())

        @self.app.post("/sse")
        async def sse_post(request: Request):
            # some clients post an init payload before opening SSE.
            try:
                _ = await request.json()
            except Exception:
                # ignore non-JSON or empty bodies
                pass
            return await sse_get(request)

        @self.app.post("/call_tool")
        async def call_tool(request: Request):
            try:
                data = await request.json()
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid JSON body")

            tool_name = data.get("name")
            arguments = data.get("arguments", {})

            if not tool_name:
                raise HTTPException(status_code=400, detail="Tool name is required")

            try:
                # Expect the provided mcp_server to expose async helpers for invoking handlers.
                # Many MCP server wrappers provide convenience methods; if not, adapt this to call
                # the underlying registered handler directly.
                result = await self.mcp_server.call_tool_handler(tool_name, arguments)
                return JSONResponse(content=[r.__dict__ for r in result])
            except AttributeError:
                # fallback: try calling the server via its public API if available
                logger.exception("call_tool_handler not found on mcp_server")
                raise HTTPException(status_code=500, detail="Server not configured to handle tool calls")
            except Exception as e:
                logger.exception("Error while handling call_tool")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/list_tools")
        async def list_tools():
            try:
                tools = await self.mcp_server.list_tools_handler()
                return JSONResponse(content=[tool.__dict__ for tool in tools])
            except AttributeError:
                logger.exception("list_tools_handler not found on mcp_server")
                raise HTTPException(status_code=500, detail="Server not configured to list tools")
            except Exception as e:
                logger.exception("Error while listing tools")
                raise HTTPException(status_code=500, detail=str(e))

    async def start(self):
        import uvicorn
        config = uvicorn.Config(self.app, host=self.host, port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
