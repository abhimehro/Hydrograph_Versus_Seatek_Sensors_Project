import subprocess

# Constants for Git commands
GIT_DIFF_COMMAND = ["git", "diff", "--staged"]
GIT_DIFF_NAME_ONLY_COMMAND = ["git", "diff", "--name-only", "--staged"]

def determine_message_type(staged_diff):
    """
    Determine the type of commit message based on diff content.
    """
    diff_lower = staged_diff.lower()
    if "fix" in diff_lower:
        return "fix"
    elif "add" in diff_lower:
        return "feat"
    elif "refactor" in diff_lower:
        return "refactor"
    else:
        return "chore"

def get_staged_file_list():
    """
    Get the list of staged files from Git.
    """
    staged_files_output = subprocess.run(
        GIT_DIFF_NAME_ONLY_COMMAND, capture_output=True, text=True
    ).stdout
    return staged_files_output.strip().split("\n")

def generate_commit_message():
    """
    Generate a commit message based on staged changes.
    """
    staged_diff = subprocess.run(
        GIT_DIFF_COMMAND, capture_output=True, text=True
    ).stdout
    if not staged_diff:
        return "No changes staged for commit."

    # Determine message type and summarize staged files
    message_type = determine_message_type(staged_diff)
    staged_files = get_staged_file_list()
    file_summary = ", ".join(staged_files)

    # Construct the commit message
    return f"{message_type}: Update {file_summary}"

# Example usage
if __name__ == "__main__":
    message = generate_commit_message()
    print(message)
