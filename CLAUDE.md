# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides Reddit content fetching capabilities. It's written in Python using the FastMCP framework and redditwarp library for Reddit API access.

## Development Commands

### Installation and Setup
- `uv install` - Install dependencies using the uv package manager
- Copy `example.env` to `.env` and add your Reddit API credentials:
  - `REDDIT_CLIENT_ID` - Your Reddit app client ID
  - `REDDIT_CLIENT_SECRET` - Your Reddit app client secret
  - `REDDIT_REFRESH_TOKEN` (optional) - For more advanced authentication

### Running the Server
- `uvx --from . mcp-reddit` - Run the MCP server directly
- The entry point is defined in pyproject.toml as `mcp_reddit.reddit_fetcher:mcp.run`

### Development Environment
- This project uses `devenv` (Nix-based development environment)
- `devenv shell` - Enter the development shell with all dependencies

## Architecture

### Core Components

**Entry Point**: `src/mcp_reddit/reddit_fetcher.py`
- Single file containing all MCP tool implementations
- Uses FastMCP framework for MCP protocol handling
- Uses redditwarp async client for Reddit API access

**Key Dependencies**:
- `fastmcp` - MCP protocol implementation
- `redditwarp` - Async Reddit API client  
- `dnspython` - DNS resolution utilities
- `praw` - Python Reddit API wrapper (secondary)

### MCP Tools Available

The server exposes 8 MCP tools:
1. `fetch_reddit_hot_threads` - Get hot posts from subreddit
2. `fetch_reddit_new_threads` - Get new posts from subreddit  
3. `get_post_details` - Get full post with comment tree
4. `search_posts` - Global Reddit search
5. `search_subreddit` - Search within specific subreddit
6. `search_multiple_subreddits` - Search across multiple subreddits
7. `get_user_content` - Get user posts/comments
8. `get_trending_subreddits` - Get popular subreddits

### Code Patterns

**Error Handling**: All tools use try/catch with detailed logging and return error strings rather than raising exceptions.

**Logging**: Comprehensive logging using Python's logging module with DEBUG level detail for API calls.

**API Client**: Single global `client` instance of redditwarp's async Client, initialized with available credentials.

**Content Processing**: Helper functions `_get_post_type()`, `_get_content()`, and `_format_comment_tree()` handle different Reddit post types and comment threading.

## Reddit API Authentication

Requires Reddit application credentials. Create app at https://www.reddit.com/prefs/apps and use "script" or "web app" type. The client supports multiple authentication modes based on available environment variables.

## Installation Methods

- **Smithery**: `npx -y @smithery/cli install @adhikasp/mcp-reddit --client claude`
- **Manual**: Configure Claude Desktop with uvx command and environment variables
- **Development**: Clone repo and use `uvx --from . mcp-reddit`