import os
from github import Github, GithubException
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOOLS_AVAILABLE = False
try:
    _gh = Github(os.getenv("GITHUB_TOKEN"))
    _user = _gh.get_user()
    GITHUB_TOOLS_AVAILABLE = True
except GithubException as e:
    print(f"GitHub authentication failed: {e}")
    _gh = None
    _user = None
    GITHUB_TOOLS_AVAILABLE = False


@tool
def list_repos() -> str:
    """
    Returns the names and descriptions of the candidate's public GitHub repositories,
    sorted by most recently updated. Use this when asked about their GitHub projects
    or what they have built.
    """
    if not GITHUB_TOOLS_AVAILABLE:
        return "GitHub tools are not available. Please check the logs for more details."

    try:
        repos = _user.get_repos(type="public", sort="updated")
        repo_texts = []

        for repo in repos:
            repo_texts.append(f"{repo.name}: {repo.description}")

        return "\n".join(repo_texts) if repo_texts else "No public repositories found."
    except Exception:
        return "An error occurred while fetching GitHub repositories. Please check the logs for more details."


@tool
def get_repo_details(repo_name: str) -> str:
    """
    Returns description, primary language, star count, and fork count for a specific
    repository. Use this when asked about a particular project in detail.
    repo_name: The repository name without the owner prefix.
    """

    if not GITHUB_TOOLS_AVAILABLE:
        return "GitHub tools are not available. Please check the logs for more details."

    try:
        repo = _user.get_repo(repo_name)
        return (
            f"Repository: {repo.name}\n"
            f"Description: {repo.description or 'No description'}\n"
            f"Language: {repo.language or 'Not specified'}\n"
            f"Stars: {repo.stargazers_count}\n"
            f"Forks: {repo.forks_count}"
        )
    except Exception:
        return f"An error occurred while fetching details for repository '{repo_name}'. Please check the logs for more details."


@tool
def get_github_profile_summary() -> str:
    """
      Returns the candidate's GitHub profile summary: bio, public repo count,
      and follower count. Use this for general GitHub questions when no specific
      repo is mentioned.
    """
    if not GITHUB_TOOLS_AVAILABLE:
        return "GitHub tools are not available. Please check the logs for more details."

    try:
        return (
            f"GitHub Username: {_user.login}\n"
            f"Name: {_user.name or 'Not set'}\n"
            f"Bio: {_user.bio or 'No bio'}\n"
            f"Public Repos: {_user.public_repos}\n"
            f"Followers: {_user.followers}\n"
            f"Following: {_user.following}"
        )
    except Exception:
        return "An error occurred while fetching GitHub profile summary. Please check the logs for more details."


GITHUB_TOOLS = [list_repos, get_repo_details, get_github_profile_summary]