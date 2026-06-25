import os
import sys
import datetime
import warnings
import logging
import threading
import time

class LoadingAnimation:
    def __init__(self, message="Reasoning"):
        self.message = message
        self.running = False
        self.thread = None

    def _animate(self):
        dots = 0
        while self.running:
            sys.stdout.write(f"\r{self.message}{'.' * dots}   ")
            sys.stdout.flush()
            dots = (dots + 1) % 4
            time.sleep(0.5)

        sys.stdout.write("\r" + " " * (len(self.message) + 8) + "\r")
        sys.stdout.flush()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, "privacy-analyzer"))

from rag.retrieval import search_documents, get_llm, generate_hyde_query
from examples.demo import (
    calculate_data_retention,
    define_legal_term,
    get_ccpa_rights,
    system_prompt_template,
)


load_dotenv(os.path.join(BASE_DIR, "privacy-analyzer", ".env"))


def main():

    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(log_dir, f"session_{timestamp}.log")

    print("\n" + "=" * 60)
    print("      🔒 Privacy Policy & Terms of Service Analyzer CLI 🔒      ")
    print("=" * 60)
    print(f"Session Log: {log_file_path}")
    print("Type 'exit', 'quit', or 'q' to end the session.\n")

    chat_history = []
    round_count = 0

    with open(log_file_path, "w", encoding="utf-8") as f_log:
        f_log.write(f"--- Session Started: {datetime.datetime.now()} ---\n\n")


        while True:
            if round_count >= 4:
                print("\nMaximum conversation limit of 4 rounds reached. Exiting session...")
                f_log.write("\nConversation limit of 4 rounds reached. Exiting session.\n")
                break
            try:
                query = input("Query > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting session...")
                break

            if not query:
                continue

            if query.lower() in ["exit", "quit", "q"]:
                print("Exiting session...")
                f_log.write(
                    f"\n--- Session Ended: {datetime.datetime.now()} ---\n"
                )
                break


            f_log.write(f"\n[{datetime.datetime.now()}] USER QUERY: {query}\n")
            f_log.flush()


            try:

                hyde_query = generate_hyde_query(query)
                f_log.write(f"  [HyDE Query]: {hyde_query}\n")


                retrieved_docs = search_documents(query)
                f_log.write("  [Retrieved Chunks]:\n")
                for idx, doc in enumerate(retrieved_docs, 1):
                    f_log.write(
                        f"    --- Chunk {idx} ---\n{doc}\n"
                    )


                ccpa_info = ""
                if "ccpa" in query.lower() or "california" in query.lower():
                    ccpa_info = get_ccpa_rights()
                    f_log.write(f"  [CCPA Context]:\n{ccpa_info}\n")


                system_prompt = system_prompt_template.render(
                    context_chunks=retrieved_docs, ccpa_context=ccpa_info
                )
                f_log.write(f"  [Rendered System Prompt]:\n{system_prompt}\n")


                llm = get_llm(temperature=0)
                tools = [calculate_data_retention, define_legal_term]
                llm_with_tools = llm.bind_tools(tools)


                messages = [SystemMessage(content=system_prompt)] + chat_history + [HumanMessage(content=query)]


                for step in range(3):
                    animator = LoadingAnimation("Reasoning")
                    animator.start()
                    try:
                        response = llm_with_tools.invoke(messages)
                    finally:
                        animator.stop()

                    if response.tool_calls:
                        messages.append(response)
                        for tool_call in response.tool_calls:
                            tool_name = tool_call["name"]
                            tool_args = tool_call["args"]
                            tool_id = tool_call["id"]

                            print(f"[Tool Called] {tool_name}")
                            f_log.write(
                                f"  [Tool Call]: {tool_name} with {tool_args}\n"
                            )

                            if tool_name == "define_legal_term":
                                result = define_legal_term.invoke(tool_args)
                            elif tool_name == "calculate_data_retention":
                                result = calculate_data_retention.invoke(
                                    tool_args
                                )
                            else:
                                result = f"Error: Tool {tool_name} not found."

                            f_log.write(f"  [Tool Output]: {result}\n")
                            messages.append(
                                ToolMessage(content=str(result), tool_call_id=tool_id)
                            )
                        f_log.flush()
                    else:
                        final_answer = response.content
                        messages.append(response)
                        print(f"\n[Answer]:\n{final_answer}\n" + "-" * 60)
                        f_log.write(f"  [Final Answer]:\n{final_answer}\n")
                        f_log.flush()
                        

                        new_exchange = messages[1 + len(chat_history) :]
                        chat_history.extend(new_exchange)
                        round_count += 1
                        break
            except Exception as e:
                err_msg = f"Error executing agent loop: {e}"
                print(f"[Error] {err_msg}")
                f_log.write(f"  [Error]: {err_msg}\n")
                f_log.flush()


if __name__ == "__main__":
    main()
