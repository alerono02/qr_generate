import abc
import csv
import tkinter as tk
from tkinter import colorchooser
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Any, Union

import qrcode
from PIL import ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer
from qrcode.main import QRCode

if TYPE_CHECKING:
    from qrcode.image.base import BaseImage
    from qrcode.main import ActiveWithNeighbors, QRCode


class BaseEyeDrawer(abc.ABC):
    needs_processing = True
    needs_neighbors = False
    factory: "StyledPilImage2"

    def initialize(self, img: "BaseImage") -> None:
        self.img = img

    def draw(self):
        (nw_eye_top, _), (_, nw_eye_bottom) = (
            self.factory.pixel_box(0, 0),
            self.factory.pixel_box(6, 6),
        )
        (nw_eyeball_top, _), (_, nw_eyeball_bottom) = (
            self.factory.pixel_box(2, 2),
            self.factory.pixel_box(4, 4),
        )
        self.draw_nw_eye((nw_eye_top, nw_eye_bottom))
        self.draw_nw_eyeball((nw_eyeball_top, nw_eyeball_bottom))

        (ne_eye_top, _), (_, ne_eye_bottom) = (
            self.factory.pixel_box(0, self.factory.width - 7),
            self.factory.pixel_box(6, self.factory.width - 1),
        )
        (ne_eyeball_top, _), (_, ne_eyeball_bottom) = (
            self.factory.pixel_box(2, self.factory.width - 5),
            self.factory.pixel_box(4, self.factory.width - 3),
        )
        self.draw_ne_eye((ne_eye_top, ne_eye_bottom))
        self.draw_ne_eyeball((ne_eyeball_top, ne_eyeball_bottom))

        (sw_eye_top, _), (_, sw_eye_bottom) = (
            self.factory.pixel_box(self.factory.width - 7, 0),
            self.factory.pixel_box(self.factory.width - 1, 6),
        )
        (sw_eyeball_top, _), (_, sw_eyeball_bottom) = (
            self.factory.pixel_box(self.factory.width - 5, 2),
            self.factory.pixel_box(self.factory.width - 3, 4),
        )
        self.draw_sw_eye((sw_eye_top, sw_eye_bottom))
        self.draw_sw_eyeball((sw_eyeball_top, sw_eyeball_bottom))

    @abc.abstractmethod
    def draw_nw_eye(self, position): ...

    @abc.abstractmethod
    def draw_nw_eyeball(self, position): ...

    @abc.abstractmethod
    def draw_ne_eye(self, position): ...

    @abc.abstractmethod
    def draw_ne_eyeball(self, position): ...

    @abc.abstractmethod
    def draw_sw_eye(self, position): ...

    @abc.abstractmethod
    def draw_sw_eyeball(self, position): ...


class CustomEyeDrawer(BaseEyeDrawer):
    def draw_nw_eye(self, position):
        draw = ImageDraw.Draw(self.img)
        draw.rounded_rectangle(
            position,
            fill=None,
            width=self.factory.box_size,
            outline="black",
            radius=self.factory.box_size * 2,
            corners=[True, True, False, True],
        )

    def draw_nw_eyeball(self, position):
        self.draw_hamburger(position)

    def draw_ne_eye(self, position):
        draw = ImageDraw.Draw(self.img)
        draw.rounded_rectangle(
            position,
            fill=None,
            width=self.factory.box_size,
            outline="black",
            radius=self.factory.box_size * 2,
            corners=[True, True, True, False],
        )

    def draw_ne_eyeball(self, position):
        self.draw_hamburger(position)

    def draw_sw_eye(self, position):
        draw = ImageDraw.Draw(self.img)
        draw.rounded_rectangle(
            position,
            fill=None,
            width=self.factory.box_size,
            outline="black",
            radius=self.factory.box_size * 2,
            corners=[True, False, True, True],
        )

    def draw_sw_eyeball(self, position):
        self.draw_hamburger(position)

    def draw_hamburger(self, position):
        draw = ImageDraw.Draw(self.img)
        x1, y1 = position[0]
        x2, y2 = position[1]
        bar_height = (y2 - y1) // 5 + 15  # Высота полоски
        gap = bar_height - 30  # Промежуток между полосками

        for i in range(3):
            y_start = y1 + i * (bar_height + gap)
            y_end = y_start + bar_height
            draw.rounded_rectangle([x1, y_start, x2, y_end], radius=self.factory.box_size, fill="black", outline="black")


class StyledPilImage2(StyledPilImage):
    def drawrect_context(self, row: int, col: int, qr: QRCode[Any]):
        box = self.pixel_box(row, col)
        if self.is_eye(row, col):
            drawer = self.eye_drawer
            if getattr(self.eye_drawer, "needs_processing", False):
                return
        else:
            drawer = self.module_drawer

        is_active: Union[bool, ActiveWithNeighbors] = (
            qr.active_with_neighbors(row, col)
            if drawer.needs_neighbors
            else bool(qr.modules[row][col])
        )

        drawer.drawrect(box, is_active)

    def process(self) -> None:
        if getattr(self.eye_drawer, "needs_processing", False):
            self.eye_drawer.factory = self
            self.eye_drawer.draw()
        super().process()


from tkinter import colorchooser  # Добавьте этот импорт

class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")

        # Цвета по умолчанию
        self.front_color = (190, 232, 32)
        self.back_color = (1, 68, 78)
        self.save_directory = None  # Директория для сохранения файлов

        # Поле для ввода URL
        self.url_label = tk.Label(root, text="Base URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        # Поле для выбора маркета
        self.market_label = tk.Label(root, text="Номер маркета:")
        self.market_label.grid(row=1, column=0, padx=10, pady=10)
        self.market_entry = tk.Entry(root, width=50)
        self.market_entry.grid(row=1, column=1, padx=10, pady=10)
        self.market_label_2 = tk.Label(root, text="(1 - Усачевский, 3 - Ленинский, 4 - на Маросейке, 62 - Gremm)")
        self.market_label_2.grid(row=2, column=0,columnspan=2, padx=10, pady=10)

        # Поле для ввода количества столов
        self.tables_label = tk.Label(root, text="Количество столов(или номера столов через ;):")
        self.tables_label.grid(row=3, column=0, padx=10, pady=10)
        self.tables_entry = tk.Entry(root, width=50)
        self.tables_entry.grid(row=3, column=1, padx=10, pady=10)

        # Выбор цвета точек
        self.color_button = tk.Button(root, text="Выбрать цвет точек", command=self.choose_front_color)
        self.color_button.grid(row=4, column=0, padx=10, pady=10)
        self.color_preview = tk.Label(root, text="    ", bg="#%02x%02x%02x" % self.front_color)
        self.color_preview.grid(row=4, column=1, padx=10, pady=10)

        # Выбор цвета фона
        self.bg_color_button = tk.Button(root, text="Выбрать цвет фона", command=self.choose_back_color)
        self.bg_color_button.grid(row=5, column=0, padx=10, pady=10)
        self.bg_color_preview = tk.Label(root, text="    ", bg="#%02x%02x%02x" % self.back_color)
        self.bg_color_preview.grid(row=5, column=1, padx=10, pady=10)

        # Выбор директории для сохранения
        self.save_dir_label = tk.Label(root, text="Выберите директорию для сохранения:")
        self.save_dir_label.grid(row=6, column=0, padx=10, pady=10)
        self.save_dir_button = tk.Button(root, text="Обзор", command=self.choose_save_directory)
        self.save_dir_button.grid(row=6, column=1, padx=10, pady=10)

        # Кнопка генерации
        self.generate_button = tk.Button(root, text="Сгенерировать QR-коды", command=self.generate_qr_codes)
        self.generate_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    def choose_save_directory(self):
        """Выбор директории для сохранения файлов"""
        self.save_directory = filedialog.askdirectory(title="Выберите директорию для сохранения")
        if self.save_directory:
            messagebox.showinfo("Директория выбрана", f"Файлы будут сохранены в: {self.save_directory}")

    def choose_front_color(self):
        """Выбор цвета точек"""
        color = colorchooser.askcolor(title="Выберите цвет точек")
        if color[1]:
            self.front_color = tuple(int(x) for x in color[0])
            self.color_preview.config(bg=color[1])

    def choose_back_color(self):
        """Выбор цвета фона"""
        color = colorchooser.askcolor(title="Выберите цвет фона")
        if color[1]:
            self.back_color = tuple(int(x) for x in color[0])
            self.bg_color_preview.config(bg=color[1])

    def generate_qr_codes(self):
        """Генерация QR-кодов"""
        base_url = self.url_entry.get().strip()
        market = self.market_entry.get().strip()
        tables_input = self.tables_entry.get().strip()

        if not base_url:
            messagebox.showerror("Ошибка", "Введите Base URL")
            return

        if not market:
            messagebox.showerror("Ошибка", "Введите номер маркета")
            return

        if not tables_input:
            messagebox.showerror("Ошибка", "Введите количество столов или номера столов через ';'")
            return

        if not self.save_directory:
            messagebox.showerror("Ошибка", "Выберите директорию для сохранения")
            return

        try:
            # Если ввод содержит ';', разбиваем на отдельные номера столов
            if ";" in tables_input:
                table_numbers = [num.strip() for num in tables_input.split(";") if num.strip()]
                # Проверяем, что все значения — числа
                if not all(num.isdigit() for num in table_numbers):
                    messagebox.showerror("Ошибка", "Номера столов должны быть числами")
                    return
                table_numbers = [int(num) for num in table_numbers]
            else:
                # Если ввод — одно число, генерируем диапазон
                if not tables_input.isdigit() or int(tables_input) <= 0:
                    messagebox.showerror("Ошибка", "Количество столов должно быть положительным числом")
                    return
                table_numbers = range(1, int(tables_input) + 1)

            for table_number in table_numbers:
                # Форматируем номер стола с ведущими нулями (001, 011, 200 и т.д.)
                formatted_table_number = str(table_number).zfill(3)
                link = f"https://{base_url}/market/{market}?deliveryType=MarketTable&table={formatted_table_number}"
                qr = QRCode(version=5, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=40)
                qr.add_data(link)

                img = qr.make_image(
                    image_factory=StyledPilImage2,
                    module_drawer=CircleModuleDrawer(),
                    eye_drawer=CustomEyeDrawer(),
                    color_mask=SolidFillColorMask(back_color=self.back_color, front_color=self.front_color),
                )
                # Сохраняем файл в формате market{market}table{formatted_table_number}.png
                img.save(f"{self.save_directory}/{market}{formatted_table_number}.png")

            messagebox.showinfo("Успех", f"QR-коды успешно сгенерированы и сохранены в {self.save_directory}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()