import requests


class GitHubMetadata:
    def __init__(self, github_repository, api_url='https://api.github.com'):
        self.api_url = api_url
        self.github_repository = github_repository

    def find_pull_requests(self, commit_ref):
        repo = ""
        if self.github_repository:
            repo = self.github_repository

        params = {
            'q': f"SHA={commit_ref}&repo:{repo}"
        }

        response = requests.get(
            f"{self.api_url}/search/issues",
            params=params,
            headers={"Accept": "application/vnd.github.v3+json"}
        )

        response.raise_for_status()
        response_json = response.json()

        return [self._summarise_pull_request(
            commit_ref,
            item
        ) for item in response_json['items']]


    def _summarise_pull_request(self, commit_ref, pull_request):
        return {
            'ref': commit_ref,
            'title': pull_request['title'],
            'closed_at' :pull_request['closed_at'],
            'url': pull_request['pull_request']['html_url']
        }