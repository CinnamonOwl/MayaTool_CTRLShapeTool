# -------------------------------------------------------------------------
# CTRL Shape Tool v010
# -------------------------------------------------------------------------

import maya.cmds as cmds
import os
import json
import subprocess

import maya.OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

try:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance

# -------------------------------------------------------------------------
# SHARED STYLESHEET
# Palette — same family as the Renamer tool:
#   Blue   #66b3ff  — Store,  focus rings, search bar
#   Purple #bf80ff  — Create
#   Pink   #ff99ff  — Change Selected
#   Mint   #99ffcc  — Save to JSON
#   Base dark       — #1e1e24 / #26262e (identical to Renamer)
# Buttons here are slightly more saturated than the Renamer's
# muted variants — they're the primary actions of this tool.
# -------------------------------------------------------------------------
STYLESHEET = """
/* === BASE === */
QWidget {
    background-color: #1e1e24;
    color: #d0d0d8;
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 12px;
}

/* === SECTION FRAMES === */
QFrame#sectionFrame {
    background-color: #26262e;
    border: 1px solid #32323c;
    border-radius: 6px;
}

/* === LABELS === */
QLabel {
    color: #88889a;
    font-size: 11px;
    background: transparent;
}
QLabel#sectionTitle {
    color: #66b3ff;
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1.5px;
    background: transparent;
}

/* === SEPARATORS === */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #32323c;
    background-color: #32323c;
    border: none;
    max-height: 1px;
}

/* === LINE EDITS === */
QLineEdit {
    background-color: #14141a;
    border: 1px solid #36363f;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0ea;
    font-weight: bold;
    selection-background-color: #66b3ff;
    selection-color: #0a0a12;
}
QLineEdit:focus {
    border: 1px solid #66b3ff;
    background-color: #1a1a22;
}
QLineEdit:hover {
    border: 1px solid #505060;
}

/* === CHECKBOXES === */
QCheckBox {
    color: #9090a8;
    spacing: 5px;
    background: transparent;
}
QCheckBox::indicator {
    width: 12px;
    height: 12px;
    border-radius: 2px;
    border: 1px solid #484860;
    background-color: #14141a;
}
QCheckBox::indicator:checked {
    background-color: #66b3ff;
    border: 1px solid #99ccff;
}
QCheckBox::indicator:hover {
    border: 1px solid #66b3ff;
}
QCheckBox:checked {
    color: #99ccff;
}

/* === BUTTONS — Default (neutral) === */
QPushButton {
    background-color: #2e2e38;
    border: 1px solid #3e3e4a;
    border-radius: 4px;
    padding: 4px 10px;
    color: #b0b0c0;
    min-height: 22px;
}
QPushButton:hover {
    background-color: #38384a;
    border: 1px solid #58587a;
    color: #e0e0f0;
}
QPushButton:pressed {
    background-color: #1e1e28;
}

/* === STORE — Blue #76acce === */
QPushButton#storeButton {
    background-color: #1c2c38;
    border: 1px solid #4a7a9a;
    border-radius: 4px;
    color: #76acce;
    font-weight: bold;
    min-height: 35px;
}
QPushButton#storeButton:hover {
    background-color: #243850;
    border: 1px solid #76acce;
    color: #a0c8e8;
}
QPushButton#storeButton:pressed {
    background-color: #141e28;
}

/* === CREATE — Purple #a885d6 === */
QPushButton#createButton {
    background-color: #26203a;
    border: 1px solid #7a5aaa;
    border-radius: 4px;
    color: #a885d6;
    font-weight: bold;
    min-height: 35px;
}
QPushButton#createButton:hover {
    background-color: #322a50;
    border: 1px solid #a885d6;
    color: #c4a8e8;
}
QPushButton#createButton:pressed {
    background-color: #1a1430;
}

/* === CHANGE SELECTED — Pink #9c61a1 === */
QPushButton#changeButton {
    background-color: #2e1e34;
    border: 1px solid #7a4880;
    border-radius: 4px;
    color: #9c61a1;
    font-weight: bold;
    min-height: 35px;
}
QPushButton#changeButton:hover {
    background-color: #3c2648;
    border: 1px solid #9c61a1;
    color: #c088c8;
}
QPushButton#changeButton:pressed {
    background-color: #1e1228;
}

/* === SAVE TO JSON — Green #7baf8a === */
QPushButton#saveButton {
    background-color: #1e2e24;
    border: 1px solid #508060;
    border-radius: 4px;
    color: #7baf8a;
    font-weight: bold;
    min-height: 22px;
    padding: 3px 10px;
    font-size: 11px;
}
QPushButton#saveButton:hover {
    background-color: #263c2e;
    border: 1px solid #7baf8a;
    color: #a0c8aa;
}
QPushButton#saveButton:pressed {
    background-color: #141e18;
}

/* === TOGGLE / SETTINGS (small utility buttons) === */
QPushButton#utilButton {
    background-color: #26262e;
    border: 1px solid #3a3a48;
    border-radius: 4px;
    color: #8888a8;
    min-height: 22px;
    padding: 3px 10px;
    font-size: 11px;
}
QPushButton#utilButton:hover {
    background-color: #2e2e3e;
    border: 1px solid #505070;
    color: #b0b0d0;
}
QPushButton#utilButton:pressed {
    background-color: #1a1a24;
}

/* === SCROLL AREA === */
QScrollArea {
    border: none;
    background-color: #1e1e24;
}
QScrollBar:vertical {
    background: #1e1e24;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #38383f;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background: #66b3ff;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

/* === LIBRARY ROWS === */
ClickableRow {
    background-color: #26262e;
    border: 1px solid #32323c;
    border-radius: 4px;
}
ClickableRow:hover {
    background-color: #2e2e3e;
    border: 1px solid #505070;
}

/* === GRID TOOL BUTTONS === */
QToolButton {
    background-color: #26262e;
    border: 1px solid #32323c;
    border-radius: 4px;
    color: #b0b0c0;
    font-size: 10px;
}
QToolButton:hover {
    background-color: #2e2e3e;
    border: 1px solid #66b3ff;
    color: #e0e0f0;
}
"""

# -------------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------------
def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


# -------------------------------------------------------------------------
# SECTION FRAME HELPER  (mirrors the Renamer's make_section)
# -------------------------------------------------------------------------
def make_section(title, parent_layout):
    frame = QtWidgets.QFrame()
    frame.setObjectName("sectionFrame")
    frame.setFrameShape(QtWidgets.QFrame.StyledPanel)

    outer = QtWidgets.QVBoxLayout(frame)
    outer.setContentsMargins(10, 8, 10, 10)
    outer.setSpacing(6)

    lbl = QtWidgets.QLabel(title.upper())
    lbl.setObjectName("sectionTitle")
    outer.addWidget(lbl)

    inner = QtWidgets.QVBoxLayout()
    inner.setSpacing(6)
    outer.addLayout(inner)

    parent_layout.addWidget(frame)
    return inner

# -------------------------------------------------------------------------
# CUSTOM WIDGETS
# -------------------------------------------------------------------------
class FlowLayout(QtWidgets.QLayout):
    def __init__(self, parent=None, margin=0, hSpacing=5, vSpacing=5):
        super(FlowLayout, self).__init__(parent)
        self._hSpace = hSpacing
        self._vSpace = vSpacing
        self.setContentsMargins(margin, margin, margin, margin)
        self.itemList = []

    def addItem(self, item):       self.itemList.append(item)
    def horizontalSpacing(self):   return self._hSpace
    def verticalSpacing(self):     return self._vSpace
    def count(self):               return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList): return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList): return self.itemList.pop(index)
        return None

    def expandingDirections(self): return QtCore.Qt.Orientations(0)
    def hasHeightForWidth(self):   return True

    def heightForWidth(self, width):
        return self.doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):    return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        m = self.contentsMargins()
        size += QtCore.QSize(m.left() + m.right(), m.top() + m.bottom())
        return size

    def doLayout(self, rect, testOnly):
        m = self.contentsMargins()
        er = rect.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        x, y, lineHeight = er.x(), er.y(), 0

        for item in self.itemList:
            if item.widget().isHidden(): continue
            nextX = x + item.sizeHint().width() + self._hSpace
            if nextX - self._hSpace > er.right() and lineHeight > 0:
                x = er.x()
                y = y + lineHeight + self._vSpace
                nextX = x + item.sizeHint().width() + self._hSpace
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y() + m.bottom()


class ClickableRow(QtWidgets.QFrame):
    clicked = QtCore.Signal()
    def __init__(self, parent=None):
        super(ClickableRow, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
        super(ClickableRow, self).mouseReleaseEvent(event)


# -------------------------------------------------------------------------
# MAIN TOOL
# -------------------------------------------------------------------------
class ControlShapeTool(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ControlShapeTool, self).__init__(parent=parent)
        self.setWindowTitle("CTRL Shape Tool")
        self.setObjectName("CtrlShapeToolWindow")
        self.setMinimumWidth(300)
        self.setStyleSheet(STYLESHEET)

        self.lib_var = "CtrlLib_DataDirectory"
        self.stored_data = None
        self.is_grid_view = False
        self.library_container = None
        self.setup_successful = False

        if self.run_startup_check():
            self.setup_ui()
            self.refresh_library()
            self.setup_successful = True

    # ------------------------------------------------------------------
    def run_startup_check(self):
        current_path = cmds.optionVar(q=self.lib_var) if cmds.optionVar(exists=self.lib_var) else None
        if current_path and os.path.exists(current_path):
            return True

        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Library Setup Required")
        msg.setText("Welcome! To use the CTRL Shape Tool, you must select a library folder.\n\nClick OK to select a folder.")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        if msg.exec_() == QtWidgets.QMessageBox.Ok:
            path = cmds.fileDialog2(fileMode=3, caption="Select Library Folder")
            if path:
                cmds.optionVar(sv=(self.lib_var, path[0]))
                return True

        cmds.warning("Setup cancelled. Tool will not open.")
        return False

    # ------------------------------------------------------------------
    def setup_ui(self):
        # Outer layout sits on self (may show Maya grey at edges when docked)
        outer_layout = QtWidgets.QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Inner container owns the theme — this is what the stylesheet colors
        self._container = QtWidgets.QWidget()
        self._container.setObjectName("themedContainer")
        self._container.setStyleSheet("QWidget#themedContainer { background-color: #1e1e24; }")
        self._container.setAutoFillBackground(True)
        outer_layout.addWidget(self._container)

        self.main_layout = QtWidgets.QVBoxLayout(self._container)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)

        # ── SETTINGS ───────────────────────────────────
        settings_btn = QtWidgets.QPushButton("Set Library Folder")
        settings_btn.setObjectName("utilButton")
        settings_btn.clicked.connect(self.set_directory)
        self.main_layout.addWidget(settings_btn)

        # ── ACTIONS ────────────────────────────────────
        actions_inner = make_section("Actions", self.main_layout)

        self.btn_store = QtWidgets.QPushButton("STORE CTRL")
        self.btn_store.setObjectName("storeButton")
        self.btn_store.clicked.connect(self.store_logic)

        self.btn_create = QtWidgets.QPushButton("CREATE CTRL")
        self.btn_create.setObjectName("createButton")
        self.btn_create.clicked.connect(self.create_logic)

        self.btn_change = QtWidgets.QPushButton("CHANGE SELECTED")
        self.btn_change.setObjectName("changeButton")
        self.btn_change.clicked.connect(self.change_selected_logic)

        self.chk_autofit = QtWidgets.QCheckBox("Auto-Fit (Uniform Scaling)")
        self.chk_autofit.setChecked(True)

        actions_inner.addWidget(self.btn_store)
        actions_inner.addWidget(self.btn_create)
        actions_inner.addWidget(self.btn_change)
        actions_inner.addWidget(self.chk_autofit)

        # ── LIBRARY ────────────────────────────────────
        lib_inner = make_section("Saved JSON Library", self.main_layout)

        # Header row: Save button on the left, Switch to Grid on the right
        header_row = QtWidgets.QHBoxLayout()

        self.btn_save = QtWidgets.QPushButton("Save to JSON")
        self.btn_save.setObjectName("saveButton")
        self.btn_save.clicked.connect(self.save_logic)
        header_row.addWidget(self.btn_save)

        header_row.addStretch()

        self.view_toggle_btn = QtWidgets.QPushButton("Switch to Grid")
        self.view_toggle_btn.setObjectName("utilButton")
        self.view_toggle_btn.setFixedWidth(110)
        self.view_toggle_btn.clicked.connect(self.toggle_view_mode)
        header_row.addWidget(self.view_toggle_btn)
        lib_inner.addLayout(header_row)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search shapes...")
        self.search_bar.textChanged.connect(self.filter_library)
        lib_inner.addWidget(self.search_bar)

        self.scroll = QtWidgets.QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumHeight(200)
        lib_inner.addWidget(self.scroll)

    # ------------------------------------------------------------------
    # MATH & LOGIC
    # ------------------------------------------------------------------
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
                "degree":   cmds.getAttr(f"{shape}.degree"),
                "spans":    cmds.getAttr(f"{shape}.spans"),
                "periodic": cmds.getAttr(f"{shape}.form") > 0,
                "cvs": [cmds.xform(f"{shape}.cv[{i}]", q=True, t=True, os=True)
                        for i in range(cmds.getAttr(f"{shape}.degree") + cmds.getAttr(f"{shape}.spans"))]
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

    # ------------------------------------------------------------------
    # CORE FUNCTIONS
    # ------------------------------------------------------------------
    def create_logic(self):
        if not self.stored_data:
            cmds.warning("Memory is empty!")
            return
        cmds.undoInfo(openChunk=True, chunkName="Create Stored Control")
        try:
            new_ctrl = cmds.group(em=True, name="default_Ctrl")
            for i, s_data in enumerate(self.stored_data["shapes"]):
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
            self.center_pivot(new_ctrl)
            cmds.move(0, 0, 0, new_ctrl, rpr=True)
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
                        old_periodic = cmds.getAttr(f"{old_shape}.form") > 0
                        if old_periodic == s_data["periodic"]:
                            cmds.rebuildCurve(old_shape, ch=False, rpo=True, rt=0, s=s_data["spans"], d=s_data["degree"])
                            for j, pos in enumerate(s_data["cvs"]):
                                cmds.xform(f"{old_shape}.cv[{j}]", t=[p * scale_factor for p in pos], os=True)
                        else:
                            if s_data["periodic"]:
                                temp_trans = cmds.circle(ch=False)[0]
                                cmds.rebuildCurve(temp_trans, ch=False, rpo=True, rt=0, s=s_data["spans"], d=s_data["degree"])
                            else:
                                temp_trans = cmds.curve(d=s_data["degree"], p=s_data["cvs"])
                            for j, pos in enumerate(s_data["cvs"]):
                                cmds.xform(f"{temp_trans}.cv[{j}]", t=[p * scale_factor for p in pos], os=True)
                            self.copy_color(old_shape, temp_trans)
                            new_shape = cmds.listRelatives(temp_trans, shapes=True)[0]
                            cmds.parent(new_shape, target, r=True, s=True)
                            cmds.delete(old_shape)
                            cmds.delete(temp_trans)
            cmds.select(sel_list)
        except Exception as e:
            cmds.warning(f"Error changing control: {e}")
        finally:
            cmds.undoInfo(closeChunk=True)

    # ------------------------------------------------------------------
    # UI & FILES
    # ------------------------------------------------------------------
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
                if cmds.confirmDialog(title='Overwrite?', message='File exists. Overwrite?', button=['Yes', 'No']) == 'No': return
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
        cmds.button(label="SNAP & FINISH", height=40, backgroundColor=[0.25, 0.45, 0.35],
                    command=lambda x: self.finish_snapshot(win_name, editor, img_path))
        cmds.showWindow(win_name)
        cmds.modelEditor(editor, edit=True, camera="persp", activeView=True)
        cmds.modelEditor(editor, edit=True, setFocus=True)
        cmds.viewFit(all=True)

    def finish_snapshot(self, win_name, editor, img_path):
        cmds.refresh()
        cmds.playblast(editorPanelName=editor, completeFilename=img_path, format="image", compression="jpg",
                       viewer=False, showOrnaments=False, percent=100, widthHeight=[128, 128],
                       frame=cmds.currentTime(q=True))
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
            if item and item.widget():
                widget = item.widget()
                name = ""
                if isinstance(widget, ClickableRow):
                    for lbl in widget.findChildren(QtWidgets.QLabel):
                        if lbl.objectName() == "rowLabel":
                            name = lbl.text().lower()
                elif isinstance(widget, QtWidgets.QToolButton):
                    name = widget.text().lower()
                widget.setVisible(search_text in name)

    def refresh_library(self):
        path = cmds.optionVar(q=self.lib_var) if cmds.optionVar(exists=self.lib_var) else None
        self.library_container = QtWidgets.QWidget()
        self.library_container.setStyleSheet("background: transparent;")

        if self.is_grid_view:
            layout = FlowLayout(self.library_container, margin=5, hSpacing=5, vSpacing=5)
        else:
            layout = QtWidgets.QVBoxLayout(self.library_container)
            layout.setSpacing(3)
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
                    btn.setFixedSize(56, 68)
                    btn.setIconSize(QtCore.QSize(40, 40))
                    if has_icon: btn.setIcon(QtGui.QIcon(img_path))
                    btn.clicked.connect(lambda *a, fn=f: self.load_and_run(fn))
                    self._add_context_menu(btn, f)
                    layout.addWidget(btn)
                else:
                    row = ClickableRow()
                    row.setMinimumHeight(50)
                    row.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
                    row_layout = QtWidgets.QHBoxLayout(row)
                    row_layout.setContentsMargins(8, 5, 8, 5)
                    row_layout.setSpacing(10)

                    lbl_icon = QtWidgets.QLabel()
                    lbl_icon.setFixedSize(40, 40)
                    if has_icon:
                        lbl_icon.setPixmap(QtGui.QIcon(img_path).pixmap(40, 40))
                        lbl_icon.setScaledContents(True)
                    else:
                        lbl_icon.setText("No IMG")
                        lbl_icon.setStyleSheet("background-color: #1e1e24; color: #505060; font-size: 8px; border: 1px solid #32323c; border-radius: 3px;")
                        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)

                    lbl_text = QtWidgets.QLabel(f.replace(".json", ""))
                    lbl_text.setObjectName("rowLabel")
                    lbl_text.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
                    lbl_text.setStyleSheet("color: #d0d0d8; font-weight: bold; font-size: 12px; background: transparent; border: none;")

                    row_layout.addWidget(lbl_icon)
                    row_layout.addWidget(lbl_text)
                    row_layout.addStretch()

                    row.clicked.connect(lambda fn=f: self.load_and_run(fn))
                    self._add_context_menu(row, f)
                    layout.addWidget(row)

        self.scroll.setWidget(self.library_container)
        if self.search_bar.text():
            self.filter_library(self.search_bar.text())

    def _add_context_menu(self, widget, filename):
        widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(lambda pos, fn=filename: self.show_context_menu(pos, fn))

    def show_context_menu(self, pos, filename):
        menu = QtWidgets.QMenu()
        open_act   = menu.addAction("Open Folder")
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
            res = cmds.promptDialog(title='Rename', message="New Name:", text=filename.replace(".json", ""), button=['OK', 'Cancel'])
            if res == 'OK':
                new_n = cmds.promptDialog(q=True, text=True)
                if new_n:
                    os.rename(full_path, os.path.join(path, f"{new_n}.json"))
                    old_img = os.path.join(icons_dir, filename.replace(".json", ".jpg"))
                    if os.path.exists(old_img): os.rename(old_img, os.path.join(icons_dir, f"{new_n}.jpg"))
                    self.refresh_library()
        elif action == delete_act:
            if cmds.confirmDialog(title='Delete', message=f'Delete {filename}?', button=['Yes', 'No']) == 'Yes':
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


# -------------------------------------------------------------------------
# AUTO-ICON UPDATER
# -------------------------------------------------------------------------
def update_shelf_icon():
    import maya.mel as mel
    SCRIPT_NAME = "ControlShapeTool"
    ICON_FILE   = "ControlShapeTool_icon.png"
    try:
        current_shelf = mel.eval("tabLayout -q -selectTab $gShelfTopLevel")
        buttons = cmds.shelfLayout(current_shelf, q=True, childArray=True) or []
        for btn in buttons:
            cmd = cmds.shelfButton(btn, q=True, command=True) or ""
            if SCRIPT_NAME in cmd:
                current_img = cmds.shelfButton(btn, q=True, image=True)
                if "pythonFamily" in current_img or "commandButton" in current_img:
                    cmds.shelfButton(btn, e=True, image=ICON_FILE)
                    print(f"Icon updated for {SCRIPT_NAME}")
    except Exception as e:
        print(f"Could not auto-update icon: {e}")

# update_shelf_icon()


# -------------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------------
def main():
    if cmds.workspaceControl("CtrlShapeToolWindowWorkspaceControl", exists=True):
        cmds.deleteUI("CtrlShapeToolWindowWorkspaceControl", control=True)
    if cmds.window("CtrlShapeToolWindow", exists=True):
        cmds.deleteUI("CtrlShapeToolWindow")

    global my_tool
    my_tool = ControlShapeTool()
    if my_tool.setup_successful:
        my_tool.show(dockable=True)
    else:
        my_tool.deleteLater()

# main()
