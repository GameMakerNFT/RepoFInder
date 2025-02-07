#!/usr/bin/env python3
#  python .\gitHubScanner.py --query "Pump.Fun-Sniper-Bot" --min_stars 100 --pages 3 --output ".\githubReposSearch\pumpfunSniperBot.csv"
import argparse
import requests
import os
from datetime import datetime
import csv

# ================================
# GitHub API Setup 
# ================================
GITHUB_TOKEN =  "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" # os.environ.get('GITHUB_TOKEN')  # Retrieve GitHub token from env var
headers = {}
if GITHUB_TOKEN:
    headers['Authorization'] = f'token {GITHUB_TOKEN}'

# ================================
# Functions for API Interaction and Filtering
# ================================
def search_repositories(query, sort="stars", order="desc", per_page=20, page=1):
    """
    Search GitHub repositories using the GitHub API.
    
    :param query: The search query string (e.g., "crypto bot OR crypto sniper ...")
    :param sort: The field to sort results by (default is "stars")
    :param order: The sort order (default is "desc")
    :param per_page: Number of results per page (max 100)
    :param page: Page number to retrieve
    :return: JSON response from the GitHub API
    """
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": sort,
        "order": order,
        "per_page": per_page,
        "page": page
    }
    print(f"Searching GitHub: page {page}, query: '{query}'")
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} {response.text}")
    return response.json()

def advanced_filter_repositories(repos, min_stars, language=None, updated_after=None):
    """
    Apply advanced filtering to the list of repositories.
    
    :param repos: List of repository objects returned by the API
    :param min_stars: Minimum star count required
    :param language: (Optional) Filter by repository's primary programming language
    :param updated_after: (Optional) A datetime object; only include repos updated after this date
    :return: List of repositories that meet all the criteria
    """
    filtered = []
    for repo in repos:
        # Filter by minimum stars
        if repo.get('stargazers_count', 0) < min_stars:
            continue

        # Filter by programming language if provided (case‑insensitive)
        if language:
            repo_language = repo.get('language')
            if not repo_language or repo_language.lower() != language.lower():
                continue

        # Filter by last updated date if provided
        if updated_after:
            updated_at = datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            if updated_at < updated_after:
                continue

        filtered.append(repo)
    return filtered

def print_repo_info(repo):
    """
    Print key details of a repository in a readable format.
    
    :param repo: A single repository object from the GitHub API
    """
    print("Name:         ", repo['full_name'])
    print("Stars:        ", repo['stargazers_count'])
    print("Forks:        ", repo['forks_count'])
    updated_at = datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
    print("Last Updated: ", updated_at.strftime('%Y-%m-%d %H:%M:%S'))
    print("Language:     ", repo.get('language', 'Unknown'))
    print("URL:          ", repo['html_url'])
    print("Description:  ", repo.get('description', 'No description provided'))
    print("-" * 60)

def export_to_csv(repos, filename):
    """
    Export repository details to a CSV file.
    
    :param repos: List of repository objects
    :param filename: Desired name of the CSV file
    """
    fieldnames = [
        'full_name',
        'stargazers_count',
        'forks_count',
        'updated_at',
        'language',
        'html_url',
        'description'
    ]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for repo in repos:
                writer.writerow({
                    'full_name': repo['full_name'],
                    'stargazers_count': repo['stargazers_count'],
                    'forks_count': repo['forks_count'],
                    'updated_at': repo['updated_at'],
                    'language': repo.get('language', 'Unknown'),
                    'html_url': repo['html_url'],
                    'description': repo.get('description', '')
                })
        print(f"\nResults exported to {filename}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")

# ================================
# Main Function with CLI
# ================================
def main():
    parser = argparse.ArgumentParser(
        description="Advanced Crypto Trading Tools Search Agent\n"
                    "Searches for advanced crypto bots, snipers, trading bots, arbitrage tools, "
                    "crypto signals, and more."
    )
    parser.add_argument(
        '--query', type=str,
        default='crypto bot OR crypto sniper OR trading bot OR arbitrage bot OR crypto trading OR crypto signals',
        help="Search query for GitHub repositories (default includes keywords for advanced crypto tools)"
    )
    parser.add_argument(
        '--min_stars', type=int, default=50,
        help="Minimum number of stars required for a repository (default: 50)"
    )
    parser.add_argument(
        '--per_page', type=int, default=20,
        help="Number of results per page (default: 20, maximum: 100)"
    )
    parser.add_argument(
        '--pages', type=int, default=1,
        help="Number of pages to fetch (default: 1)"
    )
    parser.add_argument(
        '--language', type=str,
        help="Filter by programming language (optional, e.g., Python, JavaScript)"
    )
    parser.add_argument(
        '--updated_after', type=str,
        help="Only include repositories updated after this date (YYYY-MM-DD, optional)"
    )
    parser.add_argument(
        '--output', type=str,
        help="If provided, export the results to the specified CSV file (optional)"
    )

    args = parser.parse_args()

    # Parse the updated_after date if provided
    updated_after_date = None
    if args.updated_after:
        try:
            updated_after_date = datetime.strptime(args.updated_after, '%Y-%m-%d')
        except ValueError:
            print("Error: updated_after must be in YYYY-MM-DD format.")
            return

    all_repos = []
    # Loop over the requested number of pages to fetch results
    for page in range(1, args.pages + 1):
        try:
            result = search_repositories(query=args.query, per_page=args.per_page, page=page)
            repos = result.get('items', [])
            all_repos.extend(repos)
        except Exception as e:
            print(f"Error fetching page {page}: {e}")

    print(f"\nTotal repositories fetched: {len(all_repos)}")

    # Apply advanced filtering
    filtered_repos = advanced_filter_repositories(
        all_repos,
        min_stars=args.min_stars,
        language=args.language,
        updated_after=updated_after_date
    )
    print(f"Repositories after filtering: {len(filtered_repos)}\n")

    # Display repository details
    for repo in filtered_repos:
        print_repo_info(repo)

    # Optionally export the filtered results to a CSV file
    if args.output:
        export_to_csv(filtered_repos, args.output)

if __name__ == '__main__':
    main()
