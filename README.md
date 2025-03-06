# Local Read-Only GPT Plugin

This plugin allows ChatGPT (with access to install custom plugins) to read the structure and content of local files in your project **without write access**. It helps ChatGPT understand the context of your project, while **you** manually make all code changes.

## Folder Structure

Suppose your project looks like this:

```
myproject/
├── src/
│   └── utils.py
├── requirements.txt
└── gpt_plugin/
    ├── main.py
    ├── openapi.yaml
    └── ai-plugin.json
```

- **myproject/** – your project's root folder.
- **gpt_plugin/** – the plugin folder.
  - `main.py` – FastAPI application code (endpoints `/list-project` and `/read-file`).
  - `openapi.yaml` – OpenAPI specification for the plugin.
  - `ai-plugin.json` – the plugin manifest for ChatGPT.

## Installing Dependencies

Navigate to the plugin folder and install the required libraries:

```bash
cd myproject/gpt_plugin
pip install fastapi uvicorn
```

## Launching the Server

Run the server with:

```bash
uvicorn main:app --host 0.0.0.0 --port 3333
```

Your application is now available at [http://localhost:3333](http://localhost:3333). To view automatically generated documentation, open [http://localhost:3333/docs](http://localhost:3333/docs) in your browser.

## Testing the Endpoints

1. **List all project files**:
   - `GET /list-project`
   - If you only want to list files under a specific directory (e.g. `src`), call `GET /list-project?subdir=src`
2. **Read a file**:
   - `GET /read-file?filepath=src/utils.py` returns JSON like:
     ```json
     {
       "filepath": "src/utils.py",
       "content": "...file content..."
     }
     ```

## Using HTTPS (ngrok)

ChatGPT plugins require HTTPS. The easiest approach is to use `ngrok`:

1. Install [ngrok](https://ngrok.com/).
2. Start your server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 3333
   ```
3. In a separate terminal window:
   ```bash
   ngrok http 3333
   ```
4. You will receive a URL like `https://abc123.ngrok.io`.
5. Open `openapi.yaml` and `ai-plugin.json` and replace all `http://localhost:3333` with `https://abc123.ngrok.io`.
6. Optionally, restart the server.
7. ChatGPT Plugin Discovery can now find `ai-plugin.json` at `https://abc123.ngrok.io/static/ai-plugin.json`.

## Connecting the Plugin to ChatGPT

1. Make sure you have access to install custom plugins.
2. In ChatGPT, select "Develop your own plugin."
3. Enter `https://abc123.ngrok.io` or `https://abc123.ngrok.io/static/ai-plugin.json` (depending on where your `ai-plugin.json` is served).
4. Confirm installation.

After this, ChatGPT can call these endpoints:
- `/list-project` – view the project structure.
- `/read-file` – read the content of a specific file.

## How to Use

- While in ChatGPT with the plugin enabled, you can ask:
  > "Show me the list of files in the project."  
  or:
  > "Open the file `src/utils.py`; what's inside it?"

ChatGPT will call the endpoint and display the file content.

**Note**: Because this plugin is read-only, the assistant cannot modify files. You apply all changes manually, based on the assistant's recommendations.

## Security

- The plugin does not require authentication (`"type": "none"` in `ai-plugin.json`).
- By default, any file under the project root (except the `gpt_plugin` folder) is accessible. If you need to restrict certain directories, modify the logic in `list_project` and `read_file`.
- Keep in mind that when using ngrok (or a similar service), your project becomes externally accessible. For real-world use, add authentication and limit access to your environment.

## Additional Ideas

- **Search**: Add an endpoint to search for specific words or lines in files.
- **Large Files**: If a file is very large, you may hit ChatGPT's context limit. Returning only relevant snippets is better.
- **Git Integration**: Optionally, add endpoints to show Git commits, branches, or similar.

---

