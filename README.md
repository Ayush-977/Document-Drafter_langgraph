"# Drafter-py_langgraph"

# Drafter-py_langgraph

A minimal **LangGraph**-powered document drafting assistant. It uses a Gemini model via `langchain_google_genai` and two tools—`update` and `save`—to edit an in-memory document and optionally write it to a `.txt` file.

---

## 📌 Overview

This project wires a simple agent graph with:

- **State** that stores a running list of messages.
- **Tools**:
  - `update(content: str)` — replace the current document content.
  - `save(filename: str)` — write the current content to a text file and end.
- **LLM**: `ChatGoogleGenerativeAI(model="gemini-2.5-flash")` bound to the tools, so the model can decide when to call them.
- **Graph**: `StateGraph` + `ToolNode` with conditional edges to **continue** or **end** based on tool results.

> The document is kept in a module-level variable `document_content`. Each tool call updates/reads from it.

---

## 🧩 Key Features

- **Tool-enabled agent** (LangChain + LangGraph): the LLM can call `update` and `save`.
- **Interactive CLI loop**: prompts you for actions and displays recent tool results.
- **Deterministic exit**: the graph ends after a successful `save`.

---

## 🛠️ Architecture & Flow

```
+-----------------+         +-----------------+         +-----------------+
|  Agent (LLM)    |  --->   |  ToolNode       |  --->   |  should_continue|
|  - system prompt|         |  - update/save  |         |  - end/continue |
+-----------------+         +-----------------+         +-----------------+
        ^                                                            |
        |                                                            v
        +---------------------------- continue ----------------------+
```

- **System prompt** primes the assistant with the current document state.
- **Agent** produces an `AIMessage`; when tools are called, `ToolNode` executes them.
- **Conditional edge** checks the latest `ToolMessage` to **end** after `save`.

---

## ✅ Prerequisites

- **Python 3.10+**
- A **Google API key** for Gemini models
- Packages:
  - `langgraph`, `langchain-core`, `langchain-google-genai`
  - `python-dotenv`

> The code calls `load_dotenv()` so you can keep secrets in a local `.env` file.

---

## ⚙️ Setup

```bash
# Clone
git clone https://github.com/Ayush-977/Drafter-py_langgraph.git
cd Drafter-py_langgraph

# (Recommended) Create a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

If you don't have a `requirements.txt` yet, this minimal set should work:

```txt
langgraph
langchain-core
langchain-google-genai
python-dotenv
```

---

## 🔐 Configuration

Create a `.env` file at the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

- The `ChatGoogleGenerativeAI` client will use this key.
- If the key is missing or invalid, the model invocation will fail.

---

## ▶️ Run

```bash
python main.py
```

You should see:

```
==== DRAFTER ====
```

The program streams the graph and prints recent **tool results**. After the first cycle, it prompts:

```
What would you like to do with the document? (e.g., Update: <content> | Save: <filename>)
>
```

---

## 🧪 Usage Examples

**1) Update the document**

```
> Update: Draft a 2-paragraph summary about LangGraph agents.
```

- The LLM is expected to call the `update` tool with the full content.
- You’ll see a tool result similar to:

```
TOOL RESULT: Document has been successfully updated!

Current content:
Draft a 2-paragraph summary about LangGraph agents.
```

**2) Save and finish**

```
> Save: my_notes.txt
```

- The `save` tool will write the current content to `my_notes.txt`.
- The graph transitions to **END** and the program prints:

```
==== DRAFTER FINISHED ====
```

> Note: If you omit `.txt`, the tool appends it automatically.

---

## 📂 Output

- Files saved via `save(filename)` are created in your **current working directory**.
- The console also prints a confirmation path: `Document has been saved to: <filename>.`

---

## 🧱 Project Structure (suggested)

```
Drafter-py_langgraph/
├── main.py                  # The provided agent code
├── tools.py                 # (Optional) Move tool definitions here
├── requirements.txt         # Python deps
├── .env                     # GOOGLE_API_KEY (not committed)
└── README.md                # This file
```

---

## 🪄 Extending the Agent

- **Add new tools** — define with `@tool` and include in the `tools` list.
- **Adjust routing** — modify `should_continue` to add new end conditions.
- **Persist state** — replace the module-level `document_content` with a store (DB/file).
- **Improve prompts** — extend the system prompt with instructions and style guides.

---

## 🧰 Troubleshooting

- **`GOOGLE_API_KEY` missing/invalid**: Ensure your `.env` is loaded and the key is active.
- **Model errors / rate limits**: Check Google Generative AI quota and model availability.
- **File write permission errors**: Run from a directory where you have write access; verify filename.

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-idea`
3. Commit: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-idea`
5. Open a Pull Request

---

## 📜 License

MIT License — feel free to use and modify.
