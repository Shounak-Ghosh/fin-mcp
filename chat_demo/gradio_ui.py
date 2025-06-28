# chat_demo/chat_agent.py
import gradio as gr
from langchain_core.messages import HumanMessage, AIMessage
from chat_agent import stream_chat_agent # Import the async stream_chat_agent

# Gradio's chat history is always a list of lists/dicts.
# Your format_chat_history function should convert it to LangChain's message objects.
def format_chat_history(history):
    """Convert Gradio history (list of dicts) into LangChain message objects."""
    messages = []
    for item in history:
        # Gradio's type='messages' means history items are dicts with 'role' and 'content'
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        # Fallback for old tuple format if it somehow appears (though with type='messages', it shouldn't)
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            user_msg, assistant_msg = item
            if user_msg:
                messages.append(HumanMessage(content=user_msg))
            if assistant_msg:
                messages.append(AIMessage(content=assistant_msg))
    return messages

# Make this function an async generator
async def chatbot_interface(message, history):
    # 'history' here will be in the new 'messages' format (list of dicts)
    history = history or []

    # Append the user message to history immediately in the new format
    user_message_dict = {"role": "user", "content": message}
    history.append(user_message_dict)

    # Initialize assistant's response as an empty string placeholder
    assistant_message_dict = {"role": "assistant", "content": ""}
    history.append(assistant_message_dict)

    # Yield initial state to update the UI with user's message and a placeholder for assistant
    yield history

    # Convert Gradio history (excluding the current user's message and assistant's placeholder)
    # to LangChain format for the agent's chat_history.
    lc_messages = format_chat_history(history[:-2])

    current_response_content = ""
    try:
        # *** KEY CHANGE: Use async for to iterate over the async generator ***
        async for chunk in stream_chat_agent({"input": message, "chat_history": lc_messages}):
            if "output" in chunk:
                current_response_content = chunk["output"]
                # Update the content of the last assistant message dictionary in-place
                history[-1]["content"] = current_response_content
                yield history # Yield the updated history for Gradio to refresh
            elif "error" in chunk:
                history[-1]["content"] = chunk["error"] # Set the last assistant message to the error
                yield history
                return # Stop processing on error
    except Exception as e:
        # Catch any unexpected errors within this interface function
        history[-1]["content"] = f"❌ Gradio interface error: {str(e)}"
        yield history


with gr.Blocks() as demo:
    gr.Markdown("# 📊 10-K Intelligence Chat with Streaming")

    # Specify type='messages' for the chatbot component
    chatbot = gr.Chatbot(height=400, type='messages')

    with gr.Row():
        msg = gr.Textbox(
            placeholder="Ask me about a company...",
            container=False,
            scale=7
        )
        clear = gr.Button("Clear", scale=1)

    # When submitting, call the async `chatbot_interface`
    # Gradio automatically handles awaiting async functions when they are generators.
    msg.submit(chatbot_interface, inputs=[msg, chatbot], outputs=chatbot, concurrency_limit=None)
    clear.click(lambda: [], outputs=chatbot, queue=False)

if __name__ == "__main__":
    demo.launch()