import gradio as gr
import json
import inspect
from openai import AzureOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from classes import Agent, Response
from agents import agent_triaj, agent_persoana_fizica, agent_persoana_juridica
from knowledge import vectorstore_dict

# Configurare pentru Azure OpenAI
client = AzureOpenAI(
    azure_endpoint="https://rbro-openai-hackatlon.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview",
    api_key="",
    api_version="2024-08-01-preview"
)

# Funții ajutătoare pentru gestionarea funcțiilor agentului
def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }
    signature = inspect.signature(func)
    parameters = {
        param.name: {"type": type_map.get(param.annotation, "string")}
        for param in signature.parameters.values()
    }
    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

def execute_tool_call(tool_call, tools, agent_name):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    return tools[name](**args)  # apelează funcția corespunzătoare

def get_context(file_name, question):
    vectorstore = vectorstore_dict[file_name]
    retriever = vectorstore.as_retriever()
    sources = retriever.invoke(question)
    docs_text = "".join(d.page_content for d in sources)
    return docs_text

def run_full_turn(agent, messages):
    current_agent = agent
    context = ""
    
    # Dacă agentul nu este unul dintre cei trei agenți de bază
    if current_agent not in [agent_triaj, agent_persoana_fizica, agent_persoana_juridica]:
        context = get_context(current_agent.file_name, messages[-1]["content"])

    while True:
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools = {tool.__name__: tool for tool in current_agent.tools}
        
        response = client.chat.completions.create(
            model=agent.model,
            messages=[{"role": "system", "content": current_agent.instructions + " Context: " + context}] + messages,
            tools=tool_schemas or None,
            temperature=0  # Adjusted temperature for more creative responses
        )
        
        message = response.choices[0].message
        messages.append(message)

        if message.content:
            return current_agent, message.content

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tools, current_agent.name)

            if isinstance(result, Agent):  # Schimb de agent
                current_agent = result
                result = f"Transfered to {current_agent.name}. Adopt persona immediately."

            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            messages.append(result_message)

    return current_agent, Response(agent=current_agent, messages=messages)

# Funcția de chat pentru Gradio
current_agent = agent_triaj
messages = []

def chat_with_ai(user_input):
    global current_agent, messages
    messages.append({"role": "user", "content": user_input})
    current_agent, response = run_full_turn(current_agent, messages)
    messages.append({"role": "assistant", "content": response})
    return response

with gr.Blocks(css=""".chatbox {
    border-left: 5px solid yellow;
    border-right: 5px solid yellow;
    border-top: 5px solid yellow;  # Adaugă marginea de sus
    border-bottom: 5px solid yellow;  # Adaugă marginea de jos
}
""") as chat_interface:
    
    gr.Markdown("# Hi! 👋 I'm Raffy, your personal banking assistant. How can I help you today?")
    chat_history = gr.Chatbot(elem_id="chatbot", height=600)
    user_input = gr.Textbox(placeholder="Scrie un mesaj...")

    def respond(message, history):
        response = chat_with_ai(message)
        history.append((
        message, 
        f'<div style="display: flex; align-items: center;">'  # Use flexbox for inline layout
        f'<img src="bot.png" alt="AI Response" style="width:15px;height:15px; margin-right: 10px;">'  # Image to the left with some margin
        f'{response}'  # Text to the right of the image
        f'</div>'
    ))
  # Add user message to the right
        return "", history

    user_input.submit(respond, inputs=[user_input, chat_history], outputs=[user_input, chat_history])

chat_interface.launch(share=True)
