pip
listimport
subprocess


def generate_commit_message():
    # Get the Git diff
    diff = subprocess.run(
        ["git", "diff", "--staged"], capture_output=True, text=True
    ).stdout

    if not diff:
        return "No changes staged for commit."

    # Basic logic to identify types of changes
    if "fix" in diff.lower():
        message_type = "fix"
    elif "add" in diff.lower():
        message_type = "feat"
    elif "refactor" in diff.lower():
        message_type = "refactor"
    else:
        message_type = "chore"

    # Extract file names and summarize changes
    files = subprocess.run(
        ["git", "diff", "--name-only", "--staged"], capture_output=True, text=True
    ).stdout
    file_list = files.strip().split("\n")
    file_summary = ", ".join(file_list)

    # Construct the commit message
    commit_message = f"{message_type}: Update {file_summary}"
    return commit_message


# Example usage
if __name__ == "__main__":
    message = generate_commit_message()
    print(message)
