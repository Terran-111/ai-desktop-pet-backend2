import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage 
from prompt import SYSTEM_PROMPT

# 导入所有工具
from tools.system_ops import get_system_status, kill_process_by_name, check_python_env
from tools.file_ops import organize_desktop, search_large_files
from tools.net_ops import get_public_ip_info, scan_local_ports

# 【新增】引入内存存储模块
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# 【新增】初始化内存保存器，用于持久化对话状态
memory = MemorySaver()

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
# 【修改】添加 checkpointer 参数，开启记忆功能
agent_executor = create_react_agent(
    model=llm,
    tools=tools,
    checkpointer=memory, # 注册内存检查点
)

async def run_agent_logic(user_input: str):
    """
    【修改版】增加上下文记忆支持
    """
    # LangGraph 会自动处理 messages 列表的追加，我们只需要发送当前用户输入
    inputs = {"messages": [("user", user_input)]}
    
    # 【核心修正】定义对话配置。thread_id 相同的对话会被视为同一个上下文。
    # 对于单机桌宠，我们可以固定一个 thread_id。
    config = {"configurable": {"thread_id": "commander_session_1"}} 
    
    full_response_buffer = ""

    # 【关键修改】在 astream_events 中传入 config=config
    # 如果不传这个参数，Agent 每次都会开启全新的、无记忆的会话
    async for event in agent_executor.astream_events(inputs, config=config, version="v1"): 
        kind = event["event"]
        
        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                full_response_buffer += content
    
    if full_response_buffer:
        yield full_response_buffer