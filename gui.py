"""
GUI module for the Plex Duplicate Detector application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, List, Set
import threading

from scanner import scan_library, get_folder_name
from file_operations import delete_files, format_file_size, calculate_total_size


class DuplicateDetectorGUI:
    """Main GUI application for detecting and managing duplicate video files."""

    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application.

        Args:
            root: The main tkinter window
        """
        self.root = root
        self.root.title("Plex Duplicate Detector")
        self.root.geometry("900x600")

        # Data storage
        self.scan_results: Dict[str, List[Dict]] = {}
        self.checked_files: Set[str] = set()  # Set of checked file paths
        self.library_path = tk.StringVar()

        # Create GUI components
        self._create_widgets()

    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Top frame for path selection
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(top_frame, text="Library Path:").grid(row=0, column=0, padx=5)

        path_entry = ttk.Entry(top_frame, textvariable=self.library_path, width=50)
        path_entry.grid(row=0, column=1, padx=5)

        ttk.Button(top_frame, text="Browse", command=self._browse_folder).grid(
            row=0, column=2, padx=5
        )

        ttk.Button(top_frame, text="Scan", command=self._start_scan).grid(
            row=0, column=3, padx=5
        )

        help_button = ttk.Button(top_frame, text="?", width=3, command=self._show_path_help)
        help_button.grid(row=0, column=4, padx=2)

        # Middle frame for tree view
        middle_frame = ttk.Frame(self.root, padding="10")
        middle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(middle_frame, orient=tk.HORIZONTAL)

        self.tree = ttk.Treeview(
            middle_frame,
            columns=("size",),
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="none"
        )

        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading("#0", text="Movie / File")
        self.tree.heading("size", text="Size")
        self.tree.column("#0", width=600)
        self.tree.column("size", width=100)

        # Grid layout for tree and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        middle_frame.rowconfigure(0, weight=1)
        middle_frame.columnconfigure(0, weight=1)

        # Bind click event for checkbox toggling
        self.tree.bind("<Button-1>", self._on_tree_click)

        # Bottom frame for status and actions
        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.status_label = ttk.Label(bottom_frame, text="Ready to scan")
        self.status_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        bottom_frame.columnconfigure(1, weight=1)

        self.delete_button = ttk.Button(
            button_frame,
            text="Delete Selected",
            command=self._delete_selected,
            state=tk.DISABLED
        )
        self.delete_button.pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Deselect All",
            command=self._deselect_all
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Select All",
            command=self._select_all
        ).pack(side=tk.RIGHT, padx=5)

        # Separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, padx=10, fill=tk.Y)

        ttk.Button(
            button_frame,
            text="Collapse All",
            command=self._collapse_all
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Expand All",
            command=self._expand_all
        ).pack(side=tk.RIGHT, padx=5)

    def _browse_folder(self):
        """Open folder browser dialog to select library path."""
        folder = filedialog.askdirectory(title="Select Plex Library Folder")
        if folder:
            self.library_path.set(folder)

    def _show_path_help(self):
        """Show help dialog for entering paths, including SMB shares."""
        help_text = """Path Entry Help

You can either:
1. Click 'Browse' to select a local folder
2. Type a path directly into the text field

For SMB/Network Shares (Linux):
- First mount your SMB share to your filesystem
- Then enter the mount path (e.g., /mnt/nas/movies)

Example mount commands:
sudo mkdir -p /mnt/nas
sudo mount -t cifs //server/share /mnt/nas -o username=youruser

Or add to /etc/fstab for automatic mounting:
//server/share /mnt/nas cifs credentials=/home/user/.smbcreds,uid=1000,gid=1000 0 0

After mounting, you can enter the path like:
/mnt/nas/movies
"""
        messagebox.showinfo("Path Entry Help", help_text)

    def _start_scan(self):
        """Start scanning the library in a separate thread."""
        path = self.library_path.get()
        if not path:
            messagebox.showwarning("No Path", "Please select a library folder first.")
            return

        if not Path(path).exists():
            messagebox.showerror("Invalid Path", "The selected path does not exist.")
            return

        # Clear previous results
        self._clear_tree()
        self.checked_files.clear()
        self.status_label.config(text="Scanning...")
        self.delete_button.config(state=tk.DISABLED)

        # Run scan in separate thread to keep GUI responsive
        scan_thread = threading.Thread(target=self._perform_scan, args=(path,), daemon=True)
        scan_thread.start()

    def _perform_scan(self, path: str):
        """
        Perform the actual scanning operation.

        Args:
            path: Library path to scan
        """
        try:
            results = scan_library(path)
            # Update GUI from main thread
            self.root.after(0, self._display_results, results)
        except Exception as e:
            self.root.after(0, self._show_scan_error, str(e))

    def _display_results(self, results: Dict[str, List[Dict]]):
        """
        Display scan results in the tree view.

        Args:
            results: Dictionary mapping folder paths to video file lists
        """
        self.scan_results = results
        self._clear_tree()

        if not results:
            self.status_label.config(text="No duplicates found")
            return

        # Populate tree with results
        for folder_path, video_files in sorted(results.items()):
            folder_name = get_folder_name(folder_path)
            file_count = len(video_files)

            # Insert parent (movie folder)
            parent_text = f"☐ {folder_name} ({file_count} files)"
            parent_id = self.tree.insert(
                "",
                tk.END,
                text=parent_text,
                values=("",),
                tags=("folder", folder_path)
            )

            # Insert children (video files)
            for video_file in sorted(video_files, key=lambda x: x['filename']):
                child_text = f"☐ {video_file['filename']}"
                size_text = format_file_size(video_file['size'])
                self.tree.insert(
                    parent_id,
                    tk.END,
                    text=child_text,
                    values=(size_text,),
                    tags=("file", video_file['full_path'])
                )

        # Update status
        total_movies = len(results)
        self.status_label.config(text=f"Total: {total_movies} movie(s) with duplicates")

    def _show_scan_error(self, error_msg: str):
        """Show error message if scan fails."""
        self.status_label.config(text="Scan failed")
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_msg}")

    def _clear_tree(self):
        """Clear all items from the tree view."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _on_tree_click(self, event):
        """
        Handle tree item click to toggle checkboxes.

        Args:
            event: Click event
        """
        item = self.tree.identify_row(event.y)
        if not item:
            return

        tags = self.tree.item(item, "tags")
        if not tags:
            return

        if tags[0] == "file":
            # Toggle file checkbox
            file_path = tags[1]
            self._toggle_file(item, file_path)
        elif tags[0] == "folder":
            # Toggle all files in folder
            self._toggle_folder(item)

        # Update delete button state
        self._update_delete_button()

    def _toggle_file(self, item_id: str, file_path: str):
        """
        Toggle checkbox state for a file.

        Args:
            item_id: Tree item ID
            file_path: Full path to the file
        """
        current_text = self.tree.item(item_id, "text")

        if file_path in self.checked_files:
            # Uncheck
            self.checked_files.remove(file_path)
            new_text = current_text.replace("☑", "☐")
        else:
            # Check
            self.checked_files.add(file_path)
            new_text = current_text.replace("☐", "☑")

        self.tree.item(item_id, text=new_text)

    def _toggle_folder(self, parent_id: str):
        """
        Toggle all files in a folder.

        Args:
            parent_id: Tree item ID of the parent folder
        """
        children = self.tree.get_children(parent_id)
        if not children:
            return

        # Determine if we should check or uncheck based on first child
        first_child = children[0]
        first_child_tags = self.tree.item(first_child, "tags")
        if first_child_tags and first_child_tags[0] == "file":
            first_file_path = first_child_tags[1]
            should_check = first_file_path not in self.checked_files

            # Toggle all children
            for child in children:
                child_tags = self.tree.item(child, "tags")
                if child_tags and child_tags[0] == "file":
                    file_path = child_tags[1]
                    if should_check:
                        self.checked_files.add(file_path)
                        new_text = self.tree.item(child, "text").replace("☐", "☑")
                    else:
                        self.checked_files.discard(file_path)
                        new_text = self.tree.item(child, "text").replace("☑", "☐")
                    self.tree.item(child, text=new_text)

            # Update parent checkbox
            parent_text = self.tree.item(parent_id, "text")
            if should_check:
                new_parent_text = parent_text.replace("☐", "☑")
            else:
                new_parent_text = parent_text.replace("☑", "☐")
            self.tree.item(parent_id, text=new_parent_text)

    def _select_all(self):
        """Select all files in the tree."""
        for parent in self.tree.get_children():
            for child in self.tree.get_children(parent):
                tags = self.tree.item(child, "tags")
                if tags and tags[0] == "file":
                    file_path = tags[1]
                    self.checked_files.add(file_path)
                    new_text = self.tree.item(child, "text").replace("☐", "☑")
                    self.tree.item(child, text=new_text)

            # Update parent checkbox
            parent_text = self.tree.item(parent, "text").replace("☐", "☑")
            self.tree.item(parent, text=parent_text)

        self._update_delete_button()

    def _deselect_all(self):
        """Deselect all files in the tree."""
        self.checked_files.clear()

        for parent in self.tree.get_children():
            for child in self.tree.get_children(parent):
                current_text = self.tree.item(child, "text")
                new_text = current_text.replace("☑", "☐")
                self.tree.item(child, text=new_text)

            # Update parent checkbox
            parent_text = self.tree.item(parent, "text").replace("☑", "☐")
            self.tree.item(parent, text=parent_text)

        self._update_delete_button()

    def _update_delete_button(self):
        """Enable or disable delete button based on selection."""
        if self.checked_files:
            self.delete_button.config(state=tk.NORMAL)
        else:
            self.delete_button.config(state=tk.DISABLED)

    def _expand_all(self):
        """Expand all movie folders in the tree."""
        for item in self.tree.get_children():
            self.tree.item(item, open=True)

    def _collapse_all(self):
        """Collapse all movie folders in the tree."""
        for item in self.tree.get_children():
            self.tree.item(item, open=False)

    def _delete_selected(self):
        """Delete selected files after confirmation."""
        if not self.checked_files:
            return

        file_list = list(self.checked_files)
        file_count = len(file_list)
        total_size = calculate_total_size(file_list)
        size_text = format_file_size(total_size)

        # Show confirmation dialog
        message = (
            f"Are you sure you want to delete {file_count} file(s)?\n\n"
            f"Total size: {size_text}\n\n"
            f"This action cannot be undone!"
        )

        if not messagebox.askyesno("Confirm Deletion", message):
            return

        # Perform deletion
        results = delete_files(file_list)

        # Count successes and failures
        successes = sum(1 for status in results.values() if status == "success")
        failures = file_count - successes

        # Show results
        if failures == 0:
            messagebox.showinfo(
                "Deletion Complete",
                f"Successfully deleted {successes} file(s)."
            )
        else:
            error_details = "\n".join(
                f"- {Path(path).name}: {status}"
                for path, status in results.items()
                if status != "success"
            )
            messagebox.showwarning(
                "Deletion Completed with Errors",
                f"Deleted {successes} file(s).\n"
                f"Failed to delete {failures} file(s):\n\n{error_details}"
            )

        # Rescan to update the view
        self._start_scan()

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
