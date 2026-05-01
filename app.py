import os
import re
import customtkinter as ctk
from tkinter import filedialog, messagebox

class FolderStructureCreator:
    """
    Handles folder path parsing and folder creation.
    This class is independent from the UI.
    """

    def __init__(self, root_directory: str):
        self.root_directory = root_directory

    def parse_paths(self, raw_text: str) -> list[str]:
        """
        Convert multiline text into a clean list of folder paths.
        Empty lines are ignored.
        """
        return [
            line.strip()
            for line in raw_text.splitlines()
            if line.strip()
        ]

    def normalize_relative_path(self, folder_path: str) -> str:
        """
        Makes folder paths OS-independent.

        Example:
        Project/Assets/Textures
        Project\\Assets\\Textures

        Both will work on Windows, macOS, and Linux.
        """
        parts = [
            part.strip()
            for part in re.split(r"[\\/]+", folder_path)
            if part.strip()
        ]

        if not parts:
            raise ValueError("Empty folder path found.")

        if any(part == ".." for part in parts):
            raise ValueError(f"Invalid path '{folder_path}': '..' is not allowed.")

        return os.path.join(*parts)

    def create_folders(self, folder_paths: list[str]) -> tuple[list[str], list[str]]:
        """
        Creates folders recursively.

        Returns:
        - created_or_existing: folders processed successfully
        - errors: failed folder paths with reason
        """
        created_or_existing = []
        errors = []

        for folder_path in folder_paths:
            try:
                relative_path = self.normalize_relative_path(folder_path)
                final_path = os.path.join(self.root_directory, relative_path)

                # Required recursive folder creation method
                os.makedirs(final_path, exist_ok=True)

                created_or_existing.append(final_path)

            except Exception as error:
                errors.append(f"{folder_path} -> {error}")

        return created_or_existing, errors

class FolderCreatorApp(ctk.CTk):
    """
    Main CustomTkinter desktop application.
    """

    def __init__(self):
        super().__init__()

        self.title("Multi Folder Creation Tool")
        self.geometry("850x650")
        self.minsize(750, 550)

        self.selected_directory = ""

        self.configure_theme()
        self.create_widgets()

    def configure_theme(self):
        """
        Configure modern dark theme.
        """
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def create_widgets(self):
        """
        Build the UI layout.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=3)  # Path textbox row should expand
        self.grid_rowconfigure(6, weight=1)  # Status log row should expand

        title_label = ctk.CTkLabel(
            self,
            text="Multi Folder Creation Tool",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        directory_frame = ctk.CTkFrame(self)
        directory_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        directory_frame.grid_columnconfigure(0, weight=1)

        self.directory_entry = ctk.CTkEntry(
            directory_frame,
            placeholder_text="Select target root directory..."
        )
        self.directory_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        browse_button = ctk.CTkButton(
            directory_frame,
            text="Browse",
            width=120,
            command=self.browse_directory
        )
        browse_button.grid(row=0, column=1, padx=10, pady=10)

        input_label = ctk.CTkLabel(
            self,
            text="Enter folder paths, one per line:",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        input_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="sw")

        self.path_textbox = ctk.CTkTextbox(self, height=220)
        self.path_textbox.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.path_textbox.insert(
            "1.0",
            "Project/Assets/Textures\n"
            "Project/Assets/Models\n"
            "Project/Docs/Reports\n"
        )

        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        upload_button = ctk.CTkButton(
            button_frame,
            text="Upload .txt File",
            command=self.upload_txt_file
        )
        upload_button.pack(side="left", padx=10, pady=10)

        clear_button = ctk.CTkButton(
            button_frame,
            text="Clear Input",
            fg_color="#555555",
            hover_color="#666666",
            command=self.clear_input
        )
        clear_button.pack(side="left", padx=10, pady=10)

        generate_button = ctk.CTkButton(
            button_frame,
            text="Generate Folders",
            fg_color="#1f8f4d",
            hover_color="#176b3a",
            command=self.generate_folders
        )
        generate_button.pack(side="right", padx=10, pady=10)

        log_label = ctk.CTkLabel(
            self,
            text="Status Log:",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        log_label.grid(row=5, column=0, padx=20, pady=(10, 5), sticky="sw")

        self.status_log = ctk.CTkTextbox(self, height=150)
        self.status_log.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.status_log.configure(state="disabled")

    def browse_directory(self):
        """
        Opens directory selection dialog.
        """
        directory = filedialog.askdirectory(title="Select Target Directory")

        if directory:
            self.selected_directory = directory
            self.directory_entry.delete(0, "end")
            self.directory_entry.insert(0, directory)
            self.write_log(f"Selected directory: {directory}")

    def upload_txt_file(self):
        """
        Upload a .txt file containing folder paths, one per line.
        """
        file_path = filedialog.askopenfilename(
            title="Select Folder Path Text File",
            filetypes=[("Text Files", "*.txt")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()

            self.path_textbox.delete("1.0", "end")
            self.path_textbox.insert("1.0", content)

            self.write_log(f"Loaded folder paths from: { file_path }")

        except Exception as error:
            messagebox.showerror("File Error", f"Unable to read file:\n{error}")
            self.write_log(f"Error reading file: {error}")

    def generate_folders(self):
        """
        Create folders from textbox input.
        """
        root_directory = self.directory_entry.get().strip()
        raw_text = self.path_textbox.get("1.0", "end").strip()

        if not root_directory:
            messagebox.showwarning("Missing Directory", "Please select a target directory.")
            return

        if not raw_text:
            messagebox.showwarning("Missing Paths", "Please enter or upload folder paths.")
            return

        creator = FolderStructureCreator(root_directory)
        folder_paths = creator.parse_paths(raw_text)

        created_or_existing, errors = creator.create_folders(folder_paths)

        self.write_log("-" * 60)
        self.write_log(f"Total input paths: {len(folder_paths)}")
        self.write_log(f"Successfully created or already existing: {len(created_or_existing)}")

        for path in created_or_existing:
            self.write_log(f"OK: {path}")

        if errors:
            self.write_log(f"Errors: {len(errors)}")
            for error in errors:
                self.write_log(f"ERROR: {error}")

        messagebox.showinfo(
            "Completed",
            f"Folder generation completed.\n\n"
            f"Successful: {len(created_or_existing)}\n"
            f"Errors: {len(errors)}"
        )

    def clear_input(self):
        """
        Clear manual input textbox.
        """
        self.path_textbox.delete("1.0", "end")
        self.write_log("Input cleared.")

    def write_log(self, message: str):
        """
        Write messages to the status log.
        """
        self.status_log.configure(state="normal")
        self.status_log.insert("end", message + "\n")
        self.status_log.see("end")
        self.status_log.configure(state="disabled")

if __name__ == "__main__":
    app = FolderCreatorApp()
    app.mainloop()