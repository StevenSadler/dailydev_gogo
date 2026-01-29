import os
import sys
import yaml
from datetime import datetime, date

# -----------------------------
# Helper functions
# -----------------------------

def read_yaml_file(path):
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    if data is None:
        data = {}  # <-- fix for empty YAML files when creating new project
    return data

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_summary(project_dir):
    """Save ChatGPT end-of-day summary with auto-incrementing filenames."""
    summaries_dir = os.path.join(project_dir, "summaries")
    os.makedirs(summaries_dir, exist_ok=True)

    today = date.today().isoformat()
    # Find existing summaries for today
    existing_files = [f for f in os.listdir(summaries_dir) if f.startswith(today) and f.endswith(".txt")]
    N = 1
    if existing_files:
        # Extract existing N values
        nums = []
        for f in existing_files:
            parts = f.replace(".txt","").split("_")
            if len(parts) == 2 and parts[0] == today and parts[1].isdigit():
                nums.append(int(parts[1]))
        if nums:
            N = max(nums) + 1

    filename = f"{today}_{N}.txt"
    summary_path = os.path.join(summaries_dir, filename)

    print(
        "Paste the ChatGPT end-of-day summary below.\n"
        "After pasting, press Enter, then Ctrl-D (Linux/macOS) or Ctrl-Z (Windows) to finish.\n"
        "Tip: On Linux, you may need Ctrl-Shift-V to paste into the terminal before Ctrl-D."
    )
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    summary_text = "\n".join(lines)
    with open(summary_path, "w") as f:
        f.write(summary_text)

    print(f"Summary saved to {summary_path}")

def resolve_project_files(project_files, source_roots):
    resolved = {}
    for key, info in project_files.items():
        root_name = info["root"]
        rel_path = info["path"]
        root_path = source_roots.get(root_name)
        if root_path is None:
            raise ValueError(f"Unknown root '{root_name}' in project_files.yaml for key '{key}'")
        resolved[key] = os.path.join(root_path, rel_path)
    return resolved

# -----------------------------
# Daily prompt builder
# -----------------------------

def build_daily_prompt(project_dir, project_config, resolved_files):
    """
    Build a complete daily prompt for ChatGPT including:
    1. Yesterday's summary
    2. Project background
    3. Project files
    4. Daily goals / context instructions
    5. End-of-day summary instructions for ChatGPT including sentinel command
    """
    prompt_sections = []

    # -----------------------------
    # 1. Yesterday's Summary
    # -----------------------------
    summaries_dir = os.path.join(project_dir, "summaries")
    yesterday_summary = "No summary from yesterday."  # default placeholder
    if os.path.exists(summaries_dir):
        summary_files = sorted(os.listdir(summaries_dir))
        if summary_files:
            last_summary_file = os.path.join(summaries_dir, summary_files[-1])
            with open(last_summary_file, "r") as f:
                yesterday_summary = f.read()
    prompt_sections.append("=== Yesterday's Summary ===")
    prompt_sections.append(yesterday_summary)

    # -----------------------------
    # 2. Project Background
    # -----------------------------
    context_dir = os.path.join(project_dir, "context")
    background_file = os.path.join(context_dir, "project_background.txt")
    project_background = "No project background provided."
    if os.path.exists(background_file):
        with open(background_file, "r") as f:
            project_background = f.read()
    prompt_sections.append("=== Project Background ===")
    prompt_sections.append(project_background)

    # -----------------------------
    # 3. Project Files
    # -----------------------------
    prompt_sections.append("=== Project Files ===")
    for key, file_path in resolved_files.items():  # file_path is already a string
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
            prompt_sections.append(f"--- {key} ({file_path}) ---")
            prompt_sections.append(content)
        else:
            prompt_sections.append(f"--- {key} ({file_path}) --- [File not found]")

    # -----------------------------
    # 4. Daily Goals / Context for ChatGPT
    # -----------------------------
    prompt_sections.append("=== Daily Goals / Instructions ===")
    prompt_sections.append(
        "Assist with today's work on this project. "
        "Provide suggestions, code review, and guidance. "
        "Respect the source roots and project structure."
    )

    # -----------------------------
    # 5. End-of-Day Summary Instructions (for ChatGPT)
    # -----------------------------
    sentinel_command = project_config.get("sentinel_command", "END_OF_DAY_SUMMARY")
    prompt_sections.append("=== End of Day Instructions ===")
    prompt_sections.append(
        f"When you see the sentinel command \"{sentinel_command}\" in the conversation, "
        "generate an end-of-day summary for this project in the following format:\n"
        "1. Goals for the day\n"
        "2. Decisions made and reasoning\n"
        "3. Completed tasks\n"
        "4. Remaining tasks / next steps\n\n"
        "IMPORTANT: When the user asks for a specific change, only make that change. "
        "Do not modify anything else."
    )

    return "\n\n".join(prompt_sections)

# -----------------------------
# Load project
# -----------------------------

def load_project(project_dir):
    project_config = read_yaml_file(os.path.join(project_dir, "project.yaml"))
    project_files = read_yaml_file(os.path.join(project_dir, "project_files.yaml"))
    source_roots = project_config.get("source_roots", {})
    resolved_files = resolve_project_files(project_files, source_roots)
    return project_config, resolved_files

# -----------------------------
# Project selection
# -----------------------------

def select_or_create_project():
    projects_root = "projects"
    ensure_dir(projects_root)
    projects = sorted(os.listdir(projects_root))
    print("Available projects:")
    for idx, name in enumerate(projects, 1):
        print(f"{idx}. {name}")
    print(f"{len(projects)+1}. Create a new project")

    selection = input(f"Select a project (1-{len(projects)+1}): ").strip()
    if selection == str(len(projects)+1):
        # Create new project
        new_name = input("Enter new project name: ").strip()
        new_dir = os.path.join(projects_root, new_name)
        ensure_dir(new_dir)
        # Create empty project.yaml and project_files.yaml
        with open(os.path.join(new_dir, "project.yaml"), "w") as f:
            f.write("project_name: {}\nsentinel_command: END_OF_DAY_SUMMARY\nsource_roots: {}\n".format(new_name, "{}"))
        with open(os.path.join(new_dir, "project_files.yaml"), "w") as f:
            f.write("# Add project files here\n")
        # Create folders
        ensure_dir(os.path.join(new_dir, "prompts"))
        ensure_dir(os.path.join(new_dir, "summaries"))
        ensure_dir(os.path.join(new_dir, "context"))
        return new_dir
    else:
        idx = int(selection)-1
        return os.path.join(projects_root, projects[idx])

# -----------------------------
# Main
# -----------------------------

def main():
    project_dir = select_or_create_project()

    if "--save-summary" in sys.argv:
        save_summary(project_dir)
        return
    
    project_config, resolved_files = load_project(project_dir)

    # Build daily prompt
    prompt_text = build_daily_prompt(project_dir, project_config, resolved_files)

    # Save prompt for today
    prompts_dir = os.path.join(project_dir, "prompts")
    ensure_dir(prompts_dir)
    daily_prompt_file = os.path.join(prompts_dir, "daily_prompt.txt")
    with open(daily_prompt_file, "w") as f:
        f.write(prompt_text)
    print(f"Daily prompt saved to: {daily_prompt_file}")

    # Optional: print resolved files for testing
    print("\nResolved project files:")
    for key, path in resolved_files.items():
        print(f"{key} → {path}")

if __name__ == "__main__":
    main()
