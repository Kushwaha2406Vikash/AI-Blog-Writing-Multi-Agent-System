# AI Blog Writing Multi-Agent System

An enterprise-ready **Multi-agent AI system** designed for automated, high-quality blog generation. By integrating real-time web research, strategic planning, and automated drafting, this system **cuts blog writing time by up to 60%**.

Built with **LangGraph** and **Gemini LLM**, the application features a sophisticated orchestration layer that mimics a professional editorial team's workflow.

---

## 🚀 Features

* **Intelligent Routing**: Automatically decides if a topic requires fresh web research before planning.
* **Web Research Integration**: Synthesizes raw search results into deduplicated, fact-based evidence.
* **Structured Planning**: Generates comprehensive outlines to ensure logical flow and technical depth.
* **Multi-Agent Drafting**: Distributes writing tasks across worker nodes and merges them into a single cohesive Markdown file.
* **Full Observability**: Integrated with LangSmith for real-time monitoring and debugging of agentic traces.

---

## 🛠️ Tech Stack

* **Core Framework**: [LangChain](https://www.langchain.com/) & [LangGraph](https://www.langchain.com/langgraph)
* **LLM**: [Google Gemini](https://ai.google.dev/)
* **Backend**: Python
* **Frontend UI**: [Streamlit](https://streamlit.io/)
* **Observability**: [LangSmith](https://www.langchain.com/langsmith)
* **Deployment**: Streamlit Cloud

---

## 🏗️ Architecture & Workflow

The system operates through a series of specialized nodes:

1. **Router Agent**: Determines if the topic needs live web data.
2. **Orchestrator Node (Planning)**: Creates the blueprint for the blog.
3. **Research Node (Web Search)**: Gathers and cleans technical evidence items.
4. **Worker Node (Writing)**: Generates the content based on the plan and research.
5. **Reducer Node (Merging)**: Compiles all drafted sections into a final Markdown preview.

---

## 📂 Project Structure

```text
├── core/             # Core logic and configuration
├── node/             # Individual agent node definitions
├── workflow/         # LangGraph state machine definitions
├── schemas/          # Data models and EvidenceItem objects
├── app.py            # Streamlit UI entry point
├── main.py           # Logic orchestration
└── pyproject.toml    # Dependency management

```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Gemini API Key
* LangChain/LangSmith API Keys (for observability)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/Kushwaha2406Vikash/AI-Blog-Writing-Multi-Agent-System.git
cd AI-Blog-Writing-Multi-Agent-System

```


2. **Install dependencies**:
```bash
pip install toml

```


3. **Run the application**:
```bash
streamlit run main.py

```



---

## 🔗 Links

* **Live Demo**: [Streamlit Cloud](https://ai-blog-writing-multi-agent-system-czmmv96tmnpqnsnyaswxvu.streamlit.app/)
* **Author**: [Kushwaha2406Vikash](https://www.google.com/search?q=https://github.com/Kushwaha2406Vikash)

---

**Would you like me to add a specific section for Environment Variables or detailed contribution guidelines?**

