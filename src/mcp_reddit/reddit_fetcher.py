import os
from typing import Optional
from redditwarp.ASYNC import Client
from redditwarp.models.submission_ASYNC import LinkPost, TextPost, GalleryPost
from fastmcp import FastMCP
import logging

mcp = FastMCP("Reddit MCP")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REDDIT_CLIENT_ID=os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET=os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_REFRESH_TOKEN=os.getenv("REDDIT_REFRESH_TOKEN")

logger.debug(f"Reddit credentials found: CLIENT_ID={'***' if REDDIT_CLIENT_ID else None}, CLIENT_SECRET={'***' if REDDIT_CLIENT_SECRET else None}, REFRESH_TOKEN={'***' if REDDIT_REFRESH_TOKEN else None}")

CREDS = [x for x in [REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_REFRESH_TOKEN] if x]
logger.debug(f"Using {len(CREDS)} credentials for Reddit client")

client = Client(*CREDS)
logger.info("Reddit client initialized successfully")

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
    logger.info(f"fetch_reddit_hot_threads called with subreddit='{subreddit}', limit={limit}")
    try:
        posts = []
        logger.debug(f"Starting to fetch hot posts from r/{subreddit}")
        async for submission in client.p.subreddit.pull.hot(subreddit, limit):
            logger.debug(f"Processing submission: {submission.id} - {submission.title[:50]}")
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

        logger.info(f"Successfully fetched {len(posts)} hot posts from r/{subreddit}")
        return "\n\n".join(posts)

    except Exception as e:
        logger.error(f"Error in fetch_reddit_hot_threads: {str(e)}", exc_info=True)
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
    logger.info(f"get_post_details called with post_id='{post_id}', comment_limit={comment_limit}, comment_sort='{comment_sort}'")
    try:
        logger.debug(f"Fetching submission details for post_id: {post_id}")
        submission = await client.p.submission.fetch(post_id)
        logger.debug(f"Retrieved submission: {submission.title[:50]}")

        content = (
            f"Title: {submission.title}\n"
            f"Score: {submission.score}\n"
            f"Author: {submission.author_display_name or '[deleted]'}\n"
            f"Type: {_get_post_type(submission)}\n"
            f"Content: {_get_content(submission)}\n"
            f"Link: https://reddit.com{submission.permalink}\n"
        )

        logger.debug(f"Fetching comment tree for post_id: {post_id} with sort={comment_sort}, limit={comment_limit}")
        comments = await client.p.comment_tree.fetch(post_id, sort=comment_sort, limit=comment_limit)
        if comments.children:
            logger.debug(f"Found {len(comments.children)} top-level comments")
            content += "\nComments:\n"
            for comment in comments.children:
                content += "\n" + _format_comment_tree(comment)
        else:
            logger.debug("No comments found for this post")
            content += "\nNo comments found."

        logger.info(f"Successfully retrieved post details for {post_id}")
        return content

    except Exception as e:
        logger.error(f"Error in get_post_details for post_id '{post_id}': {str(e)}", exc_info=True)
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
    logger.info(f"search_posts called with query='{query}', subreddit={subreddit}, sort='{sort}', time_filter='{time_filter}', limit={limit}")
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

        logger.debug(f"Search parameters: {search_params}")
        logger.debug(f"Starting search with client.p.submission.search()")
        
        # Use correct redditwarp API: client.p.submission.search(subreddit, query, **params)
        sr = search_params.pop('subreddit', '')
        query = search_params.pop('q')
        sort = search_params.pop('sort', 'relevance')
        time_filter = search_params.pop('t', 'all')
        limit = search_params.pop('limit', 25)
        
        async for submission in client.p.submission.search(sr, query, amount=limit, sort=sort, time=time_filter):
            logger.debug(f"Processing search result: {submission.id} - {submission.title[:50]}")
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
            logger.info(f"No posts found for search query: '{query}'")
            return "No posts found matching your criteria."
        
        logger.info(f"Successfully found {len(posts)} posts for search query: '{query}'")
        return "\n\n".join(posts)

    except Exception as e:
        logger.error(f"Error in search_posts for query '{query}': {str(e)}", exc_info=True)
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
    logger.info(f"search_subreddit called with subreddit='{subreddit}', query='{query}', sort='{sort}', time_filter='{time_filter}', limit={limit}")
    try:
        posts = []
        search_params = {
            'q': query,
            'sort': sort,
            't': time_filter,
            'limit': limit
        }

        search_params['subreddit'] = subreddit
        logger.debug(f"Search parameters for subreddit search: {search_params}")
        logger.debug(f"Calling client.p.submission.search() for subreddit r/{subreddit}")
        
        # Use correct redditwarp API: client.p.submission.search(subreddit, query, **params)
        sr = search_params.pop('subreddit')
        query = search_params.pop('q')
        sort = search_params.pop('sort', 'hot')
        time_filter = search_params.pop('t', 'week')
        limit = search_params.pop('limit', 25)
        
        async for submission in client.p.submission.search(sr, query, amount=limit, sort=sort, time=time_filter):
            logger.debug(f"Processing subreddit search result: {submission.id} - {submission.title[:50]}")
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
            logger.info(f"No posts found in r/{subreddit} for query: '{query}'")
            return f"No posts found in r/{subreddit} matching your criteria."
        
        logger.info(f"Successfully found {len(posts)} posts in r/{subreddit} for query: '{query}'")
        return "\n\n".join(posts)

    except Exception as e:
        logger.error(f"Error in search_subreddit for subreddit '{subreddit}' and query '{query}': {str(e)}", exc_info=True)
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
    logger.info(f"get_user_content called with username='{username}', content_type='{content_type}', limit={limit}")
    try:
        user_content = []
        if content_type == "posts":
            logger.debug(f"Fetching posts for user u/{username}")
            async for submission in client.p.user.pull.submitted(username, amount=limit):
                logger.debug(f"Processing user post: {submission.id} - {submission.title[:50]}")
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
                logger.info(f"No posts found for user u/{username}")
                return f"No posts found for user u/{username}."
            logger.info(f"Successfully fetched {len(user_content)} posts for user u/{username}")
            return f"Posts by u/{username}:\n\n" + "\n\n".join(user_content)
        elif content_type == "comments":
            logger.debug(f"Fetching comments for user u/{username}")
            async for comment in client.p.user.pull.comments(username, amount=limit):
                logger.debug(f"Processing user comment: {comment.id}")
                comment_info = (
                    f"Post ID: {comment.link_id.removeprefix('t3_')}\n"
                    f"Score: {comment.score}\n"
                    f"Content: {comment.body}\n"
                    f"Link: https://reddit.com{comment.permalink}\n"
                    f"---"
                )
                user_content.append(comment_info)
            if not user_content:
                logger.info(f"No comments found for user u/{username}")
                return f"No comments found for user u/{username}."
            logger.info(f"Successfully fetched {len(user_content)} comments for user u/{username}")
            return f"Comments by u/{username}:\n\n" + "\n\n".join(user_content)
        else:
            logger.warning(f"Invalid content_type '{content_type}' provided")
            return "Invalid content_type. Must be 'posts' or 'comments'."

    except Exception as e:
        logger.error(f"Error in get_user_content for user '{username}': {str(e)}", exc_info=True)
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
    logger.info(f"get_trending_subreddits called with limit={limit}")
    try:
        trending_subs = []
        logger.debug(f"Fetching trending subreddits with limit {limit}")
        async for subreddit in client.p.subreddit.pull.popular(limit=limit):
            logger.debug(f"Found trending subreddit: r/{subreddit.display_name}")
            trending_subs.append(subreddit.display_name)

        if not trending_subs:
            logger.info("No trending subreddits found")
            return "No trending subreddits found."
        logger.info(f"Successfully fetched {len(trending_subs)} trending subreddits")
        return "Trending Subreddits:\n" + "\n".join(trending_subs)

    except Exception as e:
        logger.error(f"Error in get_trending_subreddits: {str(e)}", exc_info=True)
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
    logger.info(f"search_multiple_subreddits called with subreddits={subreddits}, query='{query}', sort='{sort}', time_filter='{time_filter}', limit={limit}")
    try:
        posts = []
        subreddit_string = "+".join(subreddits)
        logger.debug(f"Combined subreddit string: {subreddit_string}")
        search_params = {
            'q': query,
            'sort': sort,
            't': time_filter,
            'limit': limit,
            'subreddit': subreddit_string
        }

        logger.debug(f"Multi-subreddit search parameters: {search_params}")
        logger.debug(f"Starting multi-subreddit search with client.p.submission.search()")
        
        # Use correct redditwarp API: client.p.submission.search(subreddit, query, **params)
        sr = search_params.pop('subreddit')
        query = search_params.pop('q')
        sort = search_params.pop('sort', 'relevance')
        time_filter = search_params.pop('t', 'all')
        limit = search_params.pop('limit', 25)
        
        async for submission in client.p.submission.search(sr, query, amount=limit, sort=sort, time=time_filter):
            logger.debug(f"Processing multi-subreddit search result: {submission.id} - {submission.title[:50]}")
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
            logger.info(f"No posts found in subreddits {', '.join(subreddits)} for query: '{query}'")
            return f"No posts found in subreddits {', '.join(subreddits)} matching your criteria."
        
        logger.info(f"Successfully found {len(posts)} posts in {len(subreddits)} subreddits for query: '{query}'")
        return "\n\n".join(posts)

    except Exception as e:
        logger.error(f"Error in search_multiple_subreddits for subreddits {subreddits} and query '{query}': {str(e)}", exc_info=True)
        return f"An error occurred: {str(e)}"
