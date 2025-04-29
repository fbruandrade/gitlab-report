#!/usr/bin/env python3
"""
GitLab Tag Deployment Tracker

This script helps identify when a specific tag has been deployed to the production environment in GitLab.
It uses the python-gitlab library to interact with the GitLab API.

Usage:
    python main.py --url <gitlab_url> --token <access_token> --project <project_id> [--tag <tag>]

Requirements:
    - python-gitlab
    - argparse
"""

import sys
import re
import argparse
import gitlab
from typing import Optional, Dict, Any, List


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Track tag deployments to production in GitLab')

    parser.add_argument('--url', required=True, help='GitLab instance URL (e.g., https://gitlab.com)')
    parser.add_argument('--token', required=True, help='GitLab personal access token')
    parser.add_argument('--project', required=True, help='GitLab project ID or path (e.g., group/project)')
    parser.add_argument('--tag', help='Specific tag to check (e.g., v1.2.3)')

    return parser.parse_args()


def connect_to_gitlab(url: str, token: str) -> gitlab.Gitlab:
    """Establish connection to GitLab API."""
    try:
        gl = gitlab.Gitlab(url=url, private_token=token)
        gl.auth()
        return gl
    except Exception as e:
        print(f"Error connecting to GitLab: {e}")
        sys.exit(1)


def get_project(gl: gitlab.Gitlab, project_id: str) -> gitlab.v4.objects.Project:
    """Get GitLab project by ID or path."""
    try:
        return gl.projects.get(project_id)
    except Exception as e:
        print(f"Error retrieving project: {e}")
        sys.exit(1)


def get_production_environment(project: gitlab.v4.objects.Project) -> Optional[Dict[str, Any]]:
    """Get the production environment details."""
    try:
        environments = project.environments.list(all=True)
        for env in environments:
            if env.name.lower() == 'production':
                return env

        print("Production environment not found.")
        return None
    except Exception as e:
        print(f"Error retrieving environments: {e}")
        return None


def get_environment_last_deployment(project: gitlab.v4.objects.Project, environment_id: int) -> Optional[Dict[str, Any]]:
    """Get the last deployment for a specific environment."""
    try:
        env = project.environments.get(environment_id)
        if hasattr(env, 'last_deployment') and env.last_deployment:
            return env.last_deployment
        print("No last deployment found for the environment.")
        return None
    except Exception as e:
        print(f"Error retrieving last deployment: {e}")
        return None


def is_valid_tag_format(tag: str) -> bool:
    """Check if tag follows the vx.y.z format."""
    pattern = r'^v\d+\.\d+\.\d+$'
    return bool(re.match(pattern, tag))


def check_tag_deployment(deployment: Optional[Dict[str, Any]], tag: Optional[str] = None) -> None:
    """
    Check if a specific tag has been deployed to production or show the latest deployed tag.

    Args:
        deployment: The last deployment object
        tag: Optional tag to check (if None, will show the latest tag)
    """
    if not deployment:
        print("No deployment found for the production environment.")
        return

    # Get the latest tag
    latest_tag = deployment.ref

    print(f"Latest tag deployed to production: {latest_tag} (deployed at {deployment.created_at})")

    # If a specific tag was provided, check if it matches the latest deployment
    if tag:
        if not is_valid_tag_format(tag):
            print(f"Warning: The provided tag '{tag}' does not follow the expected format vx.y.z")

        if deployment.ref == tag:
            print(f"Tag {tag} was deployed to production at {deployment.created_at}")
        else:
            print(f"Tag {tag} has not been deployed to production yet.")


def main() -> None:
    """Main function to run the script."""
    args = parse_arguments()

    # Connect to GitLab
    gl = connect_to_gitlab(args.url, args.token)

    # Get project
    project = get_project(gl, args.project)
    print(f"Connected to project: {project.name}")

    # Get production environment
    prod_env = get_production_environment(project)
    if not prod_env:
        sys.exit(1)

    print(f"Found production environment (ID: {prod_env.id})")

    # Get deployments for production environment
    deployments = get_environment_deployments(project, prod_env.id)

    # Check tag deployment
    check_tag_deployment(deployments, args.tag)


if __name__ == '__main__':
    main()
