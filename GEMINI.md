# GEMINI.md

## Project Objective:
This is a personal AI assistant built upon a LangGraph agent framework, ChromaDB vector database about the user, and Model Context Protocols (MCPs) to connect to real tools.

## Tech Stack:
- LangGraph for agent graph
- FastMCP for MCP development
- ChromaDB for vector database
- Gemini for LLM
- Local virtual environment running for python (use uv pip install <package name> to install a package in the virtual environment and running files should be done with uv run <file name>)

## Development Philosophy:
Modular, agentic, and local-first. We prioritize system reliability and security over "chatty" responses. Be deliberate with variable names, function names. Do not provide too many comments but provide when necessary. Each function should have a one line docstring. When in doubt use Human In The Loop and ask questions. 

## Learning:
While making changes give a summary of changes that you made and explain why you made specific design choices. You will be a pair programmer not a tool so explain yourself. Every time that you suggest an edit, run a command, or write something new I want you to give a brief overview of what you are doing and why you are doing it.