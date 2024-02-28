import json
import praw
import logging
import argparse

from datetime import datetime
from time import sleep
from praw.exceptions import RedditAPIException

logging.basicConfig(filename="reddit_scrapper.log", level=logging.DEBUG)
logger = logging.getLogger(__name__)

reddit = praw.Reddit(
    client_id="",
    client_secret="",
    user_agent="",
    username="",
    password="",
    check_for_async=False,
)

subreddit_list = []


def reddit_scrapper(
    subreddit: str,
    no_of_posts: int | None = None,
    type_of_posts: str | None = None,
    comment_to_scrape: bool | None = None,
    sort_comment: str | None = None,
    no_of_comments: int | None = None,
    moderator_to_scrape: bool | None = None,
):
    try:
        logger.info(
            {
                "type_of_posts": type_of_posts,
                "comment_to_scrape": comment_to_scrape,
                "sort_comment": sort_comment,
                "no_of_comments": no_of_comments,
                "moderator_to_scrape": moderator_to_scrape,
            }
        )

        # Get subreddit details
        subreddit = reddit.subreddit(subreddit)

        logger.info({"subreddit": subreddit})

        if subreddit:
            logger.info({"subreddit": subreddit})
            subreddit_list.append(
                {
                    "name": subreddit.name,
                    "title": subreddit.title,
                    "submission_type": subreddit.submission_type,
                    "description": subreddit.public_description,
                    "subscribers": subreddit.subscribers,
                    "active_user_count": subreddit.active_user_count,
                    "mobile_banner_image": subreddit.mobile_banner_image,
                    "whitelist_status": subreddit.whitelist_status,
                    "created_at": datetime.utcfromtimestamp(
                        subreddit.created_utc
                    ).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "posts": [],
                    "moderators": [],
                }
            )

            # Get all posts of the subreddit
            subreddit_posts = []

            posts = (
                subreddit.new(limit=no_of_posts)
                if type_of_posts == "new"
                else (
                    subreddit.top(limit=no_of_posts)
                    if type_of_posts == "top"
                    else subreddit.hot(limit=no_of_posts)
                )
            )

            for post in posts:
                try:
                    subreddit_posts.append(
                        {
                            "id": post.id,
                            "title": post.title,
                            "link_flair_text": post.link_flair_text,
                            "url": post.url,
                            # "author": post.author.name,
                            "description": post.selftext,
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "is_video": post.is_video,
                            "created_at": datetime.utcfromtimestamp(
                                post.created_utc
                            ).strftime("%Y-%m-%d %H:%M:%S UTC"),
                        }
                    )

                    # comments
                    if comment_to_scrape:
                        pass
                except RedditAPIException as e:
                    logger.warning(
                        f"Rate limit exceeded. Waiting for {e.sleep_time} seconds."
                    )
                    sleep(e.sleep_time)

            subreddit_list[0]["posts"] = subreddit_posts

            if moderator_to_scrape:
                # Get all moderators of the subreddit
                subreddit_moderators = []
                moderators = subreddit.moderator()
                for moderator in moderators:
                    try:
                        subreddit_moderators.append(
                            {"id": moderator.id, "name": moderator.name}
                        )
                    except RedditAPIException as e:
                        logger.warning(
                            f"Rate limit exceeded. Waiting for {e.sleep_time} seconds."
                        )
                        sleep(e.sleep_time)

                subreddit_list[0]["moderators"] = subreddit_moderators

            if subreddit_list:
                file_name = (
                    f"reddit_scrapper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                logger.info({"subreddit_list": subreddit_list})
                with open(file_name, "w") as json_file:
                    json.dump(subreddit_list, json_file, indent=2)
    # except NotFound:
    #     print(f"The subreddit '{subreddit}' does not exist.")
    # except Redirect:
    #     print(f"The subreddit '{subreddit}' redirects to the search page.")
    except Exception as e:
        logger.error({"Error": e})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape Subreddit Posts, Comments, and Moderators details!!"
    )
    parser.add_argument(
        "subreddit", type=str, help="Please enter a subreddit name you want to scrape."
    )
    parser.add_argument(
        "--no_of_posts",
        type=int,
        default=None,
        help="Please enter the number of posts you want to scrap.",
        required=False,
    )
    parser.add_argument(
        "--type_of_posts",
        type=str,
        choices=["hot", "new", "top"],
        default="new",
        help="Please enter the type of posts you want to scrap",
        required=False,
    )
    parser.add_argument(
        "--comment_to_scrape",
        type=bool,
        default=False,
        help="Please enter a subreddit name you want to scrape.",
        required=False,
    )
    parser.add_argument(
        "--sort_comment",
        type=str,
        choices=["best", "top", "new", "controversial", "old", "q&a"],
        default="best",
        help="Please enter the way you want to sort the comment.",
        required=False,
    )
    parser.add_argument(
        "--no_of_comments",
        type=int,
        default=None,
        help="Please enter number of comments you want to scrap.",
        required=False,
    )
    parser.add_argument(
        "--moderator_to_scrape",
        type=bool,
        default=False,
        help="Please enter a subreddit name you want to scrape.",
        required=False,
    )
    args = parser.parse_args()

    reddit_scrapper(
        args.subreddit,
        args.no_of_posts,
        args.type_of_posts,
        args.comment_to_scrape,
        args.sort_comment,
        args.no_of_comments,
        args.moderator_to_scrape,
    )
