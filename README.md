# Daily Dev Prompt Builder for Gogo

## Instructions:

### To generate a daily prompt for an existing project:
1. Open a terminal at the root of this project.
2. Enter the following command:

```bash
$ python3 tools/prompt_builder.py
```
3. Select the number corresponding to your project.
4. Open the `daily_prompt.txt` file for your project:
   - Path: `projects/<your project>/prompts/daily_prompt.txt`
5. Copy the contents into the clipboard.
6. Open a web browser and go to [ChatGPT.com](https://chatgpt.com).
7. Paste from the clipboard into ChatGPT prompt.

### To create a new project:
1. Open a terminal at the root of this project.
2. Enter the following command:

```bash
$ python3 tools/prompt_builder.py
```
3. Select the option to create a new project.
4. Name your project.
5. Manually set up the 3 input files:
   - `project_files.yaml`
   - `project.yaml`
   - `context/project_background.txt`