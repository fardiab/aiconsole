import git
import os
from git.exc import GitCommandError, InvalidGitRepositoryError


class GitRepository:
    def __init__(self, repo_path: str):
        if not os.path.isdir(repo_path):
            raise ValueError(f"Path {repo_path} is not a valid directory")
        self.repo_path = repo_path
        try:
            self.repo = git.Repo(repo_path)
        except InvalidGitRepositoryError:
            raise ValueError(f"The directory at {repo_path} is not a valid Git repository")

    def commit_changes(self, message: str):
        """
        Adds all changes in the materials directory to the Git index and commits them.
        """
        self.repo.git.add(all=True)  # Add all changes
        self.repo.index.commit(message)  # Commit with the provided message

        # Check if the current branch has an upstream branch
        current_branch = self.repo.active_branch
        if current_branch.tracking_branch() is None:
            # Set the upstream branch if not set
            self.repo.git.branch("--set-upstream-to=origin/main", current_branch.name)

        try:
            # Push changes to remote origin
            self.repo.remotes.origin.push()
        except GitCommandError as e:
            # Handle errors during the push operation
            raise Exception(f"Error while pushing to remote: {e.stderr.strip()}")

    def get_changelog(self, branch="main", max_commits=10):
        """
        Retrieves the commit history for the materials repository.
        :param branch: Git branch name (default is 'main').
        :param max_commits: Number of commits to retrieve (default is 10).
        """
        try:
            commits = list(self.repo.iter_commits(branch, max_count=max_commits))
        except GitCommandError as e:
            # Handle errors during the commit retrieval
            raise Exception(f"Error while fetching commits: {e.stderr.strip()}")

        changelog = []
        for commit in commits:
            changelog.append(
                {
                    "commit": commit.hexsha,
                    "author": commit.author.name,
                    "date": commit.committed_datetime,
                    "message": commit.message.strip(),
                }
            )
        return changelog
