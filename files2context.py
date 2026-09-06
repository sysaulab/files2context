#!/usr/bin/env python3
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Optional DND Support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# Try to import tiktoken for token counting (Optional)
try:
    import tiktoken
    TOKENIZER_AVAILABLE = True
except ImportError:
    TOKENIZER_AVAILABLE = False

# File extensions to Markdown code block language identifiers
LANG_MAP = {
    'py': 'python', 'js': 'js', 'jsx': 'jsx', 'ts': 'ts', 'tsx': 'tsx',
    'java': 'java', 'c': 'c', 'cpp': 'cpp', 'h': 'h', 'cs': 'csharp',
    'html': 'html', 'css': 'css', 'json': 'json', 'md': 'markdown',
    'sh': 'bash', 'yml': 'yaml', 'yaml': 'yaml', 'txt': 'text',
    'xml': 'xml', 'sql': 'sql', 'rb': 'ruby', 'go': 'go', 'rs': 'rust'
}

class MarkdownAggregatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown File Aggregator")
        self.root.geometry("900x750")
        
        # Define fonts for a polished look
        mono_font = ("Menlo", 11)
        
        # Top Toolbar
        top_frame = ttk.Frame(root, padding=10)
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Save as .md", command=self.save_as_md).pack(side=tk.LEFT, padx=2)

        # DND Status Label
        dnd_status = "DND Active (Drop files here)" if DND_AVAILABLE else "DND Disabled (Install tkinterdnd2)"
        ttk.Label(top_frame, text=dnd_status, foreground="green" if DND_AVAILABLE else "grey").pack(side=tk.RIGHT)

        # Add Path Frame
        path_frame = ttk.Frame(root, padding=10)
        path_frame.pack(fill=tk.X)
        ttk.Label(path_frame, text="Add path (file or folder):").pack(anchor=tk.W)
        
        self.path_entry = ttk.Entry(path_frame)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(path_frame, text="Add", command=self.add_manual_path).pack(side=tk.RIGHT)

        # Files Added Frame
        files_frame = ttk.Frame(root, padding=10)
        files_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(files_frame, text="Files added (select to remove):").pack(anchor=tk.W)
        
        self.file_listbox = tk.Listbox(files_frame, selectmode=tk.EXTENDED, font=mono_font)
        scrollbar1 = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar1.set)
        
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # DND Binding for Listbox
        if DND_AVAILABLE:
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.on_drop)
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)

        # Generated Markdown Frame
        output_frame = ttk.Frame(root, padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(output_frame, text="Generated Markdown (copy this):").pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=mono_font)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Status Bar
        self.status_label = ttk.Label(root, text="Total size: 0 bytes | 0 tokens", relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select Files")
        for path in paths:
            self.add_path_to_list(path)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    self.add_path_to_list(os.path.join(root, file))

    def add_manual_path(self):
        path = self.path_entry.get().strip()
        if path:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        self.add_path_to_list(os.path.join(root, file))
            elif os.path.isfile(path):
                self.add_path_to_list(path)
            else:
                messagebox.showerror("Error", f"Path does not exist: {path}")
            self.path_entry.delete(0, tk.END)

    def add_path_to_list(self, path):
        # Avoid duplicates
        if path not in self.file_listbox.get(0, tk.END):
            self.file_listbox.insert(tk.END, path)
            self.refresh_preview()

    def remove_selected(self):
        for index in reversed(self.file_listbox.curselection()):
            self.file_listbox.delete(index)
        self.refresh_preview()

    def clear_all(self):
        self.file_listbox.delete(0, tk.END)
        self.refresh_preview()

    def on_drop(self, event):
        # TkDND wraps paths with spaces in braces, and separates multiple files with spaces
        paths = self.root.tk.splitlist(event.data)
        for path in paths:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        self.add_path_to_list(os.path.join(root, file))
            else:
                self.add_path_to_list(path)

    def refresh_preview(self):
        files = self.file_listbox.get(0, tk.END)
        markdown = ""
        total_size = 0

        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                total_size += len(content.encode('utf-8'))
                ext = os.path.splitext(file_path)[1].lstrip('.').lower()
                lang = LANG_MAP.get(ext, ext)
                
                # Use full path for clarity
                markdown += f"```{lang}:{file_path}\n{content}\n```\n\n"
            except Exception as e:
                markdown += f"Error reading {file_path}: {e}\n\n"

        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, markdown)

        # Token Count
        token_count = 0
        if TOKENIZER_AVAILABLE and markdown:
            try:
                enc = tiktoken.get_encoding("cl100k_base")
                token_count = len(enc.encode(markdown))
            except:
                token_count = 0

        self.status_label.config(text=f"Total size: {total_size:,} bytes | {token_count:,} tokens")

    def copy_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        messagebox.showinfo("Success", "Copied Markdown to clipboard!")

    def save_as_md(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown Files", "*.md")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.output_text.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Saved to {file_path}")

if __name__ == "__main__":
    # Conditional root initialization for optional DND
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        
    app = MarkdownAggregatorApp(root)
    root.mainloop()