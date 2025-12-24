"""
GUI module for the Plex Duplicate Detector application.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Dict, List, Set
import threading

from scanner import (
    scan_library, get_folder_name,
    find_duplicate_folders_exact, find_duplicate_folders_fuzzy,
    get_folder_stats
)
from file_operations import delete_files, format_file_size, calculate_total_size
from folder_tags import FolderTagManager
from tooltip import TreeviewTooltip, get_path_from_tags
from quality_analyzer import QualityAnalyzer


class DuplicateDetectorGUI:
    """Main GUI application for detecting and managing duplicate video files."""

    # UI Dimension Constants
    PATHS_LISTBOX_HEIGHT = 3
    PATHS_LISTBOX_WIDTH = 50
    CONTENTS_DIALOG_WIDTH = 600
    CONTENTS_DIALOG_HEIGHT = 400

    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application.

        Args:
            root: The main tkinter window
        """
        self.root = root
        self.root.title("Plex Duplicate Detector")
        self.root.geometry("900x600")

        # Data storage - Video Files Tab
        self.scan_results: Dict[str, List[Dict]] = {}
        self.checked_files: Set[str] = set()  # Set of checked file paths

        # Data storage - Duplicate Folders Tab
        self.folder_scan_results: Dict[str, List[str]] = {}  # group_id -> folder paths
        self.folder_metadata: Dict[str, Dict] = {}  # folder_path -> stats
        self.checked_folders: Set[str] = set()  # Set of checked folder paths
        self.matching_mode = tk.StringVar(value="exact")
        self.similarity_threshold = tk.IntVar(value=80)
        self.scan_scope = tk.StringVar(value="single")
        self.additional_paths: List[str] = []

        # Shared data
        self.library_path = tk.StringVar()

        # Initialize tag manager
        self.tag_manager = FolderTagManager()
        self.tagged_folders = self.tag_manager.load_tags()

        # Create GUI components
        self._create_widgets()

    def _create_widgets(self):
        """Create and layout all GUI widgets."""
        # Top frame for shared path selection
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(top_frame, text="Library Path:").grid(row=0, column=0, padx=5)

        path_entry = ttk.Entry(top_frame, textvariable=self.library_path, width=50)
        path_entry.grid(row=0, column=1, padx=5)

        ttk.Button(top_frame, text="Browse", command=self._shared_browse_folder).grid(
            row=0, column=2, padx=5
        )

        help_button = ttk.Button(top_frame, text="?", width=3, command=self._shared_show_path_help)
        help_button.grid(row=0, column=3, padx=2)

        # Create tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Create Tab 1: Video Files
        self._create_video_files_tab()

        # Create Tab 2: Duplicate Folders
        self._create_duplicate_folders_tab()

    def _create_video_files_tab(self):
        """Create the Video Files tab with existing functionality."""
        # Create tab container
        video_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(video_tab, text="Video Files")

        # Control frame for scan button
        control_frame = ttk.Frame(video_tab)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Button(control_frame, text="Scan", command=self._video_start_scan).pack(side=tk.LEFT, padx=5)

        # Middle frame for tree view
        middle_frame = ttk.Frame(video_tab)
        middle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        video_tab.rowconfigure(1, weight=1)
        video_tab.columnconfigure(0, weight=1)

        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(middle_frame, orient=tk.HORIZONTAL)

        self.video_tree = ttk.Treeview(
            middle_frame,
            columns=("size",),
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="none"
        )

        tree_scroll_y.config(command=self.video_tree.yview)
        tree_scroll_x.config(command=self.video_tree.xview)

        # Configure columns
        self.video_tree.heading("#0", text="Movie / File")
        self.video_tree.heading("size", text="Size")
        self.video_tree.column("#0", width=600)
        self.video_tree.column("size", width=100)

        # Grid layout for tree and scrollbars
        self.video_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        middle_frame.rowconfigure(0, weight=1)
        middle_frame.columnconfigure(0, weight=1)

        # Bind click event for checkbox toggling
        self.video_tree.bind("<Button-1>", self._video_on_tree_click)

        # Add tooltip support for showing full paths
        TreeviewTooltip(self.video_tree, lambda item_id: get_path_from_tags(self.video_tree, item_id))

        # Bottom frame for status and actions
        bottom_frame = ttk.Frame(video_tab)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.video_status_label = ttk.Label(bottom_frame, text="Ready to scan")
        self.video_status_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        bottom_frame.columnconfigure(1, weight=1)

        self.video_delete_button = ttk.Button(
            button_frame,
            text="Delete Selected",
            command=self._video_delete_selected,
            state=tk.DISABLED
        )
        self.video_delete_button.pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Deselect All",
            command=self._video_deselect_all
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Select All",
            command=self._video_select_all
        ).pack(side=tk.RIGHT, padx=5)

        # Separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, padx=10, fill=tk.Y)

        ttk.Button(
            button_frame,
            text="Collapse All",
            command=self._video_collapse_all
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Expand All",
            command=self._video_expand_all
        ).pack(side=tk.RIGHT, padx=5)

    def _create_duplicate_folders_tab(self):
        """Create the Duplicate Folders tab."""
        # Create tab container
        folder_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(folder_tab, text="Duplicate Folders")

        # Control frame - top of tab
        control_frame = ttk.Frame(folder_tab)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Row 1: Matching mode and threshold
        ttk.Label(control_frame, text="Matching Mode:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        mode_frame = ttk.Frame(control_frame)
        mode_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Radiobutton(
            mode_frame,
            text="Exact",
            variable=self.matching_mode,
            value="exact",
            command=self._folder_on_mode_change
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            mode_frame,
            text="Fuzzy",
            variable=self.matching_mode,
            value="fuzzy",
            command=self._folder_on_mode_change
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(control_frame, text="Similarity:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)

        self.folder_threshold_scale = ttk.Scale(
            control_frame,
            from_=50,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.similarity_threshold,
            length=150,
            state=tk.DISABLED
        )
        self.folder_threshold_scale.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        self.folder_threshold_label = ttk.Label(control_frame, text="80%")
        self.folder_threshold_label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)

        # Update threshold label when slider changes
        self.similarity_threshold.trace_add("write", self._folder_update_threshold_label)

        # Row 2: Scan scope and scan button
        ttk.Label(control_frame, text="Scan Scope:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        scope_frame = ttk.Frame(control_frame)
        scope_frame.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Radiobutton(
            scope_frame,
            text="Single Path",
            variable=self.scan_scope,
            value="single",
            command=self._folder_on_scope_change
        ).pack(side=tk.LEFT, padx=5)

        ttk.Radiobutton(
            scope_frame,
            text="Multiple Paths",
            variable=self.scan_scope,
            value="multiple",
            command=self._folder_on_scope_change
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="Scan for Duplicates",
            command=self._folder_start_scan
        ).grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)

        # Row 3: Multiple paths list (initially hidden)
        self.folder_paths_frame = ttk.Frame(control_frame)
        self.folder_paths_frame.grid(row=2, column=0, columnspan=5, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.folder_paths_frame.grid_remove()  # Hide initially

        ttk.Label(self.folder_paths_frame, text="Additional Paths:").pack(side=tk.LEFT, padx=5)

        self.folder_paths_listbox = tk.Listbox(
            self.folder_paths_frame,
            height=self.PATHS_LISTBOX_HEIGHT,
            width=self.PATHS_LISTBOX_WIDTH
        )
        self.folder_paths_listbox.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        paths_button_frame = ttk.Frame(self.folder_paths_frame)
        paths_button_frame.pack(side=tk.LEFT, padx=5)

        ttk.Button(paths_button_frame, text="Add Path", command=self._folder_add_path).pack(side=tk.TOP, pady=2)
        ttk.Button(paths_button_frame, text="Remove", command=self._folder_remove_path).pack(side=tk.TOP, pady=2)

        # Middle frame for tree view
        middle_frame = ttk.Frame(folder_tab)
        middle_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        folder_tab.rowconfigure(1, weight=1)
        folder_tab.columnconfigure(0, weight=1)

        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(middle_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(middle_frame, orient=tk.HORIZONTAL)

        self.folder_tree = ttk.Treeview(
            middle_frame,
            columns=("videos", "size", "tags"),
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="none"
        )

        tree_scroll_y.config(command=self.folder_tree.yview)
        tree_scroll_x.config(command=self.folder_tree.xview)

        # Configure columns
        self.folder_tree.heading("#0", text="Folder Name")
        self.folder_tree.heading("videos", text="Videos")
        self.folder_tree.heading("size", text="Size")
        self.folder_tree.heading("tags", text="Tags")

        self.folder_tree.column("#0", width=400)
        self.folder_tree.column("videos", width=80)
        self.folder_tree.column("size", width=100)
        self.folder_tree.column("tags", width=80)

        # Grid layout for tree and scrollbars
        self.folder_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        middle_frame.rowconfigure(0, weight=1)
        middle_frame.columnconfigure(0, weight=1)

        # Bind click event for checkbox toggling
        self.folder_tree.bind("<Button-1>", self._folder_on_tree_click)

        # Add tooltip support for showing full paths
        TreeviewTooltip(self.folder_tree, lambda item_id: get_path_from_tags(self.folder_tree, item_id))

        # Bottom frame for status and actions
        bottom_frame = ttk.Frame(folder_tab)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        self.folder_status_label = ttk.Label(bottom_frame, text="Ready to scan")
        self.folder_status_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        button_frame = ttk.Frame(bottom_frame)
        button_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.E)
        bottom_frame.columnconfigure(1, weight=1)

        # Action buttons
        self.folder_export_button = ttk.Button(
            button_frame,
            text="Export Tagged",
            command=self._folder_export_tagged,
            state=tk.DISABLED
        )
        self.folder_export_button.pack(side=tk.RIGHT, padx=5)

        self.folder_clear_tags_button = ttk.Button(
            button_frame,
            text="Clear Tags",
            command=self._folder_clear_tags,
            state=tk.DISABLED
        )
        self.folder_clear_tags_button.pack(side=tk.RIGHT, padx=5)

        self.folder_tag_button = ttk.Button(
            button_frame,
            text="Tag Selected",
            command=self._folder_tag_selected,
            state=tk.DISABLED
        )
        self.folder_tag_button.pack(side=tk.RIGHT, padx=5)

        self.folder_view_contents_button = ttk.Button(
            button_frame,
            text="View Contents",
            command=self._folder_view_contents,
            state=tk.DISABLED
        )
        self.folder_view_contents_button.pack(side=tk.RIGHT, padx=5)

        # Separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(side=tk.RIGHT, padx=10, fill=tk.Y)

        ttk.Button(
            button_frame,
            text="Collapse All",
            command=self._folder_collapse_all
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Expand All",
            command=self._folder_expand_all
        ).pack(side=tk.RIGHT, padx=5)

    # ===== Shared Methods (used by both tabs) =====

    def _shared_browse_folder(self):
        """Open folder browser dialog to select library path."""
        folder = filedialog.askdirectory(title="Select Plex Library Folder")
        if folder:
            self.library_path.set(folder)

    def _shared_show_path_help(self):
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

    # ===== Video Files Tab Methods =====

    def _video_start_scan(self):
        """Start scanning the library in a separate thread."""
        path = self.library_path.get()
        if not path:
            messagebox.showwarning("No Path", "Please select a library folder first.")
            return

        if not Path(path).exists():
            messagebox.showerror("Invalid Path", "The selected path does not exist.")
            return

        # Clear previous results
        self._video_clear_tree()
        self.checked_files.clear()
        self.video_status_label.config(text="Scanning...")
        self.video_delete_button.config(state=tk.DISABLED)

        # Run scan in separate thread to keep GUI responsive
        scan_thread = threading.Thread(target=self._video_perform_scan, args=(path,), daemon=True)
        scan_thread.start()

    def _video_perform_scan(self, path: str):
        """
        Perform the actual scanning operation.

        Args:
            path: Library path to scan
        """
        try:
            results = scan_library(path)
            # Update GUI from main thread
            self.root.after(0, self._video_display_results, results)
        except Exception as e:
            self.root.after(0, self._video_show_scan_error, str(e))

    def _video_display_results(self, results: Dict[str, List[Dict]]):
        """
        Display scan results in the tree view.

        Args:
            results: Dictionary mapping folder paths to video file lists
        """
        self.scan_results = results
        self._video_clear_tree()

        if not results:
            self.video_status_label.config(text="No duplicates found")
            return

        # Initialize quality analyzer
        analyzer = QualityAnalyzer(use_metadata=False)

        # Populate tree with results
        for folder_path, video_files in sorted(results.items()):
            folder_name = get_folder_name(folder_path)
            file_count = len(video_files)

            # Find best file in this folder (only if 2+ files)
            best_file_path = None
            if len(video_files) >= 2:
                best_score = -1
                best_name = None

                for video_file in video_files:
                    score = analyzer.analyze_video_file(
                        video_file['full_path'],
                        video_file['size']
                    )

                    # Track best score, use alphabetical order for ties
                    if score.total_score > best_score:
                        best_score = score.total_score
                        best_file_path = video_file['full_path']
                        best_name = video_file['filename']
                    elif score.total_score == best_score and best_name:
                        # Tie: pick alphabetically first
                        if video_file['filename'] < best_name:
                            best_file_path = video_file['full_path']
                            best_name = video_file['filename']

            # Insert parent (movie folder)
            parent_text = f"☐ {folder_name} ({file_count} files)"
            parent_id = self.video_tree.insert(
                "",
                tk.END,
                text=parent_text,
                values=("",),
                tags=("folder", folder_path)
            )

            # Insert children (video files)
            for video_file in sorted(video_files, key=lambda x: x['filename']):
                # Add star if this is the best file
                is_best = (video_file['full_path'] == best_file_path)
                star = "⭐ " if is_best else ""
                child_text = f"☐ {star}{video_file['filename']}"
                size_text = format_file_size(video_file['size'])
                self.video_tree.insert(
                    parent_id,
                    tk.END,
                    text=child_text,
                    values=(size_text,),
                    tags=("file", video_file['full_path'])
                )

        # Update status
        total_movies = len(results)
        self.video_status_label.config(text=f"Total: {total_movies} movie(s) with duplicates")

    def _video_show_scan_error(self, error_msg: str):
        """Show error message if scan fails."""
        self.video_status_label.config(text="Scan failed")
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_msg}")

    def _video_clear_tree(self):
        """Clear all items from the tree view."""
        for item in self.video_tree.get_children():
            self.video_tree.delete(item)

    def _video_on_tree_click(self, event):
        """
        Handle tree item click to toggle checkboxes.

        Args:
            event: Click event
        """
        item = self.video_tree.identify_row(event.y)
        if not item:
            return

        tags = self.video_tree.item(item, "tags")
        if not tags:
            return

        if tags[0] == "file":
            # Toggle file checkbox
            file_path = tags[1]
            self._video_toggle_file(item, file_path)
        elif tags[0] == "folder":
            # Toggle all files in folder
            self._video_toggle_folder(item)

        # Update delete button state
        self._video_update_delete_button()

    def _video_toggle_file(self, item_id: str, file_path: str):
        """
        Toggle checkbox state for a file.

        Args:
            item_id: Tree item ID
            file_path: Full path to the file
        """
        current_text = self.video_tree.item(item_id, "text")

        if file_path in self.checked_files:
            # Uncheck
            self.checked_files.remove(file_path)
            new_text = current_text.replace("☑", "☐")
        else:
            # Check
            self.checked_files.add(file_path)
            new_text = current_text.replace("☐", "☑")

        self.video_tree.item(item_id, text=new_text)

    def _video_toggle_folder(self, parent_id: str):
        """
        Toggle all files in a folder.

        Args:
            parent_id: Tree item ID of the parent folder
        """
        children = self.video_tree.get_children(parent_id)
        if not children:
            return

        # Determine if we should check or uncheck based on first child
        first_child = children[0]
        first_child_tags = self.video_tree.item(first_child, "tags")
        if first_child_tags and first_child_tags[0] == "file":
            first_file_path = first_child_tags[1]
            should_check = first_file_path not in self.checked_files

            # Toggle all children
            for child in children:
                child_tags = self.video_tree.item(child, "tags")
                if child_tags and child_tags[0] == "file":
                    file_path = child_tags[1]
                    if should_check:
                        self.checked_files.add(file_path)
                        new_text = self.video_tree.item(child, "text").replace("☐", "☑")
                    else:
                        self.checked_files.discard(file_path)
                        new_text = self.video_tree.item(child, "text").replace("☑", "☐")
                    self.video_tree.item(child, text=new_text)

            # Update parent checkbox
            parent_text = self.video_tree.item(parent_id, "text")
            if should_check:
                new_parent_text = parent_text.replace("☐", "☑")
            else:
                new_parent_text = parent_text.replace("☑", "☐")
            self.video_tree.item(parent_id, text=new_parent_text)

    def _video_select_all(self):
        """Select all files in the tree."""
        for parent in self.video_tree.get_children():
            for child in self.video_tree.get_children(parent):
                tags = self.video_tree.item(child, "tags")
                if tags and tags[0] == "file":
                    file_path = tags[1]
                    self.checked_files.add(file_path)
                    new_text = self.video_tree.item(child, "text").replace("☐", "☑")
                    self.video_tree.item(child, text=new_text)

            # Update parent checkbox
            parent_text = self.video_tree.item(parent, "text").replace("☐", "☑")
            self.video_tree.item(parent, text=parent_text)

        self._video_update_delete_button()

    def _video_deselect_all(self):
        """Deselect all files in the tree."""
        self.checked_files.clear()

        for parent in self.video_tree.get_children():
            for child in self.video_tree.get_children(parent):
                current_text = self.video_tree.item(child, "text")
                new_text = current_text.replace("☑", "☐")
                self.video_tree.item(child, text=new_text)

            # Update parent checkbox
            parent_text = self.video_tree.item(parent, "text").replace("☑", "☐")
            self.video_tree.item(parent, text=parent_text)

        self._video_update_delete_button()

    def _video_update_delete_button(self):
        """Enable or disable delete button based on selection."""
        if self.checked_files:
            self.video_delete_button.config(state=tk.NORMAL)
        else:
            self.video_delete_button.config(state=tk.DISABLED)

    def _video_expand_all(self):
        """Expand all movie folders in the tree."""
        for item in self.video_tree.get_children():
            self.video_tree.item(item, open=True)

    def _video_collapse_all(self):
        """Collapse all movie folders in the tree."""
        for item in self.video_tree.get_children():
            self.video_tree.item(item, open=False)

    def _video_delete_selected(self):
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
        self._video_start_scan()

    # ===== Duplicate Folders Tab Methods =====

    def _folder_on_mode_change(self) -> None:
        """Handle matching mode change."""
        if self.matching_mode.get() == "fuzzy":
            self.folder_threshold_scale.config(state=tk.NORMAL)
        else:
            self.folder_threshold_scale.config(state=tk.DISABLED)

    def _folder_update_threshold_label(self, *args):
        """Update threshold percentage label."""
        self.folder_threshold_label.config(text=f"{self.similarity_threshold.get()}%")

    def _folder_on_scope_change(self) -> None:
        """Handle scan scope change."""
        if self.scan_scope.get() == "multiple":
            self.folder_paths_frame.grid()
        else:
            self.folder_paths_frame.grid_remove()

    def _folder_add_path(self) -> None:
        """Add a path to the multiple paths list."""
        folder = filedialog.askdirectory(title="Select Additional Library Folder")
        if folder and folder not in self.additional_paths:
            self.additional_paths.append(folder)
            self.folder_paths_listbox.insert(tk.END, folder)

    def _folder_remove_path(self) -> None:
        """Remove selected path from the multiple paths list."""
        selection = self.folder_paths_listbox.curselection()
        if selection:
            index = selection[0]
            self.folder_paths_listbox.delete(index)
            self.additional_paths.pop(index)

    def _folder_start_scan(self):
        """Start scanning for duplicate folders."""
        # Determine paths to scan
        if self.scan_scope.get() == "single":
            path = self.library_path.get()
            if not path:
                messagebox.showwarning("No Path", "Please select a library folder first.")
                return
            if not Path(path).exists():
                messagebox.showerror("Invalid Path", "The selected path does not exist.")
                return
            scan_paths = [path]
        else:
            # Multiple paths mode
            scan_paths = self.additional_paths.copy()
            # Include main path if it's set
            if self.library_path.get():
                scan_paths.insert(0, self.library_path.get())

            if not scan_paths:
                messagebox.showwarning("No Paths", "Please add at least one library folder.")
                return

        # Clear previous results
        self._folder_clear_tree()
        self.checked_folders.clear()
        self.folder_status_label.config(text="Scanning...")
        self._folder_update_buttons()

        # Run scan in separate thread
        matching_mode = self.matching_mode.get()
        # Convert to 0.0-1.0 and ensure it's within valid range
        threshold = max(0.5, min(1.0, self.similarity_threshold.get() / 100.0))

        scan_thread = threading.Thread(
            target=self._folder_perform_scan,
            args=(scan_paths, matching_mode, threshold),
            daemon=True
        )
        scan_thread.start()

    def _folder_perform_scan(self, paths: List[str], mode: str, threshold: float):
        """Perform the actual folder scanning operation."""
        try:
            if mode == "exact":
                results = find_duplicate_folders_exact(paths)
            else:
                results = find_duplicate_folders_fuzzy(paths, threshold)

            # Get stats for each folder
            metadata = {}
            for group_folders in results.values():
                for folder_path in group_folders:
                    stats = get_folder_stats(folder_path)
                    metadata[folder_path] = stats

            # Update GUI from main thread
            self.root.after(0, self._folder_display_results, results, metadata)
        except Exception as e:
            self.root.after(0, self._folder_show_scan_error, str(e))

    def _folder_display_results(self, results: Dict[str, List[str]], metadata: Dict[str, Dict]):
        """Display folder scan results in the tree view."""
        self.folder_scan_results = results
        self.folder_metadata = metadata
        self._folder_clear_tree()

        if not results:
            self.folder_status_label.config(text="No duplicate folders found")
            return

        # Initialize quality analyzer
        analyzer = QualityAnalyzer(use_metadata=False)

        # Populate tree with results
        total_folders = 0
        for group_id, folder_paths in sorted(results.items()):
            group_size = len(folder_paths)
            total_folders += group_size

            # Find best folder in this group (only if 2+ folders)
            best_folder_path = None
            if len(folder_paths) >= 2:
                best_score = -1
                best_name = None

                for folder_path in folder_paths:
                    stats = metadata.get(folder_path, {})
                    score = analyzer.analyze_folder(folder_path, stats)

                    # Track best score, use alphabetical order for ties
                    folder_name = Path(folder_path).name
                    if score.total_score > best_score:
                        best_score = score.total_score
                        best_folder_path = folder_path
                        best_name = folder_name
                    elif score.total_score == best_score and best_name:
                        # Tie: pick alphabetically first
                        if folder_name < best_name:
                            best_folder_path = folder_path
                            best_name = folder_name

            # Get a representative name for the group
            first_folder = Path(folder_paths[0]).name
            group_name = f"Group: {first_folder} ({group_size} folders)"

            # Insert parent (group)
            parent_id = self.folder_tree.insert(
                "",
                tk.END,
                text=group_name,
                values=("", "", ""),
                tags=("group", group_id)
            )

            # Insert children (folders)
            for folder_path in sorted(folder_paths):
                folder_name = Path(folder_path).name
                stats = metadata.get(folder_path, {})

                video_count = stats.get('video_files', 0)
                total_size = stats.get('total_size', 0)
                size_text = format_file_size(total_size)

                # Add star if this is the best folder
                is_best = (folder_path == best_folder_path)
                star = "⭐ " if is_best else ""

                # Check if folder is tagged, or mark as [BEST]
                if is_best:
                    tag_text = "[BEST]"
                elif folder_path in self.tagged_folders:
                    tag_text = "[TAGGED]"
                else:
                    tag_text = ""

                child_text = f"☐ {star}{folder_name}"
                self.folder_tree.insert(
                    parent_id,
                    tk.END,
                    text=child_text,
                    values=(video_count, size_text, tag_text),
                    tags=("folder", folder_path)
                )

        # Update status
        total_groups = len(results)
        self.folder_status_label.config(
            text=f"Found: {total_folders} folders in {total_groups} group(s)"
        )

    def _folder_show_scan_error(self, error_msg: str):
        """Show error message if scan fails."""
        self.folder_status_label.config(text="Scan failed")
        messagebox.showerror("Scan Error", f"An error occurred during scanning:\n{error_msg}")

    def _folder_clear_tree(self):
        """Clear all items from the folder tree view."""
        for item in self.folder_tree.get_children():
            self.folder_tree.delete(item)

    def _folder_on_tree_click(self, event):
        """Handle tree item click to toggle checkboxes."""
        item = self.folder_tree.identify_row(event.y)
        if not item:
            return

        tags = self.folder_tree.item(item, "tags")
        if not tags:
            return

        if tags[0] == "folder":
            # Toggle folder checkbox
            folder_path = tags[1]
            self._folder_toggle_folder(item, folder_path)
        elif tags[0] == "group":
            # Toggle all folders in group
            self._folder_toggle_group(item)

        # Update button states
        self._folder_update_buttons()

    def _folder_toggle_folder(self, item_id: str, folder_path: str):
        """Toggle checkbox state for a folder."""
        current_text = self.folder_tree.item(item_id, "text")

        if folder_path in self.checked_folders:
            # Uncheck
            self.checked_folders.remove(folder_path)
            new_text = current_text.replace("☑", "☐")
        else:
            # Check
            self.checked_folders.add(folder_path)
            new_text = current_text.replace("☐", "☑")

        self.folder_tree.item(item_id, text=new_text)

    def _folder_toggle_group(self, parent_id: str):
        """Toggle all folders in a group."""
        children = self.folder_tree.get_children(parent_id)
        if not children:
            return

        # Determine if we should check or uncheck based on first child
        first_child = children[0]
        first_child_tags = self.folder_tree.item(first_child, "tags")
        if first_child_tags and first_child_tags[0] == "folder":
            first_folder_path = first_child_tags[1]
            should_check = first_folder_path not in self.checked_folders

            # Toggle all children
            for child in children:
                child_tags = self.folder_tree.item(child, "tags")
                if child_tags and child_tags[0] == "folder":
                    folder_path = child_tags[1]
                    if should_check:
                        self.checked_folders.add(folder_path)
                        new_text = self.folder_tree.item(child, "text").replace("☐", "☑")
                    else:
                        self.checked_folders.discard(folder_path)
                        new_text = self.folder_tree.item(child, "text").replace("☑", "☐")
                    self.folder_tree.item(child, text=new_text)

    def _folder_update_buttons(self):
        """Enable or disable buttons based on selection and tags."""
        # View Contents and Tag Selected buttons require selection
        if self.checked_folders:
            self.folder_view_contents_button.config(state=tk.NORMAL)
            self.folder_tag_button.config(state=tk.NORMAL)
        else:
            self.folder_view_contents_button.config(state=tk.DISABLED)
            self.folder_tag_button.config(state=tk.DISABLED)

        # Clear Tags and Export buttons require tags
        if self.tagged_folders:
            self.folder_clear_tags_button.config(state=tk.NORMAL)
            self.folder_export_button.config(state=tk.NORMAL)
        else:
            self.folder_clear_tags_button.config(state=tk.DISABLED)
            self.folder_export_button.config(state=tk.DISABLED)

    def _folder_expand_all(self):
        """Expand all groups in the tree."""
        for item in self.folder_tree.get_children():
            self.folder_tree.item(item, open=True)

    def _folder_collapse_all(self):
        """Collapse all groups in the tree."""
        for item in self.folder_tree.get_children():
            self.folder_tree.item(item, open=False)

    def _folder_tag_selected(self):
        """Tag selected folders."""
        if not self.checked_folders:
            return

        # Add all checked folders to tagged set
        try:
            for folder_path in self.checked_folders:
                self.tagged_folders = self.tag_manager.add_tag(folder_path, self.tagged_folders)
        except IOError as e:
            messagebox.showerror(
                "Tag Save Error",
                f"Failed to save tags:\n{str(e)}\n\nPlease check file permissions."
            )
            return

        # Update tree display to show tagged status
        for parent in self.folder_tree.get_children():
            for child in self.folder_tree.get_children(parent):
                child_tags = self.folder_tree.item(child, "tags")
                if child_tags and child_tags[0] == "folder":
                    folder_path = child_tags[1]
                    if folder_path in self.tagged_folders:
                        # Update tag column
                        current_values = list(self.folder_tree.item(child, "values"))
                        current_values[2] = "[TAGGED]"
                        self.folder_tree.item(child, values=current_values)

        self._folder_update_buttons()
        messagebox.showinfo("Tagged", f"Tagged {len(self.checked_folders)} folder(s)")

    def _folder_clear_tags(self):
        """Clear all tags."""
        if not self.tagged_folders:
            return

        if not messagebox.askyesno("Clear Tags", "Clear all folder tags?"):
            return

        self.tagged_folders = self.tag_manager.clear_all_tags()

        # Update tree display
        for parent in self.folder_tree.get_children():
            for child in self.folder_tree.get_children(parent):
                current_values = list(self.folder_tree.item(child, "values"))
                current_values[2] = ""
                self.folder_tree.item(child, values=current_values)

        self._folder_update_buttons()
        messagebox.showinfo("Tags Cleared", "All folder tags have been cleared")

    def _folder_view_contents(self):
        """Show folder contents in a dialog."""
        if not self.checked_folders:
            return

        # Show contents of first selected folder
        num_selected = len(self.checked_folders)
        folder_path = list(self.checked_folders)[0]
        folder = Path(folder_path)

        if not folder.exists():
            messagebox.showerror("Error", "Folder does not exist")
            return

        # Create dialog window
        dialog = tk.Toplevel(self.root)
        if num_selected > 1:
            dialog.title(f"Contents: {folder.name} (1 of {num_selected} selected)")
        else:
            dialog.title(f"Contents: {folder.name}")
        dialog.geometry(f"{self.CONTENTS_DIALOG_WIDTH}x{self.CONTENTS_DIALOG_HEIGHT}")

        # Add scrolled text widget
        text_frame = ttk.Frame(dialog, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)

        # Get folder contents
        try:
            files = []
            for item in folder.rglob('*'):
                if item.is_file():
                    relative_path = item.relative_to(folder)
                    size = item.stat().st_size
                    files.append((str(relative_path), format_file_size(size)))

            # Display contents
            if num_selected > 1:
                text_widget.insert('1.0', f"Note: Showing first of {num_selected} selected folders\n\n")
            text_widget.insert(tk.END, f"Folder: {folder_path}\n\n")
            text_widget.insert(tk.END, f"Total files: {len(files)}\n\n")
            text_widget.insert(tk.END, "Files:\n")
            text_widget.insert(tk.END, "-" * 80 + "\n")

            for file_path, size in sorted(files):
                text_widget.insert(tk.END, f"{file_path:60} {size:>15}\n")

        except Exception as e:
            text_widget.insert('1.0', f"Error reading folder contents:\n{str(e)}")

        text_widget.config(state=tk.DISABLED)

        # Add close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)

    def _folder_export_tagged(self):
        """Export tagged folders to a file."""
        if not self.tagged_folders:
            return

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Export Tagged Folders",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w') as f:
                f.write("Tagged Folders\n")
                f.write("=" * 80 + "\n\n")

                for folder_path in sorted(self.tagged_folders):
                    f.write(f"{folder_path}\n")

                    # Include stats if available
                    if folder_path in self.folder_metadata:
                        stats = self.folder_metadata[folder_path]
                        f.write(f"  Videos: {stats.get('video_files', 0)}\n")
                        f.write(f"  Size: {format_file_size(stats.get('total_size', 0))}\n")

                    f.write("\n")

            messagebox.showinfo("Export Complete", f"Exported {len(self.tagged_folders)} tagged folders")

        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Failed to export to {file_path}:\n{str(e)}\n\nPlease check file permissions and disk space."
            )

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()
