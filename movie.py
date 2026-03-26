import sys, os, subprocess, json, shutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidget, QListWidgetItem, QPushButton, QFileDialog, QLabel, 
                             QLineEdit, QSpinBox, QSplitter, QTextEdit, QFontDialog, QGroupBox, 
                             QComboBox, QCheckBox, QColorDialog, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QPixmap, QFont, QColor, QIcon

class MovieCollageMaker(QMainWindow):
    def __init__(self, start_file=None):
        super().__init__()
        self.version = "v0.1"
        self.current_project_name = "Untitled"
        self._is_dirty = False
        self.video_path = ""
        self.fps = 23.976
        self.current_frame = 0
        self.base_frame = 0
        self.font_family = "Arial"
        self.font_size = 45
        self.border_color = "#FF00FF"
        self.video_width = 1280
        self.temp_dir = "mcm_temp"
        
        if not os.path.exists(self.temp_dir): 
            os.makedirs(self.temp_dir)

        self.update_window_title()
        self.init_ui()
        
        if start_file:
            QTimer.singleShot(100, lambda: self.load_file(start_file, force_no_prompt=True))

    @property
    def is_dirty(self):
        return self._is_dirty

    @is_dirty.setter
    def is_dirty(self, value):
        self._is_dirty = value
        self.update_window_title()

    def update_window_title(self):
        dirty_indicator = "*" if self._is_dirty else ""
        self.setWindowTitle(f"{self.current_project_name}{dirty_indicator} - Movie Collage Maker {self.version}")

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        splitter = QSplitter(Qt.Horizontal)

        col1 = QWidget()
        l_col1 = QVBoxLayout(col1)
        self.group1 = QGroupBox("1. Project management")
        v1 = QVBoxLayout(self.group1)
        
        btn_import = QPushButton("Import movie..."); btn_import.clicked.connect(self.import_movie_dialog)
        v1.addWidget(btn_import)

        v1.addWidget(QLabel("Project:"))
        project_row = QHBoxLayout()
        btn_new = QPushButton("New"); btn_new.clicked.connect(self.new_project_action)
        btn_open = QPushButton("Open..."); btn_open.clicked.connect(self.open_project_dialog)
        btn_save = QPushButton("Save..."); btn_save.clicked.connect(self.save_project_action)
        project_row.addWidget(btn_new); project_row.addWidget(btn_open); project_row.addWidget(btn_save)
        v1.addLayout(project_row)

        btn_about = QPushButton("About..."); btn_about.clicked.connect(self.show_about)
        v1.addWidget(btn_about)
        
        l_col1.addWidget(self.group1)

        self.group2 = QGroupBox("2. Subtitle list")
        v2 = QVBoxLayout(self.group2)
        self.search_bar = QLineEdit(); self.search_bar.setPlaceholderText("Filter subtitles...")
        self.search_bar.textChanged.connect(self.filter_list)
        self.src_list = QListWidget()
        self.src_list.itemClicked.connect(self.on_text_selected)
        self.src_list.itemDoubleClicked.connect(self.add_to_project)
        v2.addWidget(self.search_bar); v2.addWidget(self.src_list)
        l_col1.addWidget(self.group2)

        col2 = QWidget()
        l_col2 = QVBoxLayout(col2)
        self.group3 = QGroupBox("3. Current frame editor")
        v3 = QVBoxLayout(self.group3)
        self.preview_label = QLabel("No video loaded"); self.preview_label.setMinimumSize(720, 405)
        self.preview_label.setStyleSheet("background: black;"); self.preview_label.setAlignment(Qt.AlignCenter)
        v3.addWidget(self.preview_label)

        nav_box = QHBoxLayout()
        for v in [-10, -5, -1, 1, 5, 10]:
            b = QPushButton(f"{'+' if v>0 else ''}{v}")
            b.clicked.connect(lambda ch=False, val=v: self.adjust_frame(val)); nav_box.addWidget(b)
        v3.addLayout(nav_box)

        self.offset_label = QLabel("Frame offset: +0")
        v3.addWidget(self.offset_label, alignment=Qt.AlignCenter)
        self.text_editor = QTextEdit(); self.text_editor.setMaximumHeight(70)
        self.text_editor.textChanged.connect(self.on_ui_content_changed)
        v3.addWidget(self.text_editor)
        self.btn_add = QPushButton("Add to project ↓"); self.btn_add.setMinimumHeight(50)
        self.btn_add.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        self.btn_add.clicked.connect(self.add_to_project); v3.addWidget(self.btn_add)
        l_col2.addWidget(self.group3)

        bottom_row = QHBoxLayout()
        self.group4 = QGroupBox("4. Project clips")
        v4 = QVBoxLayout(self.group4); self.dst_list = QListWidget()
        v4.addWidget(self.dst_list)
        
        list_ops = QHBoxLayout()
        btn_rem = QPushButton("Remove selected")
        btn_rem.clicked.connect(self.remove_item)
        btn_sort = QPushButton("Sort")
        btn_sort.setFixedWidth(80)
        btn_sort.clicked.connect(self.sort_items)
        list_ops.addWidget(btn_rem); list_ops.addWidget(btn_sort)
        v4.addLayout(list_ops)
        bottom_row.addWidget(self.group4, 2)

        self.group5 = QGroupBox("5. Project options")
        v5 = QVBoxLayout(self.group5)
        
        layout_row = QHBoxLayout()
        self.combo_dir = QComboBox(); self.combo_dir.addItems(["Horizontal (cols)", "Vertical (rows)"])
        self.combo_dir.currentIndexChanged.connect(self.set_dirty)
        self.spin_tile = QSpinBox(); self.spin_tile.setValue(2); self.spin_tile.setRange(1, 20)
        self.spin_tile.valueChanged.connect(self.set_dirty)
        layout_row.addWidget(QLabel("Layout:")); layout_row.addWidget(self.combo_dir)
        layout_row.addWidget(QLabel("Count:")); layout_row.addWidget(self.spin_tile)
        v5.addLayout(layout_row)

        v5.addWidget(QLabel("Extra ImageMagick parameters:"))
        self.extra_params = QLineEdit(); self.extra_params.setPlaceholderText("-quality 90 -resize 70%...")
        self.extra_params.textChanged.connect(self.set_dirty)
        v5.addWidget(self.extra_params)

        btn_font = QPushButton("Font settings..."); btn_font.clicked.connect(self.choose_font); v5.addWidget(btn_font)

        b_layout = QHBoxLayout()
        self.check_border = QCheckBox("Border"); self.spin_border = QSpinBox(); self.spin_border.setValue(2)
        self.check_border.toggled.connect(self.set_dirty); self.spin_border.valueChanged.connect(self.set_dirty)
        self.btn_b_color = QPushButton("Color..."); self.btn_b_color.clicked.connect(self.choose_border_color)
        b_layout.addWidget(self.check_border); b_layout.addWidget(self.spin_border); b_layout.addWidget(self.btn_b_color)
        v5.addLayout(b_layout); v5.addStretch()

        gen_container = QHBoxLayout()
        self.btn_gen = QPushButton("GENERATE FILE...")
        self.btn_gen.setFixedWidth(360); self.btn_gen.setMinimumHeight(70)
        self.btn_gen.setStyleSheet("background-color: #c62828; color: white; font-weight: bold;")
        self.btn_gen.clicked.connect(self.generate_collage)
        self.icon_label = QLabel(); self.icon_label.setFixedSize(64, 64)
        if os.path.exists("mcm.png"):
            self.icon_label.setPixmap(QPixmap("mcm.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        gen_container.addWidget(self.btn_gen); gen_container.addWidget(self.icon_label); gen_container.addStretch()
        v5.addLayout(gen_container)
        
        bottom_row.addWidget(self.group5, 1)
        l_col2.addLayout(bottom_row)
        splitter.addWidget(col1); splitter.addWidget(col2); main_layout.addWidget(splitter)

        self.preview_timer = QTimer(); self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.update_preview)

    def set_dirty(self): self.is_dirty = True

    def on_ui_content_changed(self): 
        self.trigger_preview_refresh()
        if not self.text_editor.signalsBlocked(): self.set_dirty()

    def check_unsaved_changes(self):
        if not self.is_dirty: return True
        ret = QMessageBox.question(self, "Unsaved changes", 
                                 "You have unsaved changes. Save them before proceeding?",
                                 QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save: return self.save_project_action()
        return ret == QMessageBox.Discard

    def closeEvent(self, event):
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()

    def new_project_action(self):
        if self.check_unsaved_changes():
            self.reset_settings()
            self.video_path = ""
            self.src_list.clear()
            self.preview_label.setText("No video loaded")
            self.current_project_name = "Untitled"
            self.extra_params.clear()
            self.is_dirty = False

    def sort_items(self):
        items_data = [self.dst_list.item(i).data(Qt.UserRole) for i in range(self.dst_list.count())]
        items_data.sort(key=lambda x: x['frame'])
        self.dst_list.clear()
        for data in items_data:
            it = QListWidgetItem(f"[{data['frame']}] {data['text']}"); it.setData(Qt.UserRole, data); self.dst_list.addItem(it)
        self.set_dirty()

    def on_text_selected(self, item):
        self.base_frame = item.data(Qt.UserRole)
        self.current_frame = self.base_frame
        self.text_editor.blockSignals(True); self.text_editor.setText(item.text()); self.text_editor.blockSignals(False)
        self.update_preview()

    def show_about(self):
        msg = QMessageBox(self); msg.setWindowTitle("About"); msg.setTextFormat(Qt.RichText)
        if os.path.exists("mcm.png"): msg.setIconPixmap(QPixmap("mcm.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        text = (f"<div style='margin-left: 10px;'><b style='font-size: 14px;'>Movie Collage Maker {self.version}</b><br><br>"
                "&copy; 2026 Krzysztof Blachnicki<br>License: MIT<br><br>"
                "Website: <a href='https://krzysiu.net'>krzysiu.net</a><br>"
                "GitHub: <a href='https://github.com/Krzysiu/movieCollageMaker'>movieCollageMaker</a><br>"
                "Support: <a href='https://buymeacoffee.com/krzysiunet'>buymeacoffee.com/krzysiunet</a></div>")
        msg.setText(text); msg.exec()

    def load_file(self, p, force_no_prompt=False):
        if not force_no_prompt and not self.check_unsaved_changes(): return
        if not os.path.exists(p): return
        if p.endswith('.mcm'): self.open_project(p); return
        self.reset_settings(); self.video_path = p
        self.current_project_name = os.path.basename(p)
        w_cmd = ['ffprobe', '-v', '0', '-select_streams', 'v:0', '-show_entries', 'stream=width', '-of', 'csv=p=0', p]
        try: self.video_width = int(subprocess.run(w_cmd, capture_output=True, text=True).stdout.strip())
        except: self.video_width = 1280
        res = subprocess.run(['ffprobe', '-v', '0', '-of', 'csv=p=0', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', p], capture_output=True, text=True).stdout.strip()
        if '/' in res: n, d = res.split('/'); self.fps = float(n)/float(d)
        self.extract_subs(p); self.is_dirty = False

    def open_project(self, p):
        with open(p, 'r') as f:
            d = json.load(f); self.load_file(d['v'], force_no_prompt=True); self.reset_settings()
            self.current_project_name = os.path.basename(p)
            self.font_family, self.font_size = d.get('f', "Arial"), d.get('s', 45)
            self.extra_params.setText(d.get('extra', ""))
            self.check_border.blockSignals(True); self.check_border.setChecked(d.get('brd_en', False)); self.check_border.blockSignals(False)
            self.spin_border.blockSignals(True); self.spin_border.setValue(d.get('brd_sz', 2)); self.spin_border.blockSignals(False)
            self.border_color = d.get('brd_cl', "#FF00FF")
            self.spin_tile.blockSignals(True); self.spin_tile.setValue(d.get('tile_c', 2)); self.spin_tile.blockSignals(False)
            self.combo_dir.blockSignals(True); self.combo_dir.setCurrentIndex(d.get('layout', 0)); self.combo_dir.blockSignals(False)
            for i in d['i']:
                it = QListWidgetItem(f"[{i['frame']}] {i['text']}"); it.setData(Qt.UserRole, i); self.dst_list.addItem(it)
            self.is_dirty = False

    def save_project_action(self):
        p, _ = QFileDialog.getSaveFileName(self, "Save project", "", "Project (*.mcm)")
        if p:
            d = {
                "v": self.video_path, 
                "f": self.font_family, 
                "s": self.font_size, 
                "extra": self.extra_params.text(), # ZAPIS DODANY
                "brd_en": self.check_border.isChecked(), 
                "brd_sz": self.spin_border.value(), 
                "brd_cl": self.border_color, 
                "tile_c": self.spin_tile.value(), 
                "layout": self.combo_dir.currentIndex(), 
                "i": [self.dst_list.item(i).data(Qt.UserRole) for i in range(self.dst_list.count())]
            }
            with open(p, 'w') as f: json.dump(d, f)
            self.current_project_name = os.path.basename(p)
            self.is_dirty = False; return True
        return False

    def generate_collage(self):
        if self.dst_list.count() == 0: return
        f_out, _ = QFileDialog.getSaveFileName(self, "Save result", "collage.jpg", "Images (*.jpg *.png *.webp)")
        if not f_out: return
        self.btn_gen.setEnabled(False); self.btn_gen.setText("GENERATING..."); QApplication.processEvents()
        try:
            processed = []
            for i in range(self.dst_list.count()):
                data = self.dst_list.item(i).data(Qt.UserRole)
                tmp_r, tmp_f = os.path.join(self.temp_dir, f"r_{i}.png"), os.path.join(self.temp_dir, f"f_{i}.png")
                subprocess.run(['ffmpeg', '-y', '-ss', str(data['frame']/self.fps), '-i', self.video_path, '-vframes', '1', tmp_r], capture_output=True)
                self.annotate_frame(tmp_r, tmp_f, data['text']); processed.append(tmp_f)
            
            is_h = self.combo_dir.currentIndex() == 0
            tile = f"{self.spin_tile.value()}x" if is_h else f"x{self.spin_tile.value()}"
            bg_color = self.border_color if self.check_border.isChecked() else "black"
            
            # Budujemy komendę ostrożnie
            cmd = ['magick', 'montage'] + processed + ['-tile', tile, '-geometry', '+0+0', '-background', bg_color]
            
            if self.check_border.isChecked():
                cmd += ['-bordercolor', self.border_color, '-border', str(self.spin_border.value())]
            
            # Obsługa parametrów extra bez shlex, który na Windows psuje %
            extra = self.extra_params.text().strip()
            if extra:
                # Na Windowsie przy subprocess.run(shell=False) lepiej rozbić to ręcznie spacja po spacji
                # jeśli nie ma cudzysłowów w parametrach. Jeśli są, użyjemy prostego split().
                cmd += extra.split(' ')
                
            cmd.append(f_out)
            
            # shell=True na Windows pomaga z niektórymi wywołaniami Magick, 
            # ale spróbujmy najpierw standardowo (bezpieczniej)
            subprocess.run(cmd, capture_output=True, text=True)
            
        finally:
            self.btn_gen.setEnabled(True); self.btn_gen.setText("GENERATE FILE...")

    def annotate_frame(self, in_p, out_p, text):
        wrap_width = int(self.video_width * 0.9)
        cmd = ['magick', 'convert', in_p, '-background', 'none', '-fill', 'white', '-font', self.font_family, '-pointsize', str(self.font_size), '-size', f'{wrap_width}x', '-gravity', 'center', f"caption:{text}", '-gravity', 'South', '-geometry', '+0+30', '-composite', out_p]
        subprocess.run(cmd, capture_output=True)

    def extract_subs(self, p):
        out = os.path.join(self.temp_dir, "s.srt")
        if os.path.exists(out):
            try: os.remove(out)
            except: pass
            
        subprocess.run(['ffmpeg', '-y', '-i', p, '-map', '0:s:0', out], capture_output=True)
        
        if not os.path.exists(out):
            ext_srt = os.path.splitext(p)[0] + ".srt"
            if os.path.exists(ext_srt):
                shutil.copy(ext_srt, out)

        if os.path.exists(out):
            self.src_list.clear()
            with open(out, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                if not content: return
                for b in content.split('\n\n'):
                    ls = b.strip().split('\n')
                    if len(ls) >= 3:
                        try:
                            t = ls[1].split(' --> ')[0].replace(',', '.')
                            h, m, s = t.split(':')
                            sec = int(h)*3600 + int(m)*60 + float(s)
                            it = QListWidgetItem(" ".join(ls[2:]))
                            it.setData(Qt.UserRole, int(sec * self.fps))
                            self.src_list.addItem(it)
                        except: continue

    def reset_settings(self):
        self.dst_list.clear(); self.font_family = "Arial"; self.font_size = 45; self.border_color = "#FF00FF"
        self.check_border.blockSignals(True); self.check_border.setChecked(False); self.check_border.blockSignals(False)
        self.spin_border.blockSignals(True); self.spin_border.setValue(2); self.spin_border.blockSignals(False)
        self.spin_tile.blockSignals(True); self.spin_tile.setValue(2); self.spin_tile.blockSignals(False)
        self.combo_dir.blockSignals(True); self.combo_dir.setCurrentIndex(0); self.combo_dir.blockSignals(False)
        self.is_dirty = False

    def import_movie_dialog(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select video", "", "Video (*.mkv *.mp4 *.avi)")
        if f: self.load_file(f)

    def open_project_dialog(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open project", "", "Project (*.mcm)")
        if f: self.open_project(f)

    def update_preview(self):
        if not self.video_path or self.base_frame == 0: return
        r, f = os.path.join(self.temp_dir, "p_r.jpg"), os.path.join(self.temp_dir, "p_f.jpg")
        subprocess.run(['ffmpeg', '-y', '-ss', str(self.current_frame/self.fps), '-i', self.video_path, '-vframes', '1', r], capture_output=True)
        self.annotate_frame(r, f, self.text_editor.toPlainText())
        if os.path.exists(f):
            pix = QPixmap(f); self.preview_label.setPixmap(pix.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.offset_label.setText(f"Frame offset: {'+' if self.current_frame - self.base_frame >= 0 else ''}{self.current_frame - self.base_frame}")

    def adjust_frame(self, d): self.current_frame += d; self.update_preview(); self.set_dirty()
    def trigger_preview_refresh(self): self.preview_timer.start(300)
    def choose_font(self):
        ok, font = QFontDialog.getFont(QFont(self.font_family, self.font_size), self)
        if ok: self.font_family, self.font_size = font.family(), font.pointSize(); self.update_preview(); self.set_dirty()
    def choose_border_color(self):
        c = QColorDialog.getColor(QColor(self.border_color), self)
        if c.isValid(): self.border_color = c.name(); self.set_dirty()
    def filter_list(self, t):
        for i in range(self.src_list.count()): it = self.src_list.item(i); it.setHidden(t.lower() not in it.text().lower())
    def add_to_project(self):
        if not self.video_path: return
        txt = self.text_editor.toPlainText(); data = {"frame": self.current_frame, "text": txt}
        it = QListWidgetItem(f"[{self.current_frame}] {txt}"); it.setData(Qt.UserRole, data); self.dst_list.addItem(it); self.set_dirty()
    def remove_item(self):
        for it in self.dst_list.selectedItems(): self.dst_list.takeItem(self.dst_list.row(it)); self.set_dirty()
    def dragEnterEvent(self, e): 
        if e.mimeData().hasUrls(): e.accept()
    def dropEvent(self, e): self.load_file(e.mimeData().urls()[0].toLocalFile())
    def create_h_layout(self, l, w): h = QHBoxLayout(); h.addWidget(l); h.addWidget(w); return h

if __name__ == "__main__":
    app = QApplication(sys.argv)
    if os.path.exists("mcm-16.png"): app.setWindowIcon(QIcon("mcm-16.png"))
    win = MovieCollageMaker(sys.argv[1] if len(sys.argv) > 1 else None)
    win.show()
    sys.exit(app.exec())