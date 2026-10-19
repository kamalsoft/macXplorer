import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QDir, QMimeData, QSettings, QUrl, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLabel

from core.branding import AboutDialog, app_asset_path
from core.main_window import MacXplorer
from core.theme import (
    ADVANCED_THEME_CATALOG,
    THEME_OPTIONS,
    system_theme_name,
    theme_stylesheet,
)
from plugins.diff_plugin import FileDiffDialog, FolderCompareDialog
from plugins.settings_plugin import SettingsDialog


class PluginManagerSmokeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def test_builtin_plugins_load_and_register_their_views(self):
        window = MacXplorer()
        try:
            self.assertEqual(window.windowTitle(), "macXplorer")
            self.assertEqual(
                QApplication.applicationDisplayName(),
                "macXplorer",
            )
            self.assertFalse(window.windowIcon().isNull())
            self.assertEqual(
                set(window.plugin_manager.plugins),
                {"diff", "preview", "settings", "workspace"},
            )
            self.assertEqual(window.splitter.count(), 2)
            self.assertEqual(window.workspaces.count(), 1)
            self.assertEqual(window.current_workspace.splitter.count(), 2)
            self.assertIn(
                "Compare Folders",
                [action.text() for action in window.menus["Tools"].actions()],
            )
            menu_titles = [action.text() for action in window.menuBar().actions()]
            self.assertEqual(len(menu_titles), len(set(menu_titles)))
            self.assertTrue(window.left_pane.tree.dragEnabled())
            self.assertTrue(window.left_pane.tree.acceptDrops())
            self.assertIn(
                "macXplorer Settings…",
                [action.text() for action in window.menus["File"].actions()],
            )
            self.assertIn(
                "About macXplorer",
                [action.text() for action in window.help_menu.actions()],
            )
            self.assertEqual(
                window.about_action.menuRole(), QAction.MenuRole.AboutRole
            )
            self.assertFalse(window.plugin_manager.errors)
        finally:
            window.close()

    def test_about_dialog_uses_product_brand_and_development_status(self):
        self.assertTrue(app_asset_path("macXplorer.png").is_file())
        self.assertTrue(app_asset_path("macXplorer.svg").is_file())
        dialog = AboutDialog()
        try:
            self.assertEqual(dialog.windowTitle(), "About macXplorer")
            self.assertFalse(dialog.windowIcon().isNull())
            self.assertEqual(
                dialog.findChild(QLabel, "brandTitle").text(),
                "macXplorer",
            )
            self.assertEqual(
                dialog.findChild(QLabel, "brandStatus").text(),
                "DEVELOPMENT BUILD",
            )
            self.assertEqual(
                dialog.findChild(QLabel, "brandAttribution").text(),
                "A NanovionLabs application",
            )
        finally:
            dialog.close()

    def test_app_assets_resolve_from_macos_bundle_resources(self):
        with tempfile.TemporaryDirectory() as directory:
            contents = Path(directory) / "macXplorer.app" / "Contents"
            frameworks = contents / "Frameworks"
            executable = contents / "MacOS" / "macXplorer"
            packaged_asset = contents / "Resources" / "assets" / "macXplorer.png"
            frameworks.mkdir(parents=True)
            executable.parent.mkdir()
            packaged_asset.parent.mkdir(parents=True)
            packaged_asset.write_bytes(b"test image")
            with (
                patch("core.branding.sys._MEIPASS", str(frameworks), create=True),
                patch("core.branding.sys.executable", str(executable)),
            ):
                self.assertEqual(
                    app_asset_path("macXplorer.png"), packaged_asset.resolve()
                )

    def test_preview_plugin_shows_text_and_metadata(self):
        window = MacXplorer()
        try:
            preview = window.plugin_manager.get_plugin("preview").preview_pane
            with tempfile.TemporaryDirectory() as directory:
                text_path = Path(directory) / "sample.txt"
                text_path.write_text("preview content", encoding="utf-8")
                preview.update_preview(str(text_path))
                self.assertEqual(preview.stack.currentWidget(), preview.text_preview)
                self.assertEqual(preview.text_preview.toPlainText(), "preview content")

                binary_path = Path(directory) / "sample.bin"
                binary_path.write_bytes(b"\x00\x01")
                preview.update_preview(str(binary_path))
                self.assertEqual(preview.stack.currentWidget(), preview.info_label)
                self.assertIn("Permissions", preview.info_label.text())
        finally:
            window.close()

    def test_diff_dialogs_compare_files_and_nested_folders(self):
        window = MacXplorer()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                left = root / "left"
                right = root / "right"
                (left / "nested").mkdir(parents=True)
                (right / "nested").mkdir(parents=True)
                left_file = left / "nested" / "compare.txt"
                right_file = right / "nested" / "compare.txt"
                left_file.write_text("left version\n", encoding="utf-8")
                right_file.write_text("right version\n", encoding="utf-8")

                folder_dialog = FolderCompareDialog(str(left), str(right), window)
                rows = [
                    (
                        folder_dialog.table.item(row, 0).text(),
                        folder_dialog.table.item(row, 1).text(),
                    )
                    for row in range(folder_dialog.table.rowCount())
                ]
                self.assertIn(("nested/compare.txt", "Different"), rows)

                file_dialog = FileDiffDialog(str(left_file), str(right_file), window)
                diff = file_dialog.diff_text.toPlainText()
                self.assertIn("-left version", diff)
                self.assertIn("+right version", diff)
                folder_dialog.close()
                file_dialog.close()
        finally:
            window.close()

    def test_workspace_plugin_toggles_the_right_pane(self):
        window = MacXplorer()
        try:
            window.current_workspace.set_dual_pane(True)
            workspace = window.plugin_manager.get_plugin("workspace")
            workspace.toggle_dual_pane()
            self.assertFalse(window.dual_pane_active)
            self.assertTrue(window.right_pane.isHidden())
            workspace.toggle_dual_pane()
            self.assertTrue(window.dual_pane_active)
            self.assertFalse(window.right_pane.isHidden())
        finally:
            window.close()

    def test_shortcuts_work_from_focused_file_pane(self):
        window = MacXplorer()
        try:
            window.show()
            window.left_pane.tree.setFocus()
            self.application.processEvents()

            QTest.keyClick(
                window.left_pane.tree,
                Qt.Key.Key_T,
                Qt.KeyboardModifier.ControlModifier,
            )
            self.application.processEvents()
            self.assertEqual(window.workspaces.count(), 2)

            QTest.keyClick(
                window.left_pane.tree,
                Qt.Key.Key_L,
                Qt.KeyboardModifier.ControlModifier,
            )
            self.application.processEvents()
            self.assertTrue(window.left_pane.path_bar.hasFocus())

            workspace_plugin = window.plugin_manager.get_plugin("workspace")
            workspace_plugin.set_dual_pane(False)
            window.left_pane.tree.setFocus()
            QTest.keyClick(
                window.left_pane.tree,
                Qt.Key.Key_D,
                Qt.KeyboardModifier.ControlModifier,
            )
            self.application.processEvents()
            self.assertTrue(window.dual_pane_active)

            QTest.keyClick(
                window.left_pane.tree,
                Qt.Key.Key_D,
                Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier,
            )
            self.application.processEvents()
            self.assertFalse(window.dual_pane_active)
        finally:
            window.close()

    def test_tabs_keep_navigation_and_view_state_independent(self):
        window = MacXplorer()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                left = root / "left"
                child = left / "child"
                right = root / "right"
                child.mkdir(parents=True)
                right.mkdir()

                first_tab = window.current_workspace
                first_tab.left_pane.navigate_to(str(left))
                first_tab.left_pane.navigate_to(str(child))
                first_tab.left_pane.navigate_back()
                self.assertEqual(
                    Path(first_tab.left_pane.path_bar.text()).resolve(), left.resolve()
                )
                self.assertEqual(first_tab.left_pane.current_path, left.resolve())
                first_tab.left_pane.set_view_mode("icons")

                window.new_tab(right)
                self.assertEqual(window.workspaces.count(), 2)
                self.assertEqual(window.left_pane.path_bar.text(), str(right))
                self.assertIsNot(window.current_workspace, first_tab)
                window.workspaces.setCurrentWidget(first_tab)
                self.assertEqual(
                    Path(window.left_pane.path_bar.text()).resolve(), left.resolve()
                )
                self.assertEqual(first_tab.left_pane.views.currentWidget(), first_tab.left_pane.list_view)
        finally:
            window.close()

    def test_paste_supports_copy_cut_and_safe_zip_extraction(self):
        window = MacXplorer()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = root / "source.txt"
                source.write_text("hello", encoding="utf-8")
                target = root / "destination"
                target.mkdir()
                window.left_pane.navigate_to(str(target))

                window.clipboard_paths = [source]
                window.clipboard_operation = "copy"
                window.paste_item()
                copied = target / source.name
                self.assertEqual(copied.read_text(encoding="utf-8"), "hello")
                copied.unlink()

                window.clipboard_operation = "cut"
                window.paste_item()
                self.assertFalse(source.exists())
                self.assertTrue(copied.exists())
                self.assertEqual(window.clipboard_paths, [])

                external_source = root / "external.txt"
                external_source.write_text("from Finder", encoding="utf-8")
                mime_data = QMimeData()
                mime_data.setUrls([QUrl.fromLocalFile(str(external_source))])
                QApplication.clipboard().setMimeData(mime_data)
                window.clipboard_paths = []
                window.paste_item()
                self.assertEqual(
                    (target / external_source.name).read_text(encoding="utf-8"),
                    "from Finder",
                )

                bad_archive = root / "unsafe.zip"
                with zipfile.ZipFile(bad_archive, "w") as archive:
                    archive.writestr("../outside.txt", "unsafe")
                extraction_dir = root / "extracted"
                with self.assertRaises(ValueError):
                    MacXplorer._extract_zip_to(bad_archive, extraction_dir)
                self.assertFalse(extraction_dir.exists())
                self.assertFalse((root / "outside.txt").exists())

                photo_folder = root / "photos"
                photo_folder.mkdir()
                (photo_folder / "image.txt").write_text("image", encoding="utf-8")
                valid_archive = root / "photos.zip"
                MacXplorer._create_zip([photo_folder], root, valid_archive)
                valid_destination = root / "valid-extraction"
                MacXplorer._extract_zip_to(valid_archive, valid_destination)
                self.assertEqual(
                    (valid_destination / "photos" / "image.txt").read_text(
                        encoding="utf-8"
                    ),
                    "image",
                )
                with self.assertRaises(ValueError):
                    MacXplorer._create_zip(
                        [photo_folder], root, photo_folder / "nested.zip"
                    )
                self.assertFalse((photo_folder / "nested.zip").exists())
        finally:
            window.close()

    def test_image_browsing_uses_file_model_filters(self):
        window = MacXplorer()
        try:
            pane = window.left_pane
            pane.set_images_only(True)
            self.assertTrue(pane.images_only)
            self.assertIn("*.jpg", pane.source_model.nameFilters())
            self.assertFalse(pane.source_model.nameFilterDisables())
            pane.set_images_only(False)
            self.assertEqual(pane.source_model.nameFilters(), [])
        finally:
            window.close()

    def test_settings_dialog_persists_and_applies_explorer_preferences(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            left_start = root / "left-start"
            right_start = root / "right-start"
            left_start.mkdir()
            right_start.mkdir()
            settings = QSettings(str(root / "settings.ini"), QSettings.Format.IniFormat)
            window = MacXplorer(settings=settings)
            try:
                dialog = SettingsDialog(settings, window)
                dialog.left_path_input.setText(str(left_start))
                dialog.right_path_input.setText(str(right_start))
                dialog.show_hidden.setChecked(True)
                dialog.confirm_delete.setChecked(False)
                dialog.show_preview.setChecked(False)
                dialog.dual_pane.setChecked(False)
                dialog.favorites_list.addItem(str(right_start))
                dialog._save_and_accept()
                self.assertEqual(dialog.result(), dialog.DialogCode.Accepted)

                window.apply_settings()
                self.assertEqual(
                    window.left_pane.path_bar.text(), str(left_start.resolve())
                )
                self.assertEqual(
                    window.right_pane.path_bar.text(), str(right_start.resolve())
                )
                self.assertTrue(
                    window.left_pane.source_model.filter() & QDir.Filter.Hidden
                )
                self.assertFalse(window.dual_pane_active)
                self.assertTrue(window.right_pane.isHidden())
                preview = window.plugin_manager.get_plugin("preview").preview_pane
                self.assertTrue(preview.isHidden())

                settings.sync()
                self.assertFalse(settings.value("files/confirmDelete", True, type=bool))
                self.assertEqual(
                    settings.value("workspace/favorites"), [str(right_start)]
                )
            finally:
                window.close()

    def test_cancelled_settings_dialog_does_not_persist_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = QSettings(
                str(Path(directory) / "settings.ini"), QSettings.Format.IniFormat
            )
            dialog = SettingsDialog(settings)
            dialog.show_hidden.setChecked(True)
            dialog.reject()
            self.assertFalse(settings.contains("files/showHidden"))

    def test_appearance_setting_supports_system_light_and_dark(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = QSettings(
                str(Path(directory) / "settings.ini"), QSettings.Format.IniFormat
            )
            window = MacXplorer(settings=settings)
            try:
                application = QApplication.instance()
                self.assertEqual(
                    application.styleSheet(),
                    theme_stylesheet(system_theme_name(application)),
                )

                dialog = SettingsDialog(settings, window)
                self.assertEqual(dialog.theme_selector.currentData(), "system")
                dialog.theme_selector.setCurrentIndex(
                    dialog.theme_selector.findData("light")
                )
                dialog._save_and_accept()
                window.apply_settings()
                self.assertEqual(settings.value("appearance/theme"), "light")
                self.assertEqual(application.styleSheet(), theme_stylesheet("light"))

                dialog = SettingsDialog(settings, window)
                dialog.theme_selector.setCurrentIndex(
                    dialog.theme_selector.findData("dark")
                )
                dialog._save_and_accept()
                window.apply_settings()
                self.assertEqual(settings.value("appearance/theme"), "dark")
                self.assertEqual(application.styleSheet(), theme_stylesheet("dark"))
            finally:
                window.close()

    def test_appearance_presets_preview_before_saving(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = QSettings(
                str(Path(directory) / "settings.ini"), QSettings.Format.IniFormat
            )
            window = MacXplorer(settings=settings)
            try:
                application = QApplication.instance()
                original_stylesheet = application.styleSheet()
                dialog = SettingsDialog(settings, window)
                available_ids = [
                    dialog.theme_selector.itemData(index)
                    for index in range(dialog.theme_selector.count())
                ]
                self.assertEqual(
                    available_ids, [theme_id for _, theme_id in THEME_OPTIONS]
                )
                custom_stylesheets = {
                    theme_stylesheet(theme_id)
                    for _, theme_id in THEME_OPTIONS
                    if theme_id != "system"
                }
                self.assertEqual(len(custom_stylesheets), len(THEME_OPTIONS) - 1)

                dialog.theme_selector.setCurrentIndex(
                    dialog.theme_selector.findData("ocean")
                )
                self.assertIn(
                    "background-color: #111c2b",
                    dialog.theme_preview.styleSheet(),
                )
                self.assertEqual(application.styleSheet(), original_stylesheet)
                self.assertEqual(settings.value("appearance/theme", "system"), "system")

                dialog.theme_selector.setCurrentIndex(
                    dialog.theme_selector.findData("forest")
                )
                self.assertIn(
                    "background-color: #17211c",
                    dialog.theme_preview.styleSheet(),
                )
                self.assertEqual(application.styleSheet(), original_stylesheet)
                dialog.reject()
                self.assertEqual(settings.value("appearance/theme", "system"), "system")
            finally:
                window.close()

    def test_theme_tab_browses_advanced_catalog_without_applying_concepts(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = QSettings(
                str(Path(directory) / "settings.ini"), QSettings.Format.IniFormat
            )
            window = MacXplorer(settings=settings)
            try:
                dialog = SettingsDialog(settings, window)
                self.assertEqual(
                    [
                        dialog.settings_tabs.tabText(index)
                        for index in range(dialog.settings_tabs.count())
                    ],
                    ["General", "Themes"],
                )
                self.assertEqual(
                    dialog.themes_content_layout.itemAt(1).widget().title(),
                    "Advanced UI theme catalog",
                )
                self.assertEqual(
                    [
                        dialog.advanced_theme_list.item(index).text()
                        for index in range(dialog.advanced_theme_list.count())
                    ],
                    [theme.name for theme in ADVANCED_THEME_CATALOG],
                )

                dialog.theme_search.setText("blur")
                visible_names = [
                    dialog.advanced_theme_list.item(index).text()
                    for index in range(dialog.advanced_theme_list.count())
                    if not dialog.advanced_theme_list.item(index).isHidden()
                ]
                self.assertEqual(visible_names, ["Glassmorphism", "Frosted Glass"])
                self.assertIn("Informational only", dialog.theme_detail_status.text())

                dialog.theme_search.clear()
                motion_row = next(
                    index
                    for index in range(dialog.advanced_theme_list.count())
                    if dialog.advanced_theme_list.item(index).text() == "Motion-First UI"
                )
                dialog.advanced_theme_list.setCurrentRow(motion_row)
                self.assertIn("Motion-First UI", dialog.theme_detail_name.text())
                self.assertIn(
                    "motion system", dialog.theme_detail_note.text().casefold()
                )
                self.assertEqual(settings.value("appearance/theme", "system"), "system")
                self.assertEqual(
                    QApplication.instance().styleSheet(),
                    theme_stylesheet(system_theme_name(QApplication.instance())),
                )
            finally:
                window.close()

    def test_accessibility_appearance_options_persist_and_apply(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = QSettings(
                str(Path(directory) / "settings.ini"), QSettings.Format.IniFormat
            )
            window = MacXplorer(settings=settings)
            try:
                application = QApplication.instance()
                dialog = SettingsDialog(settings, window)
                dialog.theme_selector.setCurrentIndex(
                    dialog.theme_selector.findData("light")
                )
                dialog.text_size_selector.setCurrentIndex(
                    dialog.text_size_selector.findData("extra_large")
                )
                dialog.density_selector.setCurrentIndex(
                    dialog.density_selector.findData("compact")
                )
                dialog.contrast_selector.setCurrentIndex(
                    dialog.contrast_selector.findData("high")
                )
                dialog.color_treatment_selector.setCurrentIndex(
                    dialog.color_treatment_selector.findData("colorblind")
                )
                preview_style = dialog.theme_preview.styleSheet()
                self.assertIn("font-size: 18px", preview_style)
                self.assertIn("padding: 2px", preview_style)
                self.assertIn("border: 3px solid", preview_style)
                self.assertIn("#a64b00", preview_style)
                self.assertNotEqual(application.styleSheet(), preview_style)

                dialog._save_and_accept()
                window.apply_settings()
                self.assertEqual(settings.value("appearance/textSize"), "extra_large")
                self.assertEqual(settings.value("appearance/density"), "compact")
                self.assertEqual(settings.value("appearance/contrast"), "high")
                self.assertEqual(settings.value("appearance/colorTreatment"), "colorblind")
                self.assertEqual(
                    application.styleSheet(),
                    theme_stylesheet(
                        "light",
                        text_size="extra_large",
                        density="compact",
                        contrast="high",
                        color_treatment="colorblind",
                    ),
                )
            finally:
                window.close()


if __name__ == "__main__":
    unittest.main()
