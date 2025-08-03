"""
Overlay window implementation for RaceMates.

The ``OverlayWindow`` class provides a small, transparent, always‑on‑top
window that lists any professional drivers in the current session.  It
subscribes to signals from the ``TelemetryListener`` to update its
contents and visibility.  The window can be moved by dragging with the
mouse; its position is persisted between sessions using
``config_manager``.
"""

from __future__ import annotations

from typing import List, Dict, Any

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .config_manager import get_window_position, set_window_position


class OverlayWindow(QWidget):
    """A frameless, draggable overlay listing professional drivers."""

    def __init__(self) -> None:
        super().__init__(
            flags=Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        # Transparent background and no window shadows
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus, True)
        self.setWindowFlag(Qt.NoDropShadowWindowHint, True)

        # Create UI elements
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        self.title_label = QLabel("Pro Drivers")
        self.title_label.setStyleSheet(
            "color: white; font-weight: bold; font-size: 12pt;"
        )
        layout.addWidget(self.title_label)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            "QListWidget { background-color: rgba(0, 0, 0, 160); color: white; border: none; } "
            "QListWidget::item { padding: 2px 4px; } "
            "QListWidget::item:selected { background-color: rgba(255, 255, 255, 50); }"
        )
        self.list_widget.setFrameShape(QListWidget.NoFrame)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)

        # Variables for dragging
        self._dragging = False
        self._drag_start_pos: QPoint | None = None

        # Restore previous position or default to top right
        self._apply_initial_position()

    def _apply_initial_position(self) -> None:
        """Position the overlay at the saved location or default to top right."""
        saved_x, saved_y = get_window_position()
        if saved_x is not None and saved_y is not None:
            self.move(saved_x, saved_y)
        else:
            # Default position: top-right corner with small margin
            screen = QApplication.primaryScreen()
            if screen:
                rect = screen.availableGeometry()
                # Use a small width estimate; adjust after first update
                w = 200
                x = rect.right() - w - 20
                y = rect.top() + 20
                self.move(x, y)

    def update_pro_drivers(self, pro_drivers: List[Dict[str, Any]]) -> None:
        """Update the list of professional drivers shown in the overlay."""
        self.list_widget.clear()
        if not pro_drivers:
            item = QListWidgetItem("No pro drivers in session")
            item.setForeground(Qt.gray)
            self.list_widget.addItem(item)
        else:
            for drv in pro_drivers:
                name = drv.get("Name", "")
                desc = drv.get("Description", "")
                car_num = drv.get("CarNumber", "")
                parts = []
                if car_num:
                    parts.append(car_num)
                if name:
                    parts.append(name)
                if desc:
                    parts.append(f"({desc})")
                text = " – ".join(parts[:2])  # join car number and name with dash
                if desc:
                    # Append description separated by space
                    text = f"{text} {desc}"
                item = QListWidgetItem(text)
                item.setForeground(Qt.yellow)
                self.list_widget.addItem(item)
        # Resize to fit content roughly
        self.adjustSize()

    # Dragging behavior
    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging and self._drag_start_pos is not None:
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            self.move(new_pos)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self._drag_start_pos = None
            # Persist the new position
            x = self.x()
            y = self.y()
            set_window_position(x, y)
            event.accept()
        else:
            super().mouseReleaseEvent(event)