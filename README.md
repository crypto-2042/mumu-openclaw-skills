# MuMu OpenClaw Agent Skills

This repository provides a set of highly automated **Agentic AI skills** allowing [OpenClaw](https://github.com/openclaw/openclaw) or other autonomous agents to manage and write entire novels using the [MuMuAINovel](https://github.com/MuMuAINovel/MuMuAINovel) backend.

With these skills, an agent transitions from being a simple text generator into a full **Showrunner/Editor-in-Chief**. It can maintain lore consistency, trigger background story-arc generation, read un-audited chapters, audit them using global memory RAG, and push massive rewrites.

## 📦 Directory Structure

```text
mumu-agent-skills/
├── README.md               # This documentation
├── SKILL.md                # System metadata & behavior injection for OpenClaw
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── mumu_agent/             # Core scripts for the agent
    ├── client.py           # Authenticated API Client with automatic session management
    ├── bind_project.py     # Create / Link novel projects & Fix writing styles
    ├── generate_outline.py # Brainstorm & stream new outlines via SSE plot expansion
    ├── trigger_batch.py    # Trigger remote batch-generation with automatic start-range detection
    ├── fetch_unaudited.py  # Retrieve drafts that require review
    ├── analyze_chapter.py  # Run RAG analysis vs existing continuity
    ├── review_chapter.py   # Final overwrite or immediate pass for draft chapters
    ├── check_foreshadows.py# Pull unresolved foreshadows & memory hooks
    └── manage_memory.py    # Manually assert or reject memory nodes
```

## 🚀 Quick Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env` and configure your MuMuAINovel backend credentials.
   ```bash
   cp .env.example .env
   ```
   *Note: `MUMU_PROJECT_ID` and `MUMU_STYLE_ID` will be automatically injected by the Agent during initialization. You do NOT have to write them manually.*

## 🤖 How the Agent "Lives" (Workflow)

If you are setting up an OpenClaw Agent, simply attach `SKILL.md` to its initialization prompt. The agent will execute following these guidelines:

### Phase 1: Creation & Binding
The AI creates a new fictional universe (world building, career paths, character sheets) securely pinning them to its local state lock `(.env)`.
```bash
# Example action the agent will run:
python -m mumu_agent.bind_project --action create \
  --title "Cyber Dawn" \
  --description "A story about a rogue AI" \
  --theme "Survival" \
  --genre "Sci-Fi"
```

### Phase 2: The Writing Loop (Infinite Generation)
Once the novel is bound, the agent will loop the following cognitive steps ad-infinitum:

1. **Check Loose Ends:** 
   `python -m mumu_agent.check_foreshadows --action list-pending`
   *Agent realizes a gun was shown in chapter 2 and hasn't fired yet.*

2. **Generate Plot Outlines:** 
   `python -m mumu_agent.generate_outline --count 5`

3. **Batch Write:** 
   `python -m mumu_agent.trigger_batch --count 5`
   *This fires off the LLM engine and tells the MuMu backend to process RAG analysis immediately after.*

4. **Inbox Review:** 
   `python -m mumu_agent.fetch_unaudited`
   *Agent retrieves the completed draft of the chapter.*

5. **Approval or Execution:** 
   `python -m mumu_agent.review_chapter --action rewrite --chapter_id <ID> --file rewrite.md`
   *Agent pushes a total rewrite into the server and publishes it!*

## 📜 License
GPL-3.0 License. See the main MuMuAINovel project for more details.
