from github import Github

import config

g = Github(config.GITHUB_TOKEN)
g.per_page = 100
repo = g.get_repo(config.GITHUB_REPO)


def rate_limit(func):
    def wrapper(*args, **kwargs):
        limit = g.get_rate_limit().core.remaining
        print(f'Rate limit: {limit}')
        ret = func(*args, **kwargs)
        new_limit = g.get_rate_limit().core.remaining
        used = limit - new_limit
        print(f'Rate limit: {new_limit}\nUsed: {used}')
        return ret

    return wrapper


class GithubAPI_UserRoles:
    @staticmethod
    def get_collaborators() -> list[str]:
        """Get the list of users who are collaborators on the repo."""
        return [user.login for user in repo.get_collaborators()]

    @staticmethod
    def get_contributors() -> list[str]:
        """Get the list of users who contributed to the repo."""
        return [user.login for user in repo.get_contributors()]

    @staticmethod
    def get_stargazers() -> list[str]:
        """Get the list of users who starred the repo."""
        data = [user.login for user in repo.get_stargazers()]
        return data

    @staticmethod
    def get_subscribers() -> list[str]:
        """Get the list of users who watch the repo."""
        return [user.login for user in repo.get_subscribers()]

    @classmethod
    def get_owner(cls) -> str:
        """Get the owner of the repo."""
        return repo.owner.login
