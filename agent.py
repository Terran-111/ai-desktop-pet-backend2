import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage # 引入消息类型
from prompt import SYSTEM_PROMPT

# 导入所有工具
from tools.system_ops import get_system_status, kill_process_by_name, check_python_env
from tools.file_ops import organize_desktop, search_large_files
from tools.net_ops import get_public_ip_info, scan_local_ports

load_dotenv()

# 1. 初始化模型
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "qwen-max"),
    openai_api_key=os.getenv("QWEN_API_KEY"),
    openai_api_base=os.getenv("OPENAI_API_BASE"),
    temperature=0.3,
    streaming=True
)

# 2. 注册工具箱
tools = [
    get_system_status,
    kill_process_by_name,
    check_python_env,
    organize_desktop,
    search_large_files,
    get_public_ip_info,
    scan_local_ports
]

# 3. 创建 Agent
# 【核心修改】：这里不再传任何 modifier 参数，避免报错
agent_executor = create_react_agent(
    model=llm,
    tools=tools
)

async def run_agent_logic(user_input: str):
    """
    【修改版】缓冲模式：攒够一整句话再发，解决前端语音卡死问题
    """
    inputs = {"messages": [("user", user_input)]}
    
    # 用来积攒文字的“蓄水池”
    full_response_buffer = ""

    # 使用 astream_events 获取流式 token
    async for event in agent_executor.astream_events(inputs, version="v1"):
        kind = event["event"]
        
        # 当模型生成文本块时
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                # 1. 只是攒着，先不发
                full_response_buffer += content
                # yield content  <-- 【关键】把这行注释掉或者删掉！
    
    # 2. 循环结束后，一次性把整句话发出去
    if full_response_buffer:
        yield full_response_buffer