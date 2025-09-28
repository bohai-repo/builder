import requests
from fastmcp import FastMCP
# from starlette.applications import Starlette
# from starlette.routing import Route, Mount
# from mcp.server.sse import SseServerTransport

mcp = FastMCP("测试 MCP 服务器")
@mcp.tool()
def hello(name: str) -> str:
    return f"你好 {name}!"

@mcp.tool()
def exTool1(user: str) -> str:
    return f"用户 {user} !"

# transport = SseServerTransport("/messages/")
#
# async def handle_sse(request):
#     async with transport.connect_sse(
#         request.scope,
#         request.receive,
#         request._send
#     ) as (in_stream, out_stream):
#         await mcp._mcp_server.run(
#             in_stream,
#             out_stream,
#             mcp._mcp_server.create_initialization_options()
#         )

# sse_app = Starlette(
#     routes=[
#         Route("/sse", handle_sse, methods=["GET"]),
#         Mount("/messages/", app=transport.handle_post_message)
#     ]
# )

if __name__ == "__main__":

    mcp.run(transport="http")