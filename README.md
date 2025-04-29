# GitLab Tag Deployment Tracker

This script helps identify when a specific tag has been deployed to the production environment in GitLab. It can check if a particular tag (in the format vx.y.z) has reached production or show the latest tag that was deployed.

## Features

- Connect to GitLab API using personal access token
- Identify the production environment for a project
- Show the latest tag deployed to production
- Check if a specific tag has been deployed to production
- Validate tag format (vx.y.z)

## Requirements

- Python 3.6+
- python-gitlab library

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/gitlab-report.git
   cd gitlab-report
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

   Or install directly:
   ```
   pip install python-gitlab
   ```

## Usage

Run the script with the following command-line arguments:

```
python main.py --url <gitlab_url> --token <access_token> --project <project_id> [--tag <tag>]
```

### Arguments

- `--url`: GitLab instance URL (e.g., https://gitlab.com)
- `--token`: GitLab personal access token
- `--project`: GitLab project ID or path (e.g., group/project)
- `--tag`: (Optional) Specific tag to check (e.g., v1.2.3)

### Examples

Check the latest tag deployed to production:
```
python main.py --url https://gitlab.com --token glpat-xxxxxxxxxxxx --project mygroup/myproject
```

Check if a specific tag has been deployed to production:
```
python main.py --url https://gitlab.com --token glpat-xxxxxxxxxxxx --project mygroup/myproject --tag v1.2.3
```

## Getting a GitLab Personal Access Token

1. Log in to your GitLab instance
2. Go to your user settings (click on your avatar in the top-right corner and select "Preferences")
3. Navigate to "Access Tokens" in the left sidebar
4. Create a new personal access token with the following scopes:
   - `read_api`
   - `read_repository`
5. Copy the generated token and use it with the `--token` argument

## Output Examples

When checking the latest tag:
```
Connected to project: My Project
Found production environment (ID: 123)
Latest tag deployed to production: v2.1.0 (deployed at 2023-05-15T10:30:45Z)
```

When checking a specific tag:
```
Connected to project: My Project
Found production environment (ID: 123)
Latest tag deployed to production: v2.1.0 (deployed at 2023-05-15T10:30:45Z)
Tag v1.5.0 was deployed to production at 2023-04-20T14:22:33Z
```

## License

MIT
