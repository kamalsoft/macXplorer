"""Application entry point for the modular macOS File Explorer."""

import ctypes
import logging
import sys

from PyQt6.QtWidgets import QApplication

from core.branding import app_icon
from core.main_window import MacXplorer

LOGGER = logging.getLogger(__name__)


def set_macos_process_name(name: str) -> None:
    """Set the name macOS displays in the application menu for script launches."""
    if sys.platform != "darwin":
        return

    try:
        foundation = ctypes.CDLL(
            "/System/Library/Frameworks/Foundation.framework/Foundation"
        )
        objc = ctypes.CDLL("/usr/lib/libobjc.A.dylib")
        objc.objc_getClass.restype = ctypes.c_void_p
        objc.objc_getClass.argtypes = [ctypes.c_char_p]
        objc.sel_registerName.restype = ctypes.c_void_p
        objc.sel_registerName.argtypes = [ctypes.c_char_p]

        send_object = ctypes.CFUNCTYPE(
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        )(("objc_msgSend", objc))
        process_info_class = objc.objc_getClass(b"NSProcessInfo")
        if not process_info_class:
            raise RuntimeError("NSProcessInfo is unavailable")
        process_info = send_object(
            process_info_class, objc.sel_registerName(b"processInfo")
        )

        responds_to_selector = ctypes.CFUNCTYPE(
            ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        )(("objc_msgSend", objc))
        set_name_selector = objc.sel_registerName(b"setProcessName:")
        if not responds_to_selector(
            process_info,
            objc.sel_registerName(b"respondsToSelector:"),
            set_name_selector,
        ):
            raise RuntimeError("NSProcessInfo cannot set the process name")

        string_class = objc.objc_getClass(b"NSString")
        create_string = ctypes.CFUNCTYPE(
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p,
        )(("objc_msgSend", objc))
        native_name = create_string(
            string_class,
            objc.sel_registerName(b"stringWithUTF8String:"),
            name.encode("utf-8"),
        )
        set_process_name = ctypes.CFUNCTYPE(
            None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p
        )(("objc_msgSend", objc))
        set_process_name(process_info, set_name_selector, native_name)
    except (AttributeError, OSError, RuntimeError) as error:
        LOGGER.warning("Unable to set the macOS process name to %r: %s", name, error)


def main() -> int:
    set_macos_process_name("macXplorer")
    qt_argv = ["macXplorer", *sys.argv[1:]]
    app = QApplication(qt_argv)
    app.setApplicationName("macXplorer")
    app.setApplicationDisplayName("macXplorer")
    app.setOrganizationName("MacExplorer")
    app.setWindowIcon(app_icon())

    window = MacXplorer()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
