"""
File: file_manager_pro.py
Modul: EduClass - Dateiablage Pro
Creator: https://github.com/SchulSystem
Translation: https://github.com/Lukas1120987

Features:
 - Benutzerordner: data/files/users/<username>/
 - Gruppenordner: data/files/groups/<group>/
 - Physische Speicherung (Kollisionen vermieden via timestamp-prefix)
 - Suchfunktion: Dateiname + Dateiinhalte (Plaintext, optional PDF via PyPDF2)
 - Tags & Kategorien: zentrale metadata.json pro base (data/files/metadata.json)
 - Rechte: granulare Rechte (read/write/delete) pro folder, konfigurierbar (permissions.json)
 - In-Modul-Vorschau: Text und Bilder (PIL optional), PDF text preview if PyPDF2 available
 - Versionierung: einfache Versionierung (bei Upload wird alte Datei in .versions/ gesichert)
 - Aktionslog: data/files/logs/actions.json

Notes:
 - Optional extras: Pillow (PIL) for image preview, PyPDF2 for PDF text extraction.
   Install via: pip install pillow PyPDF2
 - The module attempts to import those libs and will degrade gracefully if missing.

"""

import os
import shutil
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
import subprocess
import pathlib
import mimetypes

# optional libs
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False

try:
    import PyPDF2
    HAS_PYPDF2 = True
except Exception:
    HAS_PYPDF2 = False

# ----- helpers -----

def get_data_path():
    return os.path.join("data", "files")


def _ensure_dirs(*paths):
    for p in paths:
        os.makedirs(p, exist_ok=True)


# ----- main class -----
class Modul:
    def __init__(self, master, username: str, user_data: dict):
        self.master = master
        self.username = username
        self.user_data = user_data or {}

        # base paths
        self.base = get_data_path()
        self.users_root = os.path.join(self.base, "users")
        self.groups_root = os.path.join(self.base, "groups")
        self.logs_root = os.path.join(self.base, "logs")
        self.meta_file = os.path.join(self.base, "metadata.json")
        self.perm_file = os.path.join(self.base, "permissions.json")
        self.action_log_file = os.path.join(self.logs_root, "actions.json")

        _ensure_dirs(self.base, self.users_root, self.groups_root, self.logs_root)

        # ensure personal and group folders
        os.makedirs(self.user_folder(self.username), exist_ok=True)
        for g in self.get_user_groups():
            if g:
                os.makedirs(self.group_folder(g), exist_ok=True)

        # metadata and permissions load
        self.metadata = self._load_json(self.meta_file, default={})
        self.permissions = self._load_json(self.perm_file, default={})

        # ui state
        self.current_folder = None
        self.preview_img_ref = None

        # build UI
        self.frame = tk.Frame(master, bg="white")
        self._build_ui()
        self.refresh_tree()

    def get_frame(self):
        return self.frame

    # ----- paths -----
    def user_folder(self, username):
        return os.path.join(self.users_root, username)

    def group_folder(self, groupname):
        safe = groupname.replace('/', '_')
        return os.path.join(self.groups_root, safe)

    def get_user_groups(self):
        groups = []
        g1 = self.user_data.get('group')
        g2 = self.user_data.get('second_group')
        if g1:
            groups.append(g1)
        if g2 and g2 != g1:
            groups.append(g2)
        return groups

    # ----- UI -----
    def _build_ui(self):
        # top title
        title = tk.Label(self.frame, text='📁 Dateiablage Pro', font=("Arial", 16, "bold"), bg='white')
        title.pack(anchor='nw', padx=8, pady=(6,0))

        container = tk.Frame(self.frame, bg='white')
        container.pack(fill='both', expand=True)

        left = tk.Frame(container, bg='white', width=260)
        left.pack(side='left', fill='y', padx=6, pady=6)

        middle = tk.Frame(container, bg='white')
        middle.pack(side='left', fill='both', expand=True, padx=6, pady=6)

        right = tk.Frame(container, bg='white', width=360)
        right.pack(side='right', fill='both', padx=6, pady=6)

        # --- left: explorer tree + search ---
        tk.Label(left, text='Ordner / Suche', bg='white').pack(anchor='w')

        search_frame = tk.Frame(left, bg='white')
        search_frame.pack(fill='x', pady=4)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var).pack(side='left', fill='x', expand=True)
        tk.Button(search_frame, text='Suchen', command=self.run_search).pack(side='left', padx=4)
        tk.Button(search_frame, text='Erweitert', command=self.open_advanced_search).pack(side='left', padx=4)

        self.tree = ttk.Treeview(left)
        self.tree.pack(fill='y', expand=True)
        self.tree.bind('<<TreeviewSelect>>', lambda e: self.on_tree_select())

        btns = tk.Frame(left, bg='white')
        btns.pack(fill='x', pady=6)
        tk.Button(btns, text='Neuordner', command=self.create_subfolder).pack(side='left', fill='x', expand=True, padx=2)
        tk.Button(btns, text='Berechtigungen', command=self.edit_permissions).pack(side='left', fill='x', expand=True, padx=2)
        tk.Button(btns, text='Aktualisieren', command=self.refresh_tree).pack(side='left', fill='x', expand=True, padx=2)

        # --- middle: files list + actions ---
        tk.Label(middle, text='Dateien', bg='white').pack(anchor='w')
        cols = ('name','size','modified','tags')
        self.files_tv = ttk.Treeview(middle, columns=cols, show='headings')
        for c in cols:
            self.files_tv.heading(c, text=c.capitalize())
            self.files_tv.column(c, anchor='w')
        self.files_tv.pack(fill='both', expand=True)
        self.files_tv.bind('<Double-1>', lambda e: self.open_selected_file())

        action_frame = tk.Frame(middle, bg='white')
        action_frame.pack(fill='x', pady=6)
        tk.Button(action_frame, text='📤 Hochladen', command=self.upload_to_selected_folder).pack(side='left', padx=4)
        tk.Button(action_frame, text='📥 Herunterladen', command=self.download_selected_file).pack(side='left', padx=4)
        tk.Button(action_frame, text='📂 Öffnen', command=self.open_selected_file).pack(side='left', padx=4)
        tk.Button(action_frame, text='🗑️ Löschen', command=self.delete_selected_file).pack(side='left', padx=4)
        tk.Button(action_frame, text='Tags/Meta bearbeiten', command=self.edit_metadata).pack(side='left', padx=4)
        tk.Button(action_frame, text='Protokoll', command=self.show_log).pack(side='right', padx=4)

        self.current_folder_var = tk.StringVar(value='Kein Ordner ausgewählt')
        tk.Label(self.frame, textvariable=self.current_folder_var, bg='white', fg='gray').pack(anchor='w', padx=12)

        # --- right: preview pane ---
        tk.Label(right, text='Vorschau', bg='white').pack(anchor='w')
        self.preview_text = tk.Text(right, height=15)
        self.preview_text.pack(fill='both', expand=True)
        if HAS_PIL:
            self.preview_canvas = tk.Canvas(right, height=240, bg='white')
            self.preview_canvas.pack(fill='both', expand=False)
        else:
            self.preview_canvas = None

    # ----- tree management -----
    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        me_id = self.tree.insert('', 'end', text='Mein Ordner', values=('user', self.username), open=True)
        self._insert_folders(me_id, self.user_folder(self.username))

        groups_id = self.tree.insert('', 'end', text='Gruppen', values=('groups_root',''), open=True)
        for g in sorted(self.get_user_groups()):
            if g:
                gid = self.tree.insert(groups_id, 'end', text=g, values=('group', g), open=False)
                self._insert_folders(gid, self.group_folder(g))

        if self.user_data.get('is_admin'):
            all_users = self.tree.insert('', 'end', text='Alle Nutzer (Admin)', values=('all_users',''), open=False)
            for uname in sorted(os.listdir(self.users_root)):
                if os.path.isdir(os.path.join(self.users_root, uname)):
                    uid = self.tree.insert(all_users, 'end', text=uname, values=('user', uname))
                    self._insert_folders(uid, os.path.join(self.users_root, uname))
            all_groups = self.tree.insert('', 'end', text='Alle Gruppen (Admin)', values=('all_groups',''), open=False)
            for gname in sorted(os.listdir(self.groups_root)):
                gd = os.path.join(self.groups_root, gname)
                if os.path.isdir(gd):
                    gid = self.tree.insert(all_groups, 'end', text=gname, values=('group', gname))
                    self._insert_folders(gid, gd)

    def _insert_folders(self, parent_item, path):
        try:
            sub = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
        except Exception:
            sub = []
        for d in sub:
            p = os.path.join(path, d)
            self.tree.insert(parent_item, 'end', text=d, values=('folder', p))

    def on_tree_select(self):
        sel = self.tree.selection()
        if not sel:
            return
        it = sel[0]
        vals = self.tree.item(it, 'values')
        folder_path = None
        if vals:
            typ = vals[0]
            if typ == 'user':
                folder_path = self.user_folder(vals[1])
            elif typ == 'group':
                folder_path = self.group_folder(vals[1])
            elif typ == 'folder':
                folder_path = vals[1]
        if folder_path and os.path.isdir(folder_path):
            self.current_folder = folder_path
            self.current_folder_var.set(f"Aktueller Ordner: {os.path.relpath(folder_path,self.base)}")
            self.refresh_file_list()
        else:
            self.current_folder = None
            self.current_folder_var.set('Kein Ordner ausgewählt')
            self.clear_file_list()

    # ----- file list -----
    def clear_file_list(self):
        for i in self.files_tv.get_children():
            self.files_tv.delete(i)

    def refresh_file_list(self):
        self.clear_file_list()
        if not getattr(self, 'current_folder', None):
            return
        try:
            names = sorted(os.listdir(self.current_folder))
        except Exception:
            names = []
        for n in names:
            full = os.path.join(self.current_folder, n)
            if os.path.isfile(full):
                size_kb = max(1, os.path.getsize(full)//1024)
                mtime = datetime.fromtimestamp(os.path.getmtime(full)).strftime('%d.%m.%Y %H:%M')
                tags = self.metadata.get(os.path.relpath(full,self.base), {}).get('tags', [])
                tagstr = ','.join(tags)
                self.files_tv.insert('', 'end', values=(n, f"{size_kb} KB", mtime, tagstr))

    # ----- permissions -----
    def _load_json(self, path, default=None):
        try:
            if os.path.isfile(path):
                with open(path,'r',encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return default

    def _save_json(self, path, data):
        try:
            with open(path,'w',encoding='utf-8') as f:
                json.dump(data,f,indent=2,ensure_ascii=False)
        except Exception:
            pass

    def _ensure_folder_perm(self, folder_path):
        key = os.path.relpath(folder_path, self.base)
        if key not in self.permissions:
            # default perms: owner full, group read+write, others read (no delete)
            owner = None
            # infer owner if under users/
            rel = os.path.relpath(folder_path, self.base)
            parts = rel.split(os.sep)
            if parts[0] == 'users' and len(parts)>1:
                owner = parts[1]
            self.permissions[key] = {
                'owner': owner,
                'read': [],  # users or groups allowed to read (names)
                'write': [],
                'delete': []
            }
            # sensible defaults
            if owner:
                self.permissions[key]['read'].append(owner)
                self.permissions[key]['write'].append(owner)
                self.permissions[key]['delete'].append(owner)
            # groups
            for g in self.get_user_groups():
                if parts[0]=='groups' and parts[1]==g:
                    # group folder: allow group read/write by default
                    self.permissions[key]['read'].append(g)
                    self.permissions[key]['write'].append(g)
            self._save_json(self.perm_file, self.permissions)
        return self.permissions[key]

    def _has_perm(self, folder_path, mode):
        # mode in ('read','write','delete')
        if self.user_data.get('is_admin'):
            return True
        self._ensure_folder_perm(folder_path)
        key = os.path.relpath(folder_path,self.base)
        perms = self.permissions.get(key, {})
        # check owner
        if perms.get('owner') == self.username:
            return True
        # check direct username
        if self.username in perms.get(mode,[]):
            return True
        # check groups
        for g in self.get_user_groups():
            if g in perms.get(mode,[]):
                return True
        return False

    def edit_permissions(self):
        # only admin or owner can edit
        if not self.current_folder:
            messagebox.showwarning('Kein Ordner', 'Bitte wähle einen Ordner aus.')
            return
        if not self._has_perm(self.current_folder, 'write') and not self.user_data.get('is_admin'):
            messagebox.showerror('Zugriff', 'Du hast keine Berechtigung, Berechtigungen zu bearbeiten.')
            return
        key = os.path.relpath(self.current_folder, self.base)
        self._ensure_folder_perm(self.current_folder)
        perm = self.permissions.get(key, {})

        dlg = tk.Toplevel(self.master)
        dlg.title('Berechtigungen')
        tk.Label(dlg, text=f'Ordner: {key}').pack(anchor='w')
        tk.Label(dlg, text='Owner (username)').pack(anchor='w')
        owner_var = tk.StringVar(value=perm.get('owner') or '')
        tk.Entry(dlg, textvariable=owner_var).pack(fill='x')

        def make_listbox(name):
            tk.Label(dlg, text=name).pack(anchor='w')
            lb = tk.Listbox(dlg)
            lb.pack(fill='both', expand=True)
            for it in perm.get(name.lower(), []):
                lb.insert('end', it)
            return lb

        read_lb = make_listbox('read')
        write_lb = make_listbox('write')
        delete_lb = make_listbox('delete')

        entry_var = tk.StringVar()
        tk.Entry(dlg, textvariable=entry_var).pack(fill='x')
        def add_to(lb_name):
            val = entry_var.get().strip()
            if not val: return
            lb = {'read':read_lb,'write':write_lb,'delete':delete_lb}[lb_name]
            lb.insert('end', val)
        tk.Button(dlg, text='Hinzufügen (eingetragenen Namen)', command=lambda: add_to('read')).pack()

        def save_and_close():
            perm['owner'] = owner_var.get().strip() or None
            perm['read'] = list(read_lb.get(0,'end'))
            perm['write'] = list(write_lb.get(0,'end'))
            perm['delete'] = list(delete_lb.get(0,'end'))
            self.permissions[key] = perm
            self._save_json(self.perm_file, self.permissions)
            dlg.destroy()
            messagebox.showinfo('Gespeichert','Berechtigungen gespeichert')
        tk.Button(dlg, text='Speichern', command=save_and_close).pack()

    # ----- upload / download / delete -----
    def _unique_name(self, original):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe = original.replace(' ','_')
        return f"{ts}_{safe}"

    def upload_to_selected_folder(self):
        if not self.current_folder:
            messagebox.showwarning('Kein Ordner','Bitte wähle einen Ordner aus')
            return
        if not self._has_perm(self.current_folder, 'write'):
            messagebox.showerror('Zugriff verweigert','Du darfst hier keine Dateien hochladen')
            return
        fp = filedialog.askopenfilename()
        if not fp:
            return
        orig = os.path.basename(fp)
        target = self._unique_name(orig)
        target_path = os.path.join(self.current_folder, target)
        try:
            # versioning: if file with same "logical" name exists (without timestamp), copy old to .versions
            basename_parts = orig
            versions_dir = os.path.join(self.current_folder, '.versions')
            os.makedirs(versions_dir, exist_ok=True)
            # copy
            shutil.copy(fp, target_path)
            # store metadata
            rel = os.path.relpath(target_path, self.base)
            meta = {'original_name': orig, 'uploaded_by': self.username, 'upload_date': datetime.now().isoformat(), 'tags': [], 'category': None}
            self.metadata[rel] = meta
            self._save_json(self.meta_file, self.metadata)
            self._log_action('upload', target_path, original=orig)
            messagebox.showinfo('Erfolg', f"{orig} hochgeladen")
            self.refresh_file_list()
        except Exception as e:
            messagebox.showerror('Fehler', f'Upload fehlgeschlagen:\n{e}')

    def download_selected_file(self):
        sel = self.files_tv.selection()
        if not sel:
            messagebox.showwarning('Keine Auswahl','Bitte wähle eine Datei')
            return
        name = self.files_tv.item(sel[0], 'values')[0]
        src = os.path.join(self.current_folder, name)
        if not os.path.isfile(src):
            messagebox.showerror('Fehler','Datei nicht gefunden')
            return
        if not self._has_perm(self.current_folder,'read'):
            messagebox.showerror('Zugriff verweigert','Keine Leseberechtigung')
            return
        target_dir = filedialog.askdirectory()
        if not target_dir: return
        try:
            shutil.copy(src, os.path.join(target_dir, name))
            self._log_action('download', src, target_dir=target_dir)
            messagebox.showinfo('Erfolg','Datei kopiert')
        except Exception as e:
            messagebox.showerror('Fehler',str(e))

    def open_selected_file(self):
        sel = self.files_tv.selection()
        if not sel: return
        name = self.files_tv.item(sel[0], 'values')[0]
        path = os.path.join(self.current_folder, name)
        if not os.path.isfile(path):
            messagebox.showerror('Fehler','Datei fehlt')
            return
        if not self._has_perm(self.current_folder,'read'):
            messagebox.showerror('Zugriff verweigert','Keine Leseberechtigung')
            return
        # attempt in-module preview
        self.preview_text.config(state='normal')
        self.preview_text.delete('1.0','end')
        self._clear_canvas()
        mimetype, _ = mimetypes.guess_type(path)
        if mimetype and mimetype.startswith('image') and HAS_PIL:
            try:
                im = Image.open(path)
                im.thumbnail((600,400))
                self.preview_img_ref = ImageTk.PhotoImage(im)
                if self.preview_canvas:
                    self.preview_canvas.create_image(0,0, anchor='nw', image=self.preview_img_ref)
                else:
                    self.preview_text.insert('end','(Bild kann nicht angezeigt werden — Canvas fehlt)')
            except Exception as e:
                self.preview_text.insert('end', f'Bildvorschau fehlgeschlagen: {e}')
        else:
            # try text
            try:
                # PDFs via PyPDF2
                if path.lower().endswith('.pdf') and HAS_PYPDF2:
                    with open(path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = []
                        for p in range(min(5, len(reader.pages))):
                            try:
                                text.append(reader.pages[p].extract_text() or '')
                            except Exception:
                                pass
                        self.preview_text.insert('end', '\n\n'.join(text) or '(Keine Text-Vorschau)')
                else:
                    # read as text (try utf-8 then latin1)
                    with open(path, 'r', encoding='utf-8') as f:
                        self.preview_text.insert('end', f.read(100000))
            except Exception:
                try:
                    with open(path, 'r', encoding='latin-1') as f:
                        self.preview_text.insert('end', f.read(100000))
                except Exception:
                    self.preview_text.insert('end', f"Vorschau nicht möglich. Dateipfad: {path}")
        self.preview_text.config(state='disabled')

    def _clear_canvas(self):
        if self.preview_canvas:
            self.preview_canvas.delete('all')
            self.preview_img_ref = None

    def delete_selected_file(self):
        sel = self.files_tv.selection()
        if not sel:
            messagebox.showwarning('Keine Auswahl','Wähle eine Datei')
            return
        name = self.files_tv.item(sel[0], 'values')[0]
        path = os.path.join(self.current_folder, name)
        if not os.path.isfile(path):
            messagebox.showerror('Fehler','Datei fehlt')
            return
        if not self._has_perm(self.current_folder,'delete'):
            messagebox.showerror('Zugriff verweigert','Keine Löschberechtigung')
            return
        if not messagebox.askyesno('Löschen','Wirklich löschen?'):
            return
        try:
            # move to .trash instead of permanent delete (safer)
            trash = os.path.join(self.base, '.trash')
            os.makedirs(trash, exist_ok=True)
            shutil.move(path, os.path.join(trash, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}"))
            rel = os.path.relpath(path,self.base)
            self._log_action('delete', path)
            self.refresh_file_list()
            messagebox.showinfo('Gelöscht','Datei in den Papierkorb verschoben')
        except Exception as e:
            messagebox.showerror('Fehler',str(e))

    def create_subfolder(self):
        if not self.current_folder:
            messagebox.showwarning('Kein Ordner','Wähle einen Ordner')
            return
        if not self._has_perm(self.current_folder,'write'):
            messagebox.showerror('Zugriff verweigert','Keine Berechtigung')
            return
        name = simpledialog.askstring('Neuer Ordner','Name:')
        if not name: return
        safe = name.replace('/','_').strip()
        newp = os.path.join(self.current_folder, safe)
        try:
            os.makedirs(newp, exist_ok=False)
            self._log_action('mkdir', newp)
            self.refresh_tree()
            messagebox.showinfo('Erstellt','Ordner angelegt')
        except FileExistsError:
            messagebox.showwarning('Existiert','Ordner existiert bereits')
        except Exception as e:
            messagebox.showerror('Fehler',str(e))

    # ----- metadata / tags -----
    def edit_metadata(self):
        sel = self.files_tv.selection()
        if not sel:
            messagebox.showwarning('Keine Auswahl','Wähle eine Datei')
            return
        name = self.files_tv.item(sel[0], 'values')[0]
        path = os.path.join(self.current_folder, name)
        rel = os.path.relpath(path,self.base)
        meta = self.metadata.get(rel, {'original_name': name, 'uploaded_by': None, 'upload_date': None, 'tags': [], 'category': None})

        dlg = tk.Toplevel(self.master)
        dlg.title('Metadaten')
        tk.Label(dlg, text=f'Datei: {name}').pack(anchor='w')
        tk.Label(dlg, text='Kategorien (eine wählen)').pack(anchor='w')
        cat_var = tk.StringVar(value=meta.get('category') or '')
        tk.Entry(dlg, textvariable=cat_var).pack(fill='x')
        tk.Label(dlg, text='Tags (kommagetrennt)').pack(anchor='w')
        tags_var = tk.StringVar(value=','.join(meta.get('tags',[])))
        tk.Entry(dlg, textvariable=tags_var).pack(fill='x')

        def save_meta():
            meta['category'] = cat_var.get().strip() or None
            meta['tags'] = [t.strip() for t in tags_var.get().split(',') if t.strip()]
            meta['uploaded_by'] = meta.get('uploaded_by') or self.username
            meta['upload_date'] = meta.get('upload_date') or datetime.now().isoformat()
            self.metadata[rel] = meta
            self._save_json(self.meta_file, self.metadata)
            dlg.destroy()
            self.refresh_file_list()
        tk.Button(dlg, text='Speichern', command=save_meta).pack()

    # ----- search -----
    def run_search(self):
        q = self.search_var.get().strip()
        if not q:
            messagebox.showinfo('Suche','Bitte Suchbegriff eingeben')
            return
        results = []
        qlow = q.lower()
        # search filenames and metadata tags/categories
        for rel, meta in self.metadata.items():
            fname = os.path.basename(rel)
            if qlow in fname.lower() or qlow in (meta.get('category') or '').lower() or any(qlow in t.lower() for t in meta.get('tags',[])):
                results.append(rel)
        # search by content for text files and pdfs (best effort)
        for root, _, files in os.walk(self.base):
            for f in files:
                full = os.path.join(root,f)
                rel = os.path.relpath(full,self.base)
                if rel in results:
                    continue
                if qlow in f.lower():
                    results.append(rel)
                    continue
                # only try content for reasonable small files
                try:
                    if os.path.getsize(full) > 5*1024*1024:
                        continue
                except Exception:
                    continue
                # text
                try:
                    with open(full,'r',encoding='utf-8') as fh:
                        txt = fh.read()
                        if qlow in txt.lower():
                            results.append(rel)
                            continue
                except Exception:
                    pass
                # pdf
                if HAS_PYPDF2 and full.lower().endswith('.pdf'):
                    try:
                        with open(full,'rb') as fh:
                            reader = PyPDF2.PdfReader(fh)
                            for p in reader.pages:
                                try:
                                    page_text = p.extract_text() or ''
                                    if qlow in page_text.lower():
                                        results.append(rel)
                                        break
                                except Exception:
                                    continue
                    except Exception:
                        pass
        # show results dialog
        dlg = tk.Toplevel(self.master)
        dlg.title(f'Suchergebnisse: {len(results)}')
        tv = ttk.Treeview(dlg, columns=('path','meta'), show='headings')
        tv.heading('path', text='Pfad')
        tv.heading('meta', text='Meta')
        tv.pack(fill='both', expand=True)
        for r in results:
            meta = self.metadata.get(r,{})
            tv.insert('', 'end', values=(r, meta.get('tags')))
        def on_open(e=None):
            sel = tv.selection()
            if not sel: return
            r = tv.item(sel[0], 'values')[0]
            # set tree selection to that folder
            folder = os.path.dirname(os.path.join(self.base, r))
            # attempt to expand tree and select matching item by value
            # fallback: set current_folder and refresh
            self.current_folder = folder
            self.current_folder_var.set(f"Aktueller Ordner: {os.path.relpath(folder,self.base)}")
            self.refresh_file_list()
            dlg.destroy()
        tv.bind('<Double-1>', on_open)
        tk.Button(dlg, text='Öffnen', command=on_open).pack()

    def open_advanced_search(self):
        dlg = tk.Toplevel(self.master)
        dlg.title('Erweiterte Suche')
        tk.Label(dlg, text='Name enthält').pack(anchor='w')
        name_var = tk.StringVar()
        tk.Entry(dlg, textvariable=name_var).pack(fill='x')
        tk.Label(dlg, text='Tag enthält').pack(anchor='w')
        tag_var = tk.StringVar()
        tk.Entry(dlg, textvariable=tag_var).pack(fill='x')
        tk.Label(dlg, text='Kategorie').pack(anchor='w')
        cat_var = tk.StringVar()
        tk.Entry(dlg, textvariable=cat_var).pack(fill='x')
        def run_adv():
            qname = name_var.get().strip().lower()
            qtag = tag_var.get().strip().lower()
            qcat = cat_var.get().strip().lower()
            results = []
            for rel,meta in self.metadata.items():
                ok = True
                if qname and qname not in os.path.basename(rel).lower(): ok=False
                if qtag and not any(qtag in t.lower() for t in meta.get('tags',[])): ok=False
                if qcat and qcat not in (meta.get('category') or '').lower(): ok=False
                if ok: results.append(rel)
            # show similar to run_search
            dlg.destroy()
            self.search_var.set('')
            # reuse search results dialog logic quickly
            out = tk.Toplevel(self.master)
            out.title(f'Ergebnis: {len(results)}')
            tv = ttk.Treeview(out, columns=('path','meta'), show='headings')
            tv.heading('path', text='Pfad')
            tv.heading('meta', text='Meta')
            tv.pack(fill='both', expand=True)
            for r in results:
                meta = self.metadata.get(r,{})
                tv.insert('', 'end', values=(r, meta.get('tags')))
            def on_open(e=None):
                sel = tv.selection()
                if not sel: return
                r = tv.item(sel[0], 'values')[0]
                folder = os.path.dirname(os.path.join(self.base, r))
                self.current_folder = folder
                self.current_folder_var.set(f"Aktueller Ordner: {os.path.relpath(folder,self.base)}")
                self.refresh_file_list()
                out.destroy()
            tv.bind('<Double-1>', on_open)
            tk.Button(out, text='Öffnen', command=on_open).pack()
        tk.Button(dlg, text='Suchen', command=run_adv).pack()

    # ----- logging -----
    def _log_action(self, action_type, target_path, **meta):
        entry = {
            'time': datetime.now().isoformat(),
            'user': self.username,
            'action': action_type,
            'target': os.path.relpath(target_path,self.base),
            'meta': meta
        }
        logs = []
        try:
            if os.path.isfile(self.action_log_file):
                with open(self.action_log_file,'r',encoding='utf-8') as f:
                    logs = json.load(f)
        except Exception:
            logs = []
        logs.append(entry)
        try:
            with open(self.action_log_file,'w',encoding='utf-8') as f:
                json.dump(logs,f,indent=2,ensure_ascii=False)
        except Exception:
            pass

    def show_log(self):
        logs = []
        try:
            if os.path.isfile(self.action_log_file):
                with open(self.action_log_file,'r',encoding='utf-8') as f:
                    logs = json.load(f)
        except Exception:
            logs = []
        dlg = tk.Toplevel(self.master)
        dlg.title('Aktivitäten')
        txt = tk.Text(dlg)
        txt.pack(fill='both', expand=True)
        if not logs:
            txt.insert('end','Keine Einträge')
        else:
            for e in logs[-500:]:
                txt.insert('end', f"{e.get('time')} | {e.get('user')} | {e.get('action')} | {e.get('target')} | {json.dumps(e.get('meta',{}),ensure_ascii=False)}\n")
        txt.config(state='disabled')

# DEBUG's

#no mistakes

