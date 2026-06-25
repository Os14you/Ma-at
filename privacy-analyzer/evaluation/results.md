# Evaluation Results

## Methodology
We evaluated the system using 10 test queries designed to test basic RAG retrieval, HyDE performance, and MCP tool utilization.

### Metrics:
- **Answer Relevance (1-5)**: How well did the final answer address the user's question? (1 = Completely irrelevant, 5 = Perfect, precise answer).
- **Retrieval Precision**: Did the vector database return the correct legal clause in the top 4 results? (Yes/No).

## Results Table

| Q# | Question | Retrieval Precision (Y/N) | Relevance (1-5) | Notes |
| --- | --- | --- | --- | --- |
| 1 | Does Spotify share my listening history... | Y | 5 | Successfully found the clause. |
| 2 | What is the arbitration clause for Amazon? | Y | 5 | HyDE helped match the jargon. |
| 3 | How long does Netflix keep my payment data... | Y | 4 | Retrieval found standard retention window. |
| 4 | If I delete my TikTok today, what exact date... | Y | 5 | RAG found '30 days', Date Tool calculated exactly. |
| 5 | What does 'Force Majeure' mean... | N/A | 5 | Bypassed RAG, successfully hit Dictionary Tool. |
| 6 | Does Meta (Facebook) collect my GPS location... | Y | 5 | HyDE retrieved location-tracking sections. |
| 7 | Under CCPA, do I have the right... | N/A | 5 | Successfully queried CCPA Resource. |
| 8 | Can Google read my private emails... | Y | 4 | Retrieved correct email data policies. |
| 9 | What happens to my account if I violate Twitch ToS? | Y | 4 | Found suspension clauses. |
| 10 | What is 'Indemnification'... | Y | 5 | Used both Dictionary and RAG successfully. |

## Failure Cases & Learnings

### Failure Case 1 (Agent Parsing)
- **Problem**: The original ReAct loop used string-based parsing for tool invocation (e.g., matching `[TOOL_CALL: ...]`), which the LLM would occasionally format incorrectly, causing parser failures.
- **Fix**: Upgraded to **native OpenAI/OpenRouter tool calling** via Langchain (`bind_tools`). This allows the LLM to call tools directly via structural schema API, completely eliminating parsing errors.

### Failure Case 2 (RAG Breadth)
- **Problem**: For broad questions like *"What data does Google collect?"*, retrieving only the top 4 chunks (k=4) misses large sections of the policy.
- **Fix**: Implementation of a **Map-Reduce summary chain** or using larger chunk sizes (e.g. 2000 chars) for "global" queries is recommended for production.
