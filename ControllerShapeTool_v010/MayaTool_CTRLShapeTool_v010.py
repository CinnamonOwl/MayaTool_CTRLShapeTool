# -------------------------------------------------------------------------
# CTRL Shape Tool v009
# made with the help of Gemini & ChatGPT
# -------------------------------------------------------------------------

import maya.cmds as cmds
import os
import json
import subprocess

# --- VERSION BRIDGE ---
try:
    from PySide6 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

# -----------------------------------------------------------------------------
# CUSTOM WIDGETS
# -----------------------------------------------------------------------------

class FlowLayout(QtWidgets.QLayout):
    """Reflows items into a grid that adapts to window width."""
    def __init__(self, parent=None, margin=0, hSpacing=5, vSpacing=5):
        super(FlowLayout, self).__init__(parent)
        self._hSpace = hSpacing
        self._vSpace = vSpacing
        self.setContentsMargins(margin, margin, margin, margin)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def horizontalSpacing(self):
        return self._hSpace

    def verticalSpacing(self):
        return self._vSpace

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList): return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList): return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QtCore.QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        margins = self.contentsMargins()
        effectiveRect = rect.adjusted(margins.left(), margins.top(), -margins.right(), -margins.bottom())
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0
        spacing = self.horizontalSpacing()

        for item in self.itemList:
            wid = item.widget()
            if wid.isHidden(): continue
            spaceX = spacing
            spaceY = self.verticalSpacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y() + margins.bottom()

class ClickableRow(QtWidgets.QFrame):
    clicked = QtCore.Signal()
    def __init__(self, parent=None):
        super(ClickableRow, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.setStyleSheet("""
            ClickableRow { background-color: #444444; border-radius: 4px; }
            ClickableRow:hover { background-color: #555555; }
        """)
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton: self.clicked.emit()
        super(ClickableRow, self).mouseReleaseEvent(event)

# -----------------------------------------------------------------------------
# MAIN TOOL
# -----------------------------------------------------------------------------
class ControlShapeTool(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ControlShapeTool, self).__init__(parent=parent)
        self.setWindowTitle("CTRL Shape Tool Pro")
        self.setObjectName("CtrlShapeToolWindow")
        self.setMinimumWidth(300)
        
        self.lib_var = "CtrlLib_DataDirectory"
        self.stored_data = None
        self.is_grid_view = False
        self.library_container = None
        
        # Flag to track if we should actually show the window
        self.setup_successful = False
        
        # Run Validation
        if self.run_startup_check():
            self.setup_ui()
            self.refresh_library()
            self.setup_successful = True # Mark as ready to show
    
    def run_startup_check(self):
        """
        Checks for library. Returns True if good, False if user cancels.
        """
        # 1. Check if path exists in memory and on disk
        current_path = cmds.optionVar(q=self.lib_var) if cmds.optionVar(exists=self.lib_var) else None
        
        if current_path and os.path.exists(current_path):
            return True # All good

        # 2. Path missing: Show Notification Window first
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Library Setup Required")
        msg.setText("Welcome! To use the CTRL Shape Tool, you must select a library folder.\n\nClick OK to select a folder.")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        
        # 3. Handle User Choice
        if msg.exec_() == QtWidgets.QMessageBox.Ok:
            # User clicked OK, now show the file browser
            path = cmds.fileDialog2(fileMode=3, caption="Select Library Folder")
            if path:
                cmds.optionVar(sv=(self.lib_var, path[0]))
                return True
        
        # If we reach here, the user hit Cancel on either window
        cmds.warning("Setup cancelled. Tool will not open.")
        return False

    def add_separator(self, layout):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(line)

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # SETTINGS
        settings_btn = QtWidgets.QPushButton("SET LIBRARY FOLDER")
        settings_btn.clicked.connect(self.set_directory)
        self.main_layout.addWidget(settings_btn)

        self.add_separator(self.main_layout)

        # ACTION BUTTONS
        self.btn_store = QtWidgets.QPushButton("STORE CTRL")
        self.btn_store.setStyleSheet("background-color: #66b3ff; color: #000000; font-weight: bold; height: 35px;")
        self.btn_store.clicked.connect(self.store_logic)
        
        self.btn_create = QtWidgets.QPushButton("CREATE CTRL")
        self.btn_create.setStyleSheet("background-color: #bf80ff; color: #000000; height: 35px; font-weight: bold;")
        self.btn_create.clicked.connect(self.create_logic)

        self.btn_change = QtWidgets.QPushButton("CHANGE SELECTED")
        self.btn_change.setStyleSheet("background-color: #ff99ff; color: #000000; height: 35px; font-weight: bold;")
        self.btn_change.clicked.connect(self.change_selected_logic)

        self.chk_autofit = QtWidgets.QCheckBox("Auto-Fit (Uniform Scaling)")
        self.chk_autofit.setChecked(True)
        self.main_layout.addWidget(self.chk_autofit)

        self.btn_save = QtWidgets.QPushButton("SAVE SELECTION TO JSON")
        self.btn_save.setStyleSheet("background-color: #99ffcc; color: #000000; height: 35px; font-weight: bold;")
        self.btn_save.clicked.connect(self.save_logic)

        self.main_layout.addWidget(self.btn_store)
        self.main_layout.addWidget(self.btn_create)
        self.main_layout.addWidget(self.btn_change)
        self.main_layout.addWidget(self.btn_save)

        self.add_separator(self.main_layout)

        # HEADER
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addWidget(QtWidgets.QLabel("<b>SAVED JSON LIBRARY</b>"))
        self.view_toggle_btn = QtWidgets.QPushButton("Switch to Grid")
        self.view_toggle_btn.setFixedWidth(100)
        self.view_toggle_btn.clicked.connect(self.toggle_view_mode)
        header_layout.addWidget(self.view_toggle_btn)
        self.main_layout.addLayout(header_layout)

        # SEARCH
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search shapes...")
        self.search_bar.setStyleSheet("background-color: #333; color: white; border-radius: 4px; padding: 4px;")
        self.search_bar.textChanged.connect(self.filter_library)
        self.main_layout.addWidget(self.search_bar)

        # SCROLL
        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll)

    # --- MATH & LOGIC ---

    def get_curve_data(self):
        sel = cmds.ls(sl=True, long=True)
        if not sel:
            cmds.warning("Please select a curve.")
            return None
        shapes = cmds.listRelatives(sel[0], shapes=True, type="nurbsCurve", noIntermediate=True, fullPath=True)
        if not shapes: return None

        all_shape_data = []
        for shape in shapes:
            all_shape_data.append({
                "degree": cmds.getAttr(f"{shape}.degree"),
                "spans": cmds.getAttr(f"{shape}.spans"),
                "periodic": cmds.getAttr(f"{shape}.form") > 0,
                "cvs": [cmds.xform(f"{shape}.cv[{i}]", q=True, t=True, os=True) for i in range(cmds.getAttr(f"{shape}.degree") + cmds.getAttr(f"{shape}.spans"))]
            })
        
        bbox = cmds.exactWorldBoundingBox(sel[0])
        size = [bbox[3]-bbox[0], bbox[4]-bbox[1], bbox[5]-bbox[2]]
        return {"shapes": all_shape_data, "base_max_size": max(size) if max(size) > 0 else 1.0}

    def center_pivot(self, obj):
        bbox = cmds.exactWorldBoundingBox(obj)
        center = [(bbox[i] + bbox[i+3]) / 2 for i in range(3)]
        cmds.xform(obj, piv=center, ws=True)

    def copy_color(self, source_shape, target_transform):
        target_shape = cmds.listRelatives(target_transform, shapes=True)[0]
        if cmds.getAttr(f"{source_shape}.overrideEnabled"):
            cmds.setAttr(f"{target_shape}.overrideEnabled", 1)
            if cmds.getAttr(f"{source_shape}.overrideRGBColors"):
                cmds.setAttr(f"{target_shape}.overrideRGBColors", 1)
                rgb = cmds.getAttr(f"{source_shape}.overrideColorRGB")[0]
                cmds.setAttr(f"{target_shape}.overrideColorRGB", rgb[0], rgb[1], rgb[2])
            else:
                idx = cmds.getAttr(f"{source_shape}.overrideColor")
                cmds.setAttr(f"{target_shape}.overrideColor", idx)

    # --- CORE FUNCTIONS (WITH UNDO CHUNKS) ---

    def create_logic(self):
        if not self.stored_data:
            cmds.warning("Memory is empty!")
            return
        
        # Start UNDO Chunk
        cmds.undoInfo(openChunk=True, chunkName="Create Stored Control")
        try:
            new_ctrl = cmds.group(em=True, name="default_Ctrl")
            for i, s_data in enumerate(self.stored_data["shapes"]):
                temp_curve = None
                if s_data["periodic"]:
                    temp_curve = cmds.circle(ch=False, name=f"temp_shape_{i}")[0]
                    cmds.rebuildCurve(temp_curve, ch=False, rpo=True, rt=0, s=s_data["spans"], d=s_data["degree"])
                else:
                    temp_curve = cmds.curve(d=s_data["degree"], p=s_data["cvs"], name=f"temp_shape_{i}")

                for j, pos in enumerate(s_data["cvs"]):
                    cmds.xform(f"{temp_curve}.cv[{j}]", t=pos, os=True)

                shape_node = cmds.listRelatives(temp_curve, shapes=True)[0]
                cmds.parent(shape_node, new_ctrl, r=True, s=True)
                cmds.delete(temp_curve)
            
            # For creation, we DO want to center the pivot at origin
            self.center_pivot(new_ctrl)
            cmds.move(0,0,0, new_ctrl, rpr=True)
            cmds.makeIdentity(new_ctrl, apply=True, t=1, r=1, s=1)
            cmds.select(new_ctrl)
            
        except Exception as e:
            cmds.warning(f"Error creating control: {e}")
        finally:
            cmds.undoInfo(closeChunk=True)

    def change_selected_logic(self):
        if not self.stored_data: return
        sel_list = cmds.ls(sl=True, long=True)
        if not sel_list: return
        
        cmds.undoInfo(openChunk=True, chunkName="Change Control Shape")
        try:
            orig_max = self.stored_data.get("base_max_size", 1.0)
            
            for target in sel_list:
                target_shapes = cmds.listRelatives(target, shapes=True, type="nurbsCurve", fullPath=True) or []
                
                scale_factor = 1.0
                if self.chk_autofit.isChecked():
                    curr_bbox = cmds.exactWorldBoundingBox(target)
                    curr_size = [curr_bbox[3]-curr_bbox[0], curr_bbox[4]-curr_bbox[1], curr_bbox[5]-curr_bbox[2]]
                    curr_max = max(curr_size)
                    if orig_max > 0: scale_factor = curr_max / orig_max

                for i, s_data in enumerate(self.stored_data["shapes"]):
                    if i < len(target_shapes):
                        old_shape = target_shapes[i]
                        old_form_periodic = (cmds.getAttr(f"{old_shape}.form") > 0)
                        new_form_periodic = s_data["periodic"]
                        
                        if old_form_periodic == new_form_periodic:
                            cmds.rebuildCurve(old_shape, ch=False, rpo=True, rt=0, s=s_data["spans"], d=s_data["degree"])
                            for j, pos in enumerate(s_data["cvs"]):
                                scaled_pos = [p * scale_factor for p in pos]
                                cmds.xform(f"{old_shape}.cv[{j}]", t=scaled_pos, os=True)
                        else:
                            temp_trans = None
                            if new_form_periodic:
                                temp_trans = cmds.circle(ch=False)[0]
                                cmds.rebuildCurve(temp_trans, ch=False, rpo=True, rt=0, s=s_data["spans"], d=s_data["degree"])
                            else:
                                temp_trans = cmds.curve(d=s_data["degree"], p=s_data["cvs"])
                            
                            for j, pos in enumerate(s_data["cvs"]):
                                scaled_pos = [p * scale_factor for p in pos]
                                cmds.xform(f"{temp_trans}.cv[{j}]", t=scaled_pos, os=True)
                                
                            self.copy_color(old_shape, temp_trans)
                            new_shape = cmds.listRelatives(temp_trans, shapes=True)[0]
                            cmds.parent(new_shape, target, r=True, s=True)
                            cmds.delete(old_shape)
                            cmds.delete(temp_trans)

                # REMOVED: self.center_pivot(target) 
                # Pivot now stays exactly where it was.

            cmds.select(sel_list)
            
        except Exception as e:
            cmds.warning(f"Error changing control: {e}")
        finally:
            cmds.undoInfo(closeChunk=True)

    # --- UI & FILES ---

    def set_directory(self):
        path = cmds.fileDialog2(fileMode=3, caption="Select Library Folder")
        if path:
            cmds.optionVar(sv=(self.lib_var, path[0]))
            self.refresh_library()

    def store_logic(self):
        self.stored_data = self.get_curve_data()
        if self.stored_data: print("Stored in memory.")

    def save_logic(self):
        data = self.get_curve_data()
        path = cmds.optionVar(q=self.lib_var) if cmds.optionVar(exists=self.lib_var) else None
        if not data or not path: return

        res = cmds.promptDialog(title='Save JSON', message='File Name:', button=['OK', 'Cancel'], defaultButton='OK')
        if res == 'OK':
            name = cmds.promptDialog(q=True, text=True)
            if not name: return
            
            full_path = os.path.join(path, f"{name}.json")
            icons_dir = os.path.join(path, "icons")
            if not os.path.exists(icons_dir): os.makedirs(icons_dir)
            img_path = os.path.join(icons_dir, f"{name}.jpg")
            
            if os.path.exists(full_path):
                if cmds.confirmDialog(title='Overwrite?', message='File exists. Overwrite?', button=['Yes','No']) == 'No': return

            with open(full_path, 'w') as f:
                json.dump(data, f, indent=4)
            self.launch_snapshot_tool(img_path)

    def launch_snapshot_tool(self, img_path):
        win_name = "CtrlSnapshotToolWindow"
        if cmds.window(win_name, exists=True): cmds.deleteUI(win_name)
        cmds.window(win_name, title="Frame Thumbnail", widthHeight=(300, 350))
        main_col = cmds.columnLayout(adjustableColumn=True)
        pane = cmds.paneLayout(height=300, parent=main_col)
        editor = cmds.modelEditor(displayAppearance='smoothShaded', grid=False, allObjects=True)
        cmds.setParent(main_col)
        cmds.button(label="SNAP & FINISH", height=40, backgroundColor=[0.35, 0.6, 0.35],
                    command=lambda x: self.finish_snapshot(win_name, editor, img_path))
        cmds.showWindow(win_name)
        cmds.modelEditor(editor, edit=True, camera="persp", activeView=True)
        cmds.modelEditor(editor, edit=True, setFocus=True)
        cmds.viewFit(all=True)

    def finish_snapshot(self, win_name, editor, img_path):
        cmds.refresh()
        cmds.playblast(editorPanelName=editor, completeFilename=img_path, format="image", compression="jpg", 
                       viewer=False, showOrnaments=False, percent=100, widthHeight=[128, 128], frame=cmds.currentTime(q=True))
        cmds.deleteUI(win_name)
        self.refresh_library()

    def toggle_view_mode(self):
        self.is_grid_view = not self.is_grid_view
        self.view_toggle_btn.setText("Switch to List" if self.is_grid_view else "Switch to Grid")
        self.refresh_library()

    def filter_library(self, text):
        if not self.library_container or not self.library_container.layout(): return
        search_text = text.lower()
        layout = self.library_container.layout()
        
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                name = ""
                if isinstance(widget, ClickableRow):
                    children = widget.findChildren(QtWidgets.QLabel)
                    if len(children) >= 2: name = children[1].text().lower()
                elif isinstance(widget, QtWidgets.QToolButton):
                    name = widget.text().lower()
                widget.setVisible(search_text in name)

    def refresh_library(self):
        path = cmds.optionVar(q=self.lib_var) if cmds.optionVar(exists=self.lib_var) else None
        self.library_container = QtWidgets.QWidget()
        
        if self.is_grid_view:
            layout = FlowLayout(self.library_container, margin=5, hSpacing=5, vSpacing=5)
            btn_style = "QToolButton { background-color: #444444; border-radius: 5px; color: white; font-size: 10px; } QToolButton:hover { background-color: #555555; }"
        else:
            layout = QtWidgets.QVBoxLayout(self.library_container)
            layout.setSpacing(2)
            layout.setAlignment(QtCore.Qt.AlignTop)
            layout.setContentsMargins(2, 2, 2, 2)

        if path and os.path.exists(path):
            files = sorted([f for f in os.listdir(path) if f.endswith(".json")])
            for f in files:
                img_path = os.path.join(path, "icons", f.replace(".json", ".jpg"))
                has_icon = os.path.exists(img_path)
                
                if self.is_grid_view:
                    btn = QtWidgets.QToolButton()
                    btn.setText(f.replace(".json", ""))
                    btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
                    btn.setFixedSize(45, 60)
                    btn.setIconSize(QtCore.QSize(40, 40))
                    if has_icon: btn.setIcon(QtGui.QIcon(img_path))
                    btn.setStyleSheet(btn_style)
                    btn.clicked.connect(lambda *args, fn=f: self.load_and_run(fn))
                    self._add_context_menu(btn, f)
                    layout.addWidget(btn)
                else:
                    row = ClickableRow()
                    row.setMinimumHeight(50)
                    row.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                    
                    row_layout = QtWidgets.QHBoxLayout(row)
                    row_layout.setContentsMargins(5, 5, 5, 5)
                    row_layout.setSpacing(10)
                    
                    lbl_icon = QtWidgets.QLabel()
                    lbl_icon.setFixedSize(40, 40)
                    if has_icon:
                        lbl_icon.setPixmap(QtGui.QIcon(img_path).pixmap(40, 40))
                        lbl_icon.setScaledContents(True)
                    else:
                        lbl_icon.setText(" No IMG ")
                        lbl_icon.setStyleSheet("background-color: #333; color: #777; font-size: 8px;")
                        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)
                    
                    lbl_text = QtWidgets.QLabel(f.replace(".json", ""))
                    lbl_text.setAlignment(QtCore.Qt.AlignCenter)
                    lbl_text.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
                    
                    row_layout.addWidget(lbl_icon)
                    row_layout.addWidget(lbl_text)
                    
                    row.clicked.connect(lambda fn=f: self.load_and_run(fn))
                    self._add_context_menu(row, f)
                    layout.addWidget(row)

        self.scroll.setWidget(self.library_container)
        if self.search_bar.text(): self.filter_library(self.search_bar.text())

    def _add_context_menu(self, widget, filename):
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda pos, fn=filename: self.show_context_menu(pos, fn))

    def show_context_menu(self, pos, filename):
        menu = QtWidgets.QMenu()
        open_act = menu.addAction("Open Folder")
        rename_act = menu.addAction("Rename")
        delete_act = menu.addAction("Delete")
        
        action = menu.exec_(QtGui.QCursor.pos())
        path = cmds.optionVar(q=self.lib_var)
        full_path = os.path.join(path, filename)
        icons_dir = os.path.join(path, "icons")

        if action == open_act:
            if os.name == 'nt': os.startfile(path)
            else: subprocess.call(["open", path])
        elif action == rename_act:
            res = cmds.promptDialog(title='Rename', message="New Name:", text=filename.replace(".json",""), button=['OK','Cancel'])
            if res == 'OK':
                new_n = cmds.promptDialog(q=True, text=True)
                if new_n:
                    new_json = os.path.join(path, f"{new_n}.json")
                    os.rename(full_path, new_json)
                    old_img = os.path.join(icons_dir, filename.replace(".json", ".jpg"))
                    if os.path.exists(old_img): os.rename(old_img, os.path.join(icons_dir, f"{new_n}.jpg"))
                    self.refresh_library()
        elif action == delete_act:
            if cmds.confirmDialog(title='Delete', message=f'Delete {filename}?', button=['Yes','No']) == 'Yes':
                os.remove(full_path)
                old_img = os.path.join(icons_dir, filename.replace(".json", ".jpg"))
                if os.path.exists(old_img): os.remove(old_img)
                self.refresh_library()

    def load_and_run(self, filename):
        path = os.path.join(cmds.optionVar(q=self.lib_var), filename)
        with open(path, 'r') as f:
            self.stored_data = json.load(f)
        
        if cmds.ls(sl=True):
            self.change_selected_logic()
        else:
            self.create_logic()

# -----------------------------------------------------------------------------
# AUTO-ICON UPDATER (Paste this at the bottom of any script)
# -----------------------------------------------------------------------------
def update_shelf_icon():
    """
    Automatically updates the Maya shelf button that launched this script.
    Checks if the button uses the default icon, and if so, swaps it for the custom one.
    """
    import maya.cmds as cmds
    import maya.mel as mel

    # --- CONFIGURATION (Edit these two lines) ---
    SCRIPT_NAME = "ControlShapeTool"       # A unique word in your script's class or function name
    ICON_FILE   = "ControlShapeTool_icon.png"   # The icon file name (must be in Maya's icon folder)
    # --------------------------------------------

    try:
        # 1. Get the currently active shelf tab (e.g., "Custom", "Rigging")
        current_shelf = mel.eval("tabLayout -q -selectTab $gShelfTopLevel")
        
        # 2. Get all buttons on that shelf
        buttons = cmds.shelfLayout(current_shelf, q=True, childArray=True) or []
        
        for btn in buttons:
            # 3. Read the Python command stored inside the button
            cmd = cmds.shelfButton(btn, q=True, command=True) or ""
            
            # 4. Check if this button runs THIS script
            if SCRIPT_NAME in cmd:
                # 5. Check if it's still using a default generic icon
                current_img = cmds.shelfButton(btn, q=True, image=True)
                if "pythonFamily" in current_img or "commandButton" in current_img:
                    # 6. Swap it!
                    cmds.shelfButton(btn, e=True, image=ICON_FILE)
                    print(f"Icon updated for {SCRIPT_NAME}")
    except Exception as e:
        print(f"Could not auto-update icon: {e}")

# Run it immediately
update_shelf_icon()

def main():
    # Clean up old windows
    if cmds.workspaceControl("CtrlShapeToolWindowWorkspaceControl", exists=True):
        cmds.deleteUI("CtrlShapeToolWindowWorkspaceControl", control=True)
    if cmds.window("CtrlShapeToolWindow", exists=True):
        cmds.deleteUI("CtrlShapeToolWindow")

    global my_tool
    my_tool = ControlShapeTool()
    
    # ONLY show the window if the setup (library check) was successful
    if my_tool.setup_successful:
        my_tool.show(dockable=True)
    else:
        # If failed/cancelled, delete the python object so it doesn't linger
        my_tool.deleteLater()

main()