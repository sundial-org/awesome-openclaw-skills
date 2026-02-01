"""
ggshield Secret Scanner Skill for Moltbot

Detects 500+ types of hardcoded secrets (API keys, credentials, certificates)
before they're committed to git.

Author: GitGuardian Team
Version: 1.0.0
"""

import os
import subprocess


class GGShieldSkill:
    """
    Moltbot skill that wraps ggshield CLI for secret scanning.

    Provides methods to scan repositories, files, staged changes, and Docker images
    for hardcoded secrets using GitGuardian's detection engine.
    """

    def __init__(self):
        """Initialize the ggshield skill."""
        self.name = "ggshield"
        self.version = "1.0.0"
        self.requires_api_key = True
        self.api_key_env = "GITGUARDIAN_API_KEY"

    def _get_api_key(self) -> str:
        """
        Get GitGuardian API key from environment.

        Raises ValueError if not set.
        """
        api_key = os.environ.get(self.api_key_env)
        if not api_key:
            raise ValueError(
                f"{self.api_key_env} not set. "
                "Get one at https://dashboard.gitguardian.com"
            )
        return api_key

    def _run_ggshield(self, *args: str) -> tuple[int, str, str]:
        """
        Run ggshield CLI command with API key.

        Args:
            *args: Arguments to pass to ggshield (e.g., 'secret', 'scan', 'repo', '.')

        Returns:
            Tuple of (exit_code, stdout, stderr)

        Raises:
            FileNotFoundError: If ggshield is not installed
        """
        api_key = self._get_api_key()
        command = ["ggshield", *args]

        env = {**os.environ, self.api_key_env: api_key}

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
        )

        return result.returncode, result.stdout, result.stderr

    def _format_success(self, message: str) -> str:
        """Format success message with emoji."""
        return f"✅ {message}"

    def _format_error(self, message: str) -> str:
        """Format error message with emoji."""
        return f"❌ {message}"

    def _format_scanning(self, message: str) -> str:
        """Format scanning message with emoji."""
        return f"🔍 {message}"

    def _is_git_repository(self, path: str = ".") -> bool:
        """Check if the given path is inside a git repository."""
        git_dir = os.path.join(path, ".git")
        if os.path.exists(git_dir):
            return True
        # Also check if we're in a subdirectory of a git repo
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                capture_output=True,
                text=True,
                cwd=path,
            )
            return result.returncode == 0
        except (FileNotFoundError, OSError):
            return False

    async def scan_repo(self, path: str) -> str:
        """
        Scan entire git repository for secrets.

        Args:
            path: Path to repository root

        Returns:
            User-facing message describing results
        """
        # Validate path exists
        if not os.path.exists(path):
            return self._format_error(f"Path not found: {path}")

        if not os.path.isdir(path):
            return self._format_error(f"Not a directory: {path}")

        try:
            exit_code, stdout, stderr = self._run_ggshield(
                "secret", "scan", "repo", path
            )

            if exit_code == 0:
                return self._format_success(f"Repository clean: {path}")
            else:
                # Secrets were found
                output = stdout if stdout else stderr
                return self._format_error(f"Secrets found in repository:\n{output}")

        except FileNotFoundError:
            return self._format_error(
                "ggshield not installed. Run: pip install ggshield"
            )
        except ValueError as e:
            return self._format_error(str(e))
        except Exception as e:
            return self._format_error(f"Unexpected error: {e}")

    async def scan_file(self, path: str) -> str:
        """
        Scan a single file for secrets.

        Args:
            path: Path to file to scan

        Returns:
            User-facing message describing results
        """
        # Validate file exists
        if not os.path.exists(path):
            return self._format_error(f"File not found: {path}")

        if not os.path.isfile(path):
            return self._format_error(f"Not a file: {path}")

        try:
            exit_code, stdout, stderr = self._run_ggshield("secret", "scan", "path", path)

            if exit_code == 0:
                return self._format_success(f"File clean: {path}")
            else:
                # Secrets were found
                output = stdout if stdout else stderr
                return self._format_error(f"Secrets found in {path}:\n{output}")

        except FileNotFoundError:
            return self._format_error(
                "ggshield not installed. Run: pip install ggshield"
            )
        except ValueError as e:
            return self._format_error(str(e))
        except Exception as e:
            return self._format_error(f"Unexpected error: {e}")

    async def scan_staged(self) -> str:
        """
        Scan only staged git changes (pre-commit mode).

        Fast scanning of what's about to be committed. Requires git repository.

        Returns:
            User-facing message describing results
        """
        # Check we're in a git repository
        if not self._is_git_repository():
            return self._format_error(
                "Not in a git repository. Run from repo root."
            )

        try:
            exit_code, stdout, stderr = self._run_ggshield(
                "secret", "scan", "pre-commit"
            )

            if exit_code == 0:
                return self._format_success("Staged changes are clean")
            else:
                # Secrets were found
                output = stdout if stdout else stderr
                return self._format_error(
                    f"Secrets detected in staged changes:\n{output}"
                )

        except FileNotFoundError:
            return self._format_error(
                "ggshield not installed. Run: pip install ggshield"
            )
        except ValueError as e:
            return self._format_error(str(e))
        except Exception as e:
            return self._format_error(f"Unexpected error: {e}")

    async def install_hooks(self, hook_type: str = "pre-commit") -> str:
        """
        Install ggshield as a git pre-commit hook.

        After installation, every commit will be scanned automatically.

        Args:
            hook_type: Type of hook to install: 'pre-commit' or 'pre-push'

        Returns:
            User-facing message describing installation result
        """
        # Validate hook type
        valid_hooks = ("pre-commit", "pre-push")
        if hook_type not in valid_hooks:
            return self._format_error(
                f"Invalid hook type: {hook_type}. Must be one of: {', '.join(valid_hooks)}"
            )

        # Check we're in a git repository
        if not self._is_git_repository():
            return self._format_error(
                "Not in a git repository. Run from repo root."
            )

        try:
            exit_code, stdout, stderr = self._run_ggshield(
                "install", "--mode", "local", "--hook-type", hook_type
            )

            if exit_code == 0:
                return self._format_success(
                    f"Installed {hook_type} hook.\n"
                    f"From now on, commits with secrets will be blocked."
                )
            else:
                output = stderr if stderr else stdout
                return self._format_error(
                    f"Failed to install hook: {output}"
                )

        except FileNotFoundError:
            return self._format_error(
                "ggshield not installed. Run: pip install ggshield"
            )
        except ValueError as e:
            return self._format_error(str(e))
        except Exception as e:
            return self._format_error(f"Unexpected error: {e}")

    async def scan_docker(self, image: str) -> str:
        """
        Scan Docker image for secrets in its layers.

        Args:
            image: Docker image name/tag (e.g., 'myapp:latest')

        Returns:
            User-facing message describing results
        """
        # Validate image string
        if not image or not image.strip():
            return self._format_error("Docker image name is required")

        image = image.strip()

        try:
            exit_code, stdout, stderr = self._run_ggshield(
                "secret", "scan", "docker", image
            )

            if exit_code == 0:
                return self._format_success(f"Docker image {image} is clean")
            else:
                # Check for Docker not available error
                combined_output = f"{stdout}\n{stderr}".lower()
                if "docker" in combined_output and (
                    "not found" in combined_output
                    or "cannot connect" in combined_output
                    or "is not running" in combined_output
                ):
                    return self._format_error(
                        "Docker is not available. Make sure Docker is installed and running."
                    )

                # Check for image not found
                if "no such image" in combined_output or "not found" in combined_output:
                    return self._format_error(
                        f"Docker image not found: {image}. "
                        "Make sure the image exists locally or pull it first."
                    )

                # Secrets were found
                output = stdout if stdout else stderr
                return self._format_error(
                    f"Secrets found in Docker image {image}:\n{output}"
                )

        except FileNotFoundError:
            return self._format_error(
                "ggshield not installed. Run: pip install ggshield"
            )
        except ValueError as e:
            return self._format_error(str(e))
        except Exception as e:
            return self._format_error(f"Unexpected error: {e}")
