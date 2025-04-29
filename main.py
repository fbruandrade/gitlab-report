#!/usr/bin/env python3
"""
GitLab Tag Deployment Tracker

This script helps identify when tags have been deployed to production environments in GitLab.
It scans all projects (or a specific one) and finds all environments containing "production" in their name.
For each environment, it gets the deployment date and tag creation date.
All information is output in CSV format.

Usage:
    python main.py --url <gitlab_url> --token <access_token> [--project <project_id>] [--tag <tag>]

CSV Output Format:
    grupo,projeto,env_name1,deploy_created_at1,tag_created_at1,env_name2,deploy_created_at2,tag_created_at2,...

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
    parser.add_argument('--project', help='GitLab project ID or path (e.g., group/project). If not provided, all projects will be scanned.')
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


def get_all_projects(gl: gitlab.Gitlab) -> List[gitlab.v4.objects.Project]:
    """Get all accessible GitLab projects."""
    try:
        return gl.projects.list(all=True)
    except Exception as e:
        print(f"Error retrieving projects: {e}")
        sys.exit(1)


def get_production_environments(project: gitlab.v4.objects.Project) -> List[Dict[str, Any]]:
    """Get all environments containing 'production' in their name."""
    try:
        environments = project.environments.list(all=True)
        production_envs = []

        for env in environments:
            if 'production' in env.name.lower():
                production_envs.append(env)

        if not production_envs:
            print(f"No production environments found for project {project.path_with_namespace}.")

        return production_envs
    except Exception as e:
        print(f"Error retrieving environments for project {project.path_with_namespace}: {e}")
        return []


def get_environment_last_deployment(project: gitlab.v4.objects.Project, environment_id: int) -> Optional[Dict[str, Any]]:
    """Get the last deployment for a specific environment."""
    try:
        env = project.environments.get(environment_id)
        if hasattr(env, 'last_deployment') and env.last_deployment:
            return env.last_deployment
        return None
    except Exception as e:
        print(f"Error retrieving last deployment for environment {environment_id} in project {project.path_with_namespace}: {e}")
        return None


def get_tag_creation_date(project: gitlab.v4.objects.Project, tag_name: str) -> Optional[str]:
    """Get the creation date of a specific tag."""
    try:
        tags = project.tags.list(all=True, search=tag_name)
        for tag in tags:
            if tag.name == tag_name:
                # Return the commit creation date as the tag creation date
                if hasattr(tag, 'commit') and tag.commit and 'created_at' in tag.commit:
                    return tag.commit['created_at']
                return None
        return None
    except Exception as e:
        print(f"Error retrieving tag {tag_name} for project {project.path_with_namespace}: {e}")
        return None


def is_valid_tag_format(tag: str) -> bool:
    """Check if tag follows the vx.y.z format."""
    pattern = r'^v\d+\.\d+\.\d+$'
    return bool(re.match(pattern, tag))


def get_deployment_info(project: gitlab.v4.objects.Project, environment: Dict[str, Any]) -> Dict[str, str]:
    """
    Get deployment information for a specific environment.

    Args:
        project: The GitLab project
        environment: The environment object

    Returns:
        Dictionary with environment name, deployment date, and tag creation date
    """
    result = {
        'env_name': environment.name,
        'deploy_created_at': '',
        'tag_created_at': ''
    }

    deployment = get_environment_last_deployment(project, environment.id)
    if not deployment:
        return result

    result['deploy_created_at'] = deployment['created_at']

    # Get tag creation date
    tag_name = deployment['ref']
    tag_created_at = get_tag_creation_date(project, tag_name)
    if tag_created_at:
        result['tag_created_at'] = tag_created_at

    return result


def format_csv_row(group: str, project_name: str, env_data: List[Dict[str, str]]) -> str:
    """Format data as a CSV row."""
    row = [group, project_name]

    # Add environment data
    for env in env_data:
        row.append(env['env_name'])
        row.append(env['deploy_created_at'])
        row.append(env['tag_created_at'])

    return ','.join(row)


def main() -> None:
    """Main function to run the script."""
    args = parse_arguments()

    # Connect to GitLab
    gl = connect_to_gitlab(args.url, args.token)

    # Print CSV header
    print("grupo,projeto,env_name1,deploy_created_at1,tag_created_at1,env_name2,deploy_created_at2,tag_created_at2,env_name3,deploy_created_at3,tag_created_at3,...")

    # Get projects
    projects = []
    if args.project:
        projects = [get_project(gl, args.project)]
    else:
        projects = get_all_projects(gl)

    # Process each project
    for project in projects:
        # Get group name (namespace)
        group = project.namespace['name'] if hasattr(project, 'namespace') and project.namespace else ""

        # Get production environments
        prod_envs = get_production_environments(project)

        if not prod_envs:
            continue

        # Get deployment info for each environment
        env_data = []
        for env in prod_envs:
            env_info = get_deployment_info(project, env)
            env_data.append(env_info)

        # Print CSV row
        if env_data:
            print(format_csv_row(group, project.name, env_data))


if __name__ == '__main__':
    main()
