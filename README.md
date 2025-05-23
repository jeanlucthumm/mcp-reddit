# MCP Reddit Server
[![smithery badge](https://smithery.ai/badge/@adhikasp/mcp-reddit)](https://smithery.ai/server/@adhikasp/mcp-reddit)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that provides comprehensive tools for fetching and analyzing Reddit content.

<a href="https://glama.ai/mcp/servers/3cg9gdyors"><img width="380" height="200" src="https://glama.ai/mcp/servers/3cg9gdyors/badge" alt="mcp-reddit MCP server" /></a>

## Features

- **Subreddit Content**: Fetch hot, new, and top threads from any subreddit
- **Post Details**: Get detailed post content including full comment trees
- **Search Capabilities**: Search across Reddit globally or within specific subreddits
- **Multi-Subreddit Search**: Search across multiple subreddits simultaneously
- **User Content**: Retrieve user posts and comments
- **Trending Discovery**: Get currently trending subreddits
- **Multiple Post Types**: Support for text, link, and gallery posts
- **Flexible Sorting**: Sort by hot, new, top, relevance, and more
- **Time Filtering**: Filter content by time periods (hour, day, week, month, year, all)

## Prerequisites

This server requires Reddit API credentials to function. You'll need to:

1. Create a Reddit application at https://www.reddit.com/prefs/apps
2. Choose "script" or "web app" as the application type
3. Note your client ID and client secret

## Installation

### Installing via Smithery

To install Reddit Content for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@adhikasp/mcp-reddit):

```bash
npx -y @smithery/cli install @adhikasp/mcp-reddit --client claude
```

### Manual Installation

Add to your Claude Desktop configuration file:

```json
{
  "reddit": {
    "command": "uvx",
    "args": ["--from", "git+https://github.com/adhikasp/mcp-reddit.git", "mcp-reddit"],
    "env": {
      "REDDIT_CLIENT_ID": "your_client_id_here",
      "REDDIT_CLIENT_SECRET": "your_client_secret_here"
    }
  }
}
```

### Environment Variables

Create a `.env` file in your project directory with your Reddit API credentials:

```env
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
```

## Available Tools

### `fetch_reddit_hot_threads`
Fetch hot threads from a subreddit.

**Parameters:**
- `subreddit` (string): Name of the subreddit
- `limit` (int, optional): Number of posts to fetch (default: 10)

### `fetch_reddit_new_threads`
Fetch new/recent threads from a subreddit.

**Parameters:**
- `subreddit` (string): Name of the subreddit
- `limit` (int, optional): Number of posts to fetch (default: 10)

### `get_post_details`
Get detailed post content including full comment tree.

**Parameters:**
- `post_id` (string): Reddit post ID
- `comment_limit` (int, optional): Number of top-level comments to fetch (default: 100)
- `comment_sort` (string, optional): How to sort comments - "best", "top", "new", "controversial", "old", "qa", "random" (default: "best")

### `search_posts`
Search Reddit posts globally.

**Parameters:**
- `query` (string): The search query string
- `subreddit` (string, optional): Optional subreddit to search within
- `sort` (string, optional): Sort method - "relevance", "hot", "top", "new" (default: "relevance")
- `time_filter` (string, optional): Time filter - "hour", "day", "week", "month", "year", "all" (default: "all")
- `limit` (int, optional): Number of posts to fetch (default: 25)

### `search_subreddit`
Search within specific subreddits or get recent posts.

**Parameters:**
- `subreddit` (string): The name of the subreddit to search within
- `query` (string, optional): The search query string. If empty, returns recent posts based on sort method
- `sort` (string, optional): Sort method - "hot", "top", "new", "relevance" (default: "hot")
- `time_filter` (string, optional): Time filter - "hour", "day", "week", "month", "year", "all" (default: "week")
- `limit` (int, optional): Number of posts to fetch (default: 25)

### `search_multiple_subreddits`
Search across multiple subreddits simultaneously.

**Parameters:**
- `subreddits` (list[string]): A list of subreddit names to search within
- `query` (string): The search query string
- `sort` (string, optional): Sort method - "relevance", "hot", "top", "new" (default: "relevance")
- `time_filter` (string, optional): Time filter - "hour", "day", "week", "month", "year", "all" (default: "all")
- `limit` (int, optional): Number of posts to fetch (default: 25)

### `get_user_content`
Get user posts or comments.

**Parameters:**
- `username` (string): The Reddit username
- `content_type` (string, optional): Type of content to fetch - "posts" or "comments" (default: "posts")
- `limit` (int, optional): Number of items to fetch (default: 25)

### `get_trending_subreddits`
Get currently trending subreddits.

**Parameters:**
- `limit` (int, optional): Number of trending subreddits to fetch (default: 10)

## Usage

Using [mcp-client-cli](https://github.com/adhikasp/mcp-client-cli):

```
$ llm what are latest hot thread in r/victoria3

I'll fetch the latest hot threads from the Victoria 3 subreddit for you.

Tool Calls:
  fetch_hot_threads
  Args:
    subreddit: victoria3


Based on the hot threads, here are the key highlights from the Victoria 3 subreddit:

1. Dev Diary #126 - Update 1.8 Overview
   - Major updates planned for the game, including:
     - Political Movement Rework (Ideological Forces)
     - Discrimination Rework
     - Food Availability, Famines, and Harvest Incidents
     - Additional features like Companies owning buildings and Bulk Nationalization

2. Dev Diary #138 - Pivot of Empire Update
   - Update 1.8 "Masala Chai" has been released
   - Focuses on India with new Journal Entries, Events, and Immersion Pack
   - 10 new achievements added
   - Save games from 1.7.7 are not compatible with 1.8

3. Interesting Community Discussions:
   - A player shared a detailed experience of retaking Constantinople as Greece, highlighting the complex population dynamics
   - Humorous posts about game mechanics, such as investment rights and political movements
   - Various memes and gameplay screenshots showcasing unique game situations

The most upvoted thread is the Dev Diary #126, which provides an in-depth look at the upcoming game mechanics improvements, particularly the reworks to political movements and discrimination systems.

Would you like me to elaborate on any of these points or provide more details about the Victoria 3 update?
```
