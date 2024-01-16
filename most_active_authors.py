import requests
from collections import defaultdict


def make_request(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


def get_data(url, headers):
    data = []
    page = 1
    while True:
        response = make_request(url, headers, params={'page': page})
        if not response:
            break
        data.extend(response)
        page += 1
    return data


def get_repositories(organisation, token):
    url = f'https://api.github.com/orgs/{organisation}/repos'
    headers = {'Authorization': f'token {token}'}
    return get_data(url, headers)


def get_commits(repo_full_name, token):
    url = f'https://api.github.com/repos/{repo_full_name}/commits'
    headers = {'Authorization': f'token {token}'}
    return get_data(url, headers)


def get_top_100_active_authors(organisation, token):
    repositories = get_repositories(organisation, token)
    authors = defaultdict(int)

    for repo in repositories:
        commits = get_commits(repo['full_name'], token)
        for commit in commits:
            commit = commit['commit']
            if ('author' in commit and commit['author']
                    and 'email' in commit['author']):
                if not commit['message'].startswith('Merge pull request #'):
                    authors[commit['author']['email']] += 1

    top_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)[
                  :100]
    return top_authors


if __name__ == "__main__":
    organisation = 'twitter'
    github_token = ''
    top_authors = get_top_100_active_authors(organisation, github_token)
    for idx in range(len(top_authors)):
        author, commits = top_authors[idx]
        print(f"{idx + 1}: {author} - {commits} commits")
