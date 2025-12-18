from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from agent import run_agent_logic
import uvicorn
import asyncio

app = FastAPI()

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print(">>> 战术链路已连接 (Uplink Established) <<<")
    
    try:
        while True:
            # 接收前端发来的指令
            data = await websocket.receive_text()
            print(f"[RECV] 指令: {data}")
            
            # 只有非空指令才处理
            if data.strip():
                # 调用 Agent 并流式回传
                full_response = ""
                async for chunk in run_agent_logic(data):
                    full_response += chunk
                    await websocket.send_text(chunk)
                    # 稍微 delay 一点点防止发送太快前端吞字（可选）
                    # await asyncio.sleep(0.01)
                
                print(f"[SENT] 回复: {full_response[:50]}...")
            
    except WebSocketDisconnect:
        print(">>> 战术链路中断 (Uplink Lost) <<<")
    except Exception as e:
        print(f"[ERROR] 系统异常: {e}")

if __name__ == "__main__":
    # 启动服务，监听 8000 端口
    uvicorn.run(app, host="127.0.0.1", port=8000)   