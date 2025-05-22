import os
from typing import Optional
from redditwarp.ASYNC import Client
from redditwarp.models.submission_ASYNC import LinkPost, TextPost, GalleryPost
from fastmcp import FastMCP
import logging

mcp = FastMCP("Reddit MCP")

REDDIT_CLIENT_ID=os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET=os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_REFRESH_TOKEN=os.getenv("REDDIT_REFRESH_TOKEN")

CREDS = [x for x in [REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REFRESH_TOKEN] if x]

client = Client(*CREDS)
logging.getLogger().setLevel(logging.WARNING)

@mcp.tool()
async def fetch_reddit_hot_threads(subreddit: str, limit: int = 10) -> str:
    """
    Fetch hot threads from a subreddit

    Args:
        subreddit: Name of the subreddit
        limit: Number of posts to fetch (default: 10)

    Returns:
        Human readable string containing list of post information
    """
    try:
        posts = []
        async for submission in client.p.subreddit.pull.hot(subreddit, limit):
            post_info = (
                f"Title: {submission.title}\n"
                f"Score: {submission.score}\n"
                f"Comments: {submission.comment_count}\n"
                f"Author: {submission.author_display_name or '[deleted]'}\n"
                f"Type: {_get_post_type(submission)}\n"
                f"Content: {_get_content(submission)}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
                f"---"
            )
            posts.append(post_info)

        return "\n\n".join(posts)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return f"An error occurred: {str(e)}"

def _format_comment_tree(comment_node, depth: int = 0) -> str:
    """Helper method to recursively format comment tree with proper indentation"""
    comment = comment_node.value
    indent = "-- " * depth
    content = (
        f"{indent}* Author: {comment.author_display_name or '[deleted]'}\n"
        f"{indent}  Score: {comment.score}\n"
        f"{indent}  {comment.body}\n"
    )

    for child in comment_node.children:
        content += "\n" + _format_comment_tree(child, depth + 1)

    return content

@mcp.tool()
async def get_post_details(post_id: str, comment_limit: int = 100, comment_sort: str = "best") -> str:
    """
    Get post details with full comments.

    Args:
        post_id: Reddit post ID.
        comment_limit: Number of top-level comments to fetch (default: 100).
        comment_sort: How to sort comments (e.g., "best", "top", "new", "controversial", "old", "qa", "random").

    Returns:
        Human readable string containing post content and comments tree.
    """
    try:
        submission = await client.p.submission.fetch(post_id)

        content = (
            f"Title: {submission.title}\n"
            f"Score: {submission.score}\n"
            f"Author: {submission.author_display_name or '[deleted]'}\n"
            f"Type: {_get_post_type(submission)}\n"
            f"Content: {_get_content(submission)}\n"
            f"Link: https://reddit.com{submission.permalink}\n"
        )

        comments = await client.p.comment_tree.fetch(post_id, sort=comment_sort, limit=comment_limit)
        if comments.children:
            content += "\nComments:\n"
            for comment in comments.children:
                content += "\n" + _format_comment_tree(comment)
        else:
            content += "\nNo comments found."

        return content

    except Exception as e:
        logging.error(f"An error occurred during get_post_details: {str(e)}")
        return f"An error occurred: {str(e)}"

def _get_post_type(submission) -> str:
    """Helper method to determine post type"""
    if isinstance(submission, LinkPost):
        return 'link'
    elif isinstance(submission, TextPost):
        return 'text'
    elif isinstance(submission, GalleryPost):
        return 'gallery'
    return 'unknown'

def _get_content(submission) -> Optional[str]:
    """Helper method to extract post content based on type"""
    if isinstance(submission, LinkPost):
        return submission.permalink
    elif isinstance(submission, TextPost):
        return submission.body
    elif isinstance(submission, GalleryPost):
        return str(submission.gallery_link)
    return None

@mcp.tool()
async def search_posts(query: str, subreddit: Optional[str] = None, sort: str = "relevance", time_filter: str = "all", limit: int = 25) -> str:
    """
    Search Reddit posts.

    Args:
        query: The search query string.
        subreddit: Optional name of the subreddit to search within.
        sort: How to sort the results (e.g., "relevance", "hot", "top", "new").
        time_filter: Filter results by time (e.g., "hour", "day", "week", "month", "year", "all").
        limit: Number of posts to fetch (default: 25).

    Returns:
        Human readable string containing a list of post information.
    """
    try:
        posts = []
        search_params = {
            'q': query,
            'sort': sort,
            't': time_filter,
            'limit': limit
        }
        if subreddit:
            search_params['subreddit'] = subreddit

        async for submission in client.p.search(**search_params):
            post_info = (
                f"Title: {submission.title}\n"
                f"Score: {submission.score}\n"
                f"Comments: {submission.comment_count}\n"
                f"Author: {submission.author_display_name or '[deleted]'}\n"
                f"Type: {_get_post_type(submission)}\n"
                f"Content: {_get_content(submission)}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
                f"---"
            )
            posts.append(post_info)

        if not posts:
            return "No posts found matching your criteria."
        return "\n\n".join(posts)

    except Exception as e:
        logging.error(f"An error occurred during search_posts: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
async def search_subreddit(subreddit: str, query: str, sort: str = "hot", time_filter: str = "week", limit: int = 25) -> str:
    """
    Search within specific subreddits.

    Args:
        subreddit: The name of the subreddit to search within.
        query: The search query string.
        sort: How to sort the results (e.g., "hot", "top", "new", "relevance").
        time_filter: Filter results by time (e.g., "hour", "day", "week", "month", "year", "all").
        limit: Number of posts to fetch (default: 25).

    Returns:
        Human readable string containing a list of post information.
    """
    try:
        posts = []
        search_params = {
            'q': query,
            'sort': sort,
            't': time_filter,
            'limit': limit
        }

        async for submission in client.p.subreddit.search(subreddit, **search_params):
            post_info = (
                f"Title: {submission.title}\n"
                f"Score: {submission.score}\n"
                f"Comments: {submission.comment_count}\n"
                f"Author: {submission.author_display_name or '[deleted]'}\n"
                f"Type: {_get_post_type(submission)}\n"
                f"Content: {_get_content(submission)}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
                f"---"
            )
            posts.append(post_info)

        if not posts:
            return f"No posts found in r/{subreddit} matching your criteria."
        return "\n\n".join(posts)

    except Exception as e:
        logging.error(f"An error occurred during search_subreddit: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
async def get_user_content(username: str, content_type: str = "posts", limit: int = 25) -> str:
    """
    Get user posts/comments.

    Args:
        username: The Reddit username.
        content_type: Type of content to fetch ("posts" or "comments").
        limit: Number of items to fetch (default: 25).

    Returns:
        Human readable string containing a list of user content.
    """
    try:
        user_content = []
        if content_type == "posts":
            async for submission in client.p.redditor.pull.submitted(username, limit=limit):
                post_info = (
                    f"Title: {submission.title}\n"
                    f"Score: {submission.score}\n"
                    f"Comments: {submission.comment_count}\n"
                    f"Type: {_get_post_type(submission)}\n"
                    f"Content: {_get_content(submission)}\n"
                    f"Link: https://reddit.com{submission.permalink}\n"
                    f"---"
                )
                user_content.append(post_info)
            if not user_content:
                return f"No posts found for user u/{username}."
            return f"Posts by u/{username}:\n\n" + "\n\n".join(user_content)
        elif content_type == "comments":
            async for comment in client.p.redditor.pull.comments(username, limit=limit):
                comment_info = (
                    f"Post ID: {comment.link_id.removeprefix('t3_')}\n"
                    f"Score: {comment.score}\n"
                    f"Content: {comment.body}\n"
                    f"Link: https://reddit.com{comment.permalink}\n"
                    f"---"
                )
                user_content.append(comment_info)
            if not user_content:
                return f"No comments found for user u/{username}."
            return f"Comments by u/{username}:\n\n" + "\n\n".join(user_content)
        else:
            return "Invalid content_type. Must be 'posts' or 'comments'."

    except Exception as e:
        logging.error(f"An error occurred during get_user_content: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
async def get_trending_subreddits(limit: int = 10) -> str:
    """
    Get trending subreddits.

    Args:
        limit: Number of trending subreddits to fetch (default: 10).

    Returns:
        Human readable string containing a list of trending subreddit names.
    """
    try:
        trending_subs = []
        async for subreddit in client.p.subreddit.pull.trending(limit=limit):
            trending_subs.append(subreddit.display_name)

        if not trending_subs:
            return "No trending subreddits found."
        return "Trending Subreddits:\n" + "\n".join(trending_subs)

    except Exception as e:
        logging.error(f"An error occurred during get_trending_subreddits: {str(e)}")
        return f"An error occurred: {str(e)}"

@mcp.tool()
async def search_multiple_subreddits(subreddits: list[str], query: str, sort: str = "relevance", time_filter: str = "all", limit: int = 25) -> str:
    """
    Multi-reddit search.

    Args:
        subreddits: A list of subreddit names to search within.
        query: The search query string.
        sort: How to sort the results (e.g., "relevance", "hot", "top", "new").
        time_filter: Filter results by time (e.g., "hour", "day", "week", "month", "year", "all").
        limit: Number of posts to fetch (default: 25).

    Returns:
        Human readable string containing a list of post information.
    """
    try:
        posts = []
        subreddit_string = "+".join(subreddits)
        search_params = {
            'q': query,
            'sort': sort,
            't': time_filter,
            'limit': limit,
            'subreddit': subreddit_string
        }

        async for submission in client.p.search(**search_params):
            post_info = (
                f"Title: {submission.title}\n"
                f"Score: {submission.score}\n"
                f"Comments: {submission.comment_count}\n"
                f"Author: {submission.author_display_name or '[deleted]'}\n"
                f"Type: {_get_post_type(submission)}\n"
                f"Content: {_get_content(submission)}\n"
                f"Link: https://reddit.com{submission.permalink}\n"
                f"---"
            )
            posts.append(post_info)

        if not posts:
            return f"No posts found in subreddits {', '.join(subreddits)} matching your criteria."
        return "\n\n".join(posts)

    except Exception as e:
        logging.error(f"An error occurred during search_multiple_subreddits: {str(e)}")
        return f"An error occurred: {str(e)}"
