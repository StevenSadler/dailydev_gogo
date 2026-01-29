# Daily Dev Prompt Builder for Gogo

Instructions:

To generate a daily prompt for an existing project:
    Open a terminal at the root of this project.
    At the terminal, enter this command:
        $ python3 tools/prompt_builder.py
    Select the number corresponding to your project.
    Open the daily_prompt.txt for your project:
        projects/<your project>/prompts/daily_prompt.txt
    Copy the contents into the clipboard.

    Open web browser and go to ChatGPT.com
    Paste from the clipboard into ChatGPT prompt.

To create a new project:
    Open a terminal at the root of this project.
    At the terminal, enter this command:
        $ python3 tools/prompt_builder.py
    Select the number corresponding to create a new project.
    Name the project.
    Manually set up the 3 input files:
        project_files.yaml
        project.yaml
        context/project_background.txt

    