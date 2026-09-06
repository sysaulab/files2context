
# files2context

An ugly GUI tool that compiles text files into a single Markdown-formatted context, ready for pasting into chatbots, LLM prompts, or documentation.

![Screenshot placeholder](screenshot.png)

---

## Features

- **Add files or entire folders** recursively (ignores dotfiles and dotfolders by default).
- **Custom file/folder entry** – paste or type a path directly.
- **Markdown code blocks** – each file is wrapped in a fenced code block with:
  - The file’s relative path (from the common base folder) as the info string.
  - Syntax highlighting hints based on file extension (e.g., `.py` → `python`).
- **Token counting** – optionally shows token budget (using `tiktoken`’s `cl100k_base` encoding, used by GPT‑4/ChatGPT).
- **Copy to clipboard** – one‑click copy of the generated Markdown.
- **Save as `.md`** – export to a file.
- **Manage file list** – remove individual entries or clear all.
- **Status bar** – displays total byte size and token count (if `tiktoken` is installed).

---

## Installation

Clone the repository and run the script directly (requires Python 3.6+).

```bash
git clone https://github.com/yourusername/files2context.git
cd files2context
python files2context.py
```

No installation is required – it’s a single-file Python script using only the standard library plus an optional third‑party module.

---

## Dependencies

- **Python 3.6+** with Tkinter (usually included with standard Python distributions).
- **Optional**: [tiktoken](https://github.com/openai/tiktoken) – install to display token counts:

  ```bash
  pip install tiktoken
  ```

  If `tiktoken` is not installed, the status bar will show a reminder instead of the token count.

---

## Usage

### GUI Mode

Launch the script without arguments:

```bash
python files2context.py
```

The main window offers:

- **Add Files** – select one or more files via a file dialog.
- **Add Folder** – pick a folder; all files inside (recursively) will be added, excluding hidden entries.
- **Add path (file or folder)** – enter a filesystem path manually and click **Add**.
- **Remove Selected** – delete the highlighted entries from the list.
- **Clear All** – remove every file from the list.
- **Copy to Clipboard** – copy the entire generated Markdown.
- **Save as .md** – save the content to a `.md` file.

The generated Markdown updates automatically as you modify the file list.

### Command‑Line Arguments

You can pass file or folder paths directly when starting the script. They will be added automatically after a short delay.

```bash
python files2context.py /path/to/file.txt /path/to/folder
```

---

## How It Works

1. **File collection** – the tool gathers all specified file paths (expanding folders recursively) while ignoring entries starting with a dot (`.`).
2. **Common base path** – computes the longest common prefix of all selected files to create relative paths in the Markdown output.
3. **Markdown generation** – for each file, it produces a fenced code block:

   ````markdown
   ```python:src/main.py
   print("Hello, world!")
   ```
   ````

   - The language identifier is derived from the file extension (see [Extension Mapping](#extension-mapping)).
   - The path is shown relative to the common base, using forward slashes for cross‑platform consistency.
4. **Token estimation** – if `tiktoken` is available, the entire Markdown text is encoded with the `cl100k_base` tokenizer and the token count is displayed in the status bar alongside the byte size.

---

## Extension Mapping

The tool maps common file extensions to Markdown code block language tags. If an extension is not recognised, it falls back to the extension itself (without the dot) or `text`.

| Extension | Language |
|-----------|----------|
| `.py`     | `python` |
| `.js`     | `js`     |
| `.jsx`    | `jsx`    |
| `.ts`     | `ts`     |
| `.tsx`    | `tsx`    |
| `.java`   | `java`   |
| `.c`      | `c`      |
| `.cpp`    | `cpp`    |
| `.h`      | `h`      |
| `.cs`     | `csharp` |
| `.go`     | `go`     |
| `.rb`     | `ruby`   |
| `.php`    | `php`    |
| `.html`   | `html`   |
| `.css`    | `css`    |
| `.scss`   | `scss`   |
| `.less`   | `less`   |
| `.json`   | `json`   |
| `.xml`    | `xml`    |
| `.yaml`   | `yaml`   |
| `.toml`   | `toml`   |
| `.md`     | `markdown` |
| `.sh`     | `bash`   |
| … and many more. See the `LANG_MAP` dictionary in the source.

---

## Example

Suppose you have a project with the following files:

```
my_project/
├── src/
│   └── main.py
└── README.md
```

After adding the folder `my_project`, the generated Markdown looks like:

````markdown
```python:src/main.py
# Content of main.py
```

```markdown:README.md
# Content of README.md
```
````

This can be pasted directly into a chatbot to provide full context.

---

## License

This project is provided under the [MIT License](LICENSE) (if you include a LICENSE file).  
Feel free to use, modify, and distribute it as you see fit.
