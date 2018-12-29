"""Backup Pusher GUI
This is a GUI for the BackupPusher main python script.
See docstring in main.py.
Copyright 2018, Alonzo Castanon
TODOS:
1. Add support for excluding specific file extensions
2. Add ScrollBar
3. Instead of copying everything at once, use something to check for differences"""

# Module Imports
import os
from os.path import expanduser
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory
# Code Imports
import backupPusher as bp

class BackupPusher(tk.Frame):
    """Main class for BackupPusher GUI"""
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        # Variables
        self.home_directory = expanduser("~")
        self.parent_name = self.home_directory
        self.path_to_iid = dict()
        self.iid_count = 0
        self.family_tree = dict()
        self.all_directories = []
        # Define Widgets
        self.heading = ttk.Label(self.parent, text="Backup Pusher v1.0")
        self.select_parent_button = ttk.Button(self.parent, text="Select Directory to Copy",
                                               command=self.select_parent)
        label_text = "   Select Directories to EXCLUDE\n(Select Root folder to include ALL)"
        self.excludes_label = ttk.Label(self.parent, text=label_text, anchor="center")
        self.excludes_tree = ttk.Treeview(self.parent)
        self.excludes_tree["columns"] = ("size", "children")
        self.excludes_tree.column("size", width=100, anchor="w")
        self.excludes_tree.heading("size", text="Size (MB)")
        self.excludes_tree.column("children", width=75, anchor="w")
        self.excludes_tree.heading("children", text="Children")
        self.copy_button = ttk.Button(self.parent, text="Copy!", command=self.copy, state="disabled")
        # Position Widgets
        self.heading.grid(column=0, row=0)
        self.select_parent_button.grid(column=0, row=1, pady=15)
        self.excludes_label.grid(column=0, row=2, pady=(0, 10))
        self.excludes_tree.grid(column=0, row=3, padx=15)
        self.copy_button.grid(column=0, row=4, pady=15)

    def select_parent(self):
        """Triggers askdirectory dialog box to appear, setting the
        parent_name directory to the selected directory path"""
        self.parent_name = askdirectory(initialdir=self.home_directory,
                                        title="Select Target Folder", mustexist=True)
        self.parent_name = self.parent_name.replace("/", "\\")
        self.populate_excludes_window()

    def populate_excludes_window(self):
        """Populates the excludes widget, triggered after user provides a
        target parent folder"""
        self.excludes_tree.insert("", 0, iid="0", text=self.get_basename(self.parent_name),
                                  values=self.get_values(self.parent_name))
        self.path_to_iid[self.parent_name] = self.iid_count
        self.family_tree[str(self.iid_count)] = []
        self.iid_count += 1
        self.all_directories.append(self.parent_name)
        for dirpath, dirnames, filenames in os.walk(os.fsencode(self.parent_name)):
            dirpath = os.fsdecode(dirpath)
            if dirpath != self.parent_name:
                self.excludes_tree.insert(self.child_to_parent_iid(dirpath), index=10000,
                                          iid=str(self.iid_count),
                                          text=self.get_basename(dirpath),
                                          values=self.get_values(dirpath))
                self.path_to_iid[dirpath] = self.iid_count
                self.family_tree[self.child_to_parent_iid(dirpath)].append(str(self.iid_count))
                self.family_tree[str(self.iid_count)] = []
                self.iid_count += 1
                self.all_directories.append(dirpath)
        self.copy_button["state"] = "normal"

    def get_basename(self, path):
        """Returns the base file name (after last '\\') of a path"""
        temp = path.split("\\")
        if temp[-1] == "":
            return temp[-2]
        else:
            return temp[-1]

    def get_values(self, path):
        """Given a path to a directory, return the total size of all children,
        and the total count of children"""
        path = os.fsencode(path)
        total_size = 0
        item_count = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                item_count += 1
                total_size += os.path.getsize(fp)
        return [int(total_size/(10**6)), item_count]

    def child_to_parent_iid(self, dirpath):
        dirpath = dirpath.split("\\")
        dirpath = "\\".join(dirpath[:-1])
        return str(self.path_to_iid[dirpath])

    def dive(self, target):
        result = set()
        family = self.family_tree[target]
        result = result.union(set(family))
        for child in family:
            result = result.union(set(self.dive(child)))
        return result

    def dive_family_tree(self, to_exclude):
        to_include = set(self.all_directories)
        iid_to_path = {value:key for key, value in self.path_to_iid.items()}
        temp = set()
        for iid in to_exclude:
            temp = temp.union(self.dive(iid))
        subtract = []
        for iid in temp:
            subtract.append(iid_to_path[int(iid)])
        for iid in to_exclude:
            subtract.append(iid_to_path[int(iid)])
        subtract = set(subtract)
        return (to_include - subtract)

    def copy(self):
        to_exclude = self.excludes_tree.selection()
        if (len(to_exclude) == 1) and (to_exclude[0] == "0"):
            to_exclude = tuple()
        to_include = self.dive_family_tree(to_exclude)
        bp.write_config("C:\\Users\\Alonzo\\Drive\\Laptop\\", list(to_include))
        bp.main()
        self.copy_button["state"] = "disabled"
        self.copy_button["text"] = "Done!"

if __name__ == "__main__":
    ROOT = tk.Tk()
    ROOT.title("Backup Pusher")
    BackupPusher(ROOT).grid()
    ROOT.mainloop()
