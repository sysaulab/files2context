#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import os
import sys

# Try to import tiktoken for token counting
try:
    import tiktoken
    TOKENIZER = tiktoken.get_encoding("cl100k_base")  # used by GPT-4, ChatGPT
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TOKENIZER = None
    TIKTOKEN_AVAILABLE = False

# Map file extensions to Markdown code block language identifiers
LANG_MAP = {
    '.py': 'python', '.js': 'js', '.jsx': 'jsx', '.ts': 'ts', '.tsx': 'tsx',
    '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.h': 'h', '.cs': 'csharp',
    '.go': 'go', '.rb': 'ruby', '.php': 'php', '.html': 'html', '.htm': 'html',
    '.css': 'css', '.scss': 'scss', '.less': 'less', '.json': 'json',
    '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml', '.toml': 'toml',
    '.md': 'markdown', '.sh': 'bash', '.bash': 'bash', '.ps1': 'powershell',
    '.sql': 'sql', '.r': 'r', '.rs': 'rust', '.swift': 'swift', '.kt': 'kotlin',
    '.dart': 'dart', '.lua': 'lua', '.pl': 'perl', '.pm': 'perl',
    '.tcl': 'tcl', '.vim': 'vim', '.tex': 'latex', '.txt': 'text',
}

def get_language(ext):
    return LANG_MAP.get(ext.lower(), ext.lstrip('.') or 'text')

def read_file_content(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding=sys.getfilesystemencoding()) as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file: {e}]"
    except Exception as e:
        return f"[Error reading file: {e}]"

class FileAggregatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown File Aggregator")
        self.root.geometry("950x750")

        self.file_paths = []  # list of absolute paths

        # --- Top button row ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5, fill=tk.X)

        tk.Button(btn_frame, text="Add Files", command=self.add_files, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Add Folder", command=self.add_folder, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Remove Selected", command=self.remove_selected, width=15).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Clear All", command=self.clear_all, width=10).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Copy to Clipboard", command=self.copy_to_clipboard, width=18).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Save as .md", command=self.save_to_file, width=12).pack(side=tk.LEFT, padx=2)

        # --- Entry for adding a custom path ---
        path_entry_frame = tk.Frame(root)
        path_entry_frame.pack(pady=5, fill=tk.X, padx=10)

        tk.Label(path_entry_frame, text="Add path (file or folder):").pack(side=tk.LEFT)
        self.path_entry = tk.Entry(path_entry_frame, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(path_entry_frame, text="Add", command=self.add_path_from_entry, width=8).pack(side=tk.LEFT, padx=2)

        # --- File list ---
        list_frame = tk.Frame(root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tk.Label(list_frame, text="Files added (select to remove):").pack(anchor=tk.W)

        listbox_frame = tk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(listbox_frame, height=6, selectmode=tk.EXTENDED)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # --- Markdown output ---
        output_frame = tk.Frame(root)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tk.Label(output_frame, text="Generated Markdown (copy this):").pack(anchor=tk.W)

        self.text_area = scrolledtext.ScrolledText(
            output_frame, wrap=tk.WORD, font=("Courier New", 10)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # --- Status bar ---
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # If command-line arguments were given, add them
        if len(sys.argv) > 1:
            self.root.after(100, lambda: self.add_paths(sys.argv[1:]))

        self.update_output()

    def add_paths(self, paths):
        """Add a list of file/directory paths (expand directories recursively), skipping dotfiles/dotfolders."""
        new_files = []
        for p in paths:
            p = os.path.abspath(p)
            # Skip dotfiles/dotfolders at the root level
            basename = os.path.basename(p)
            if basename.startswith('.'):
                continue

            if os.path.isfile(p):
                if p not in self.file_paths:
                    new_files.append(p)
            elif os.path.isdir(p):
                # Walk recursively, but prune dot directories and skip dot files
                for dirpath, dirnames, filenames in os.walk(p):
                    # Remove dot directories from dirnames so os.walk won't descend into them
                    dirnames[:] = [d for d in dirnames if not d.startswith('.')]
                    # Skip dot files
                    for f in filenames:
                        if f.startswith('.'):
                            continue
                        full = os.path.join(dirpath, f)
                        if full not in self.file_paths:
                            new_files.append(full)
            else:
                messagebox.showwarning("Invalid path", f"Path not found: {p}")

        if new_files:
            self.file_paths.extend(new_files)
            self.update_output()
            self.update_listbox()
            messagebox.showinfo("Files added", f"Added {len(new_files)} file(s).")
        else:
            messagebox.showinfo("No new files", "All paths already added or no valid files found (dotfiles ignored).")

    def add_files(self):
        """Add files via file dialog."""
        new_paths = filedialog.askopenfilenames(
            title="Select text files",
            filetypes=[("All files", "*.*")]
        )
        if new_paths:
            self.add_paths(new_paths)

    def add_folder(self):
        """Add all files from a folder recursively."""
        folder = filedialog.askdirectory(title="Select a folder to add recursively")
        if folder:
            self.add_paths([folder])

    def add_path_from_entry(self):
        """Add the path entered in the entry field."""
        path = self.path_entry.get().strip()
        if path:
            self.add_paths([path])
            self.path_entry.delete(0, tk.END)

    def remove_selected(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("No selection", "Please select files to remove.")
            return
        for idx in reversed(selected):
            del self.file_paths[idx]
        self.update_output()
        self.update_listbox()

    def clear_all(self):
        if self.file_paths:
            self.file_paths.clear()
            self.update_output()
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for p in self.file_paths:
            self.listbox.insert(tk.END, p)

    def compute_common_base(self):
        if not self.file_paths:
            return None
        try:
            return os.path.commonpath(self.file_paths)
        except ValueError:
            return None

    def update_output(self):
        """Rebuild Markdown, update text area, and refresh status bar."""
        if not self.file_paths:
            self.text_area.delete(1.0, tk.END)
            self.status_var.set("No files")
            return

        base = self.compute_common_base()
        markdown_parts = []

        for path in self.file_paths:
            content = read_file_content(path)
            if base is not None:
                rel = os.path.relpath(path, base)
            else:
                rel = os.path.abspath(path)
            rel = rel.replace(os.sep, '/')
            _, ext = os.path.splitext(path)
            lang = get_language(ext)
            code_block = f"```{lang}:{rel}\n{content}\n```"
            markdown_parts.append(code_block)

        full_markdown = "\n\n".join(markdown_parts)

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, full_markdown)

        # Update status bar
        self.update_status(full_markdown)

    def update_status(self, markdown_text):
        """Compute size in bytes and tokens and show in status bar."""
        text_bytes = len(markdown_text.encode('utf-8'))
        if TIKTOKEN_AVAILABLE and TOKENIZER:
            try:
                token_count = len(TOKENIZER.encode(markdown_text))
                token_str = f"{token_count:,} tokens"
            except Exception:
                token_str = "token count unavailable"
        else:
            token_str = "tiktoken not installed – install for token count"

        self.status_var.set(f"Total size: {text_bytes:,} bytes  |  {token_str}")

    def copy_to_clipboard(self):
        content = self.text_area.get(1.0, tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Copied", "Markdown copied to clipboard.")
        else:
            messagebox.showwarning("Nothing to copy", "No files added or content empty.")

    def save_to_file(self):
        content = self.text_area.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Nothing to save", "No files added or content empty.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Markdown saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")

def main():
    root = tk.Tk()
    app = FileAggregatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()