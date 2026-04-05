from __future__ import annotations

import argparse
import datetime as dt
import io
import platform
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont, ImageTk


WINDOW_TITLE = "兑换记录图片生成器"
CANVAS_SIZE = (1280, 900)
PREVIEW_SIZE = (880, 620)
BACKGROUND_COLOR = "#F7F7F9"
HEADER_BG = "#1F296A"
HEADER_TEXT = "#E5E6EB"
PRIMARY_TEXT = "#1D2330"
SECONDARY_TEXT = "#A9AFBF"
LINE_COLOR = "#E7EAF1"
NOTE_TEXT = "#545C6C"


@dataclass(slots=True)
class RewardRecord:
    device_type: str
    login_type: str
    game_name: str
    prize_name: str
    exchange_status: str
    exchange_time: str
    page_title: str = "兑换记录"
    note_title: str = "领奖说明"
    note_body: str = "游戏奖励直接发放至游戏邮箱，请在游戏中查收。奖励发放存在延迟，请耐心等待。"


def default_record() -> RewardRecord:
    return RewardRecord(
        device_type="安卓",
        login_type="Q",
        game_name="呆小莹唠",
        prize_name="套装·浪漫波比",
        exchange_status="已发放",
        exchange_time=dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


def candidate_font_paths() -> list[Path]:
    system = platform.system()
    candidates: list[str] = []
    if system == "Windows":
        candidates = [
            r"C:\Windows\Fonts\msyh.ttc",
            r"C:\Windows\Fonts\msyhbd.ttc",
            r"C:\Windows\Fonts\simhei.ttf",
            r"C:\Windows\Fonts\simsun.ttc",
            r"C:\Windows\Fonts\Deng.ttf",
        ]
    elif system == "Darwin":
        candidates = [
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    return [Path(path) for path in candidates]


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in candidate_font_paths():
        if path.exists():
            return ImageFont.truetype(path.as_posix(), size=size)
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    if not text:
        return [""]

    lines: list[str] = []
    current = ""
    for char in text:
        candidate = f"{current}{char}"
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines


def format_exchange_time(exchange_time: str) -> str:
    text = exchange_time.strip()
    if " " in text:
        date_part, time_part = text.split(" ", 1)
        return f"{date_part}\n{time_part}"
    return text


def build_header_title(record: RewardRecord) -> str:
    device_map = {"安卓": "安卓(android)", "苹果": "苹果(ios)"}
    login_map = {"Q": "手Q", "微信": "微信"}
    device_text = device_map.get(record.device_type.strip(), record.device_type.strip() or "安卓(android)")
    login_text = login_map.get(record.login_type.strip(), record.login_type.strip() or "手Q")
    game_name = record.game_name.strip() or "输入游戏名字"
    return f"{device_text}-{login_text}-{game_name}"


def draw_centered_multiline(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    top_y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    line_spacing: int = 14,
) -> None:
    lines = text.splitlines() or [text]
    if len(lines) == 1:
        draw.text((center_x, top_y), lines[0], font=font, fill=fill, anchor="ma")
        return

    line_height = draw.textbbox((0, 0), "国", font=font)[3]
    for index, line in enumerate(lines):
        y = top_y + index * (line_height + line_spacing)
        draw.text((center_x, y), line, font=font, fill=fill, anchor="ma")


def create_reward_image(record: RewardRecord, size: tuple[int, int] = CANVAS_SIZE) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    header_font = load_font(48)
    page_title_font = load_font(54)
    table_header_font = load_font(30)
    table_value_font = load_font(34)
    note_title_font = load_font(30)
    note_body_font = load_font(24)
    close_font = load_font(36)
    top_action_font = load_font(36)

    draw.rectangle((0, 0, width, 92), fill=HEADER_BG)
    draw.text(
        (60, 46),
        build_header_title(record),
        font=header_font,
        fill=HEADER_TEXT,
        anchor="lm",
    )
    draw.text((width - 290, 46), "[更换绑定角色]", font=top_action_font, fill=HEADER_TEXT, anchor="mm")
    draw.text((width - 112, 46), "[刷新]", font=top_action_font, fill=HEADER_TEXT, anchor="mm")

    draw.text((width - 56, 148), "×", font=close_font, fill="#B8BDC8", anchor="mm")

    draw.text((width // 2, 170), record.page_title, font=page_title_font, fill=PRIMARY_TEXT, anchor="mm")

    table_left = 150
    table_right = width - 150
    table_width = table_right - table_left
    column_widths = [int(table_width * 0.42), int(table_width * 0.24), int(table_width * 0.34)]
    column_centers = [
        table_left + column_widths[0] // 2,
        table_left + column_widths[0] + column_widths[1] // 2,
        table_left + column_widths[0] + column_widths[1] + column_widths[2] // 2,
    ]

    header_y = 300
    header_line_y = 360
    row_top_y = 408
    row_bottom_y = 565

    draw.line((table_left, header_line_y, table_right, header_line_y), fill=LINE_COLOR, width=3)
    draw.line((table_left, row_bottom_y, table_right, row_bottom_y), fill=LINE_COLOR, width=3)

    headers = ["奖品名称", "兑换状态", "兑换时间"]
    for center_x, text in zip(column_centers, headers, strict=True):
        draw.text((center_x, header_y), text, font=table_header_font, fill=SECONDARY_TEXT, anchor="mm")

    prize_max_width = column_widths[0] - 50
    prize_lines = wrap_text(draw, record.prize_name, table_value_font, prize_max_width)[:2]
    prize_text = "\n".join(prize_lines)
    status_text = record.exchange_status.strip()
    time_text = format_exchange_time(record.exchange_time)

    draw_centered_multiline(
        draw,
        column_centers[0],
        row_top_y,
        prize_text,
        table_value_font,
        PRIMARY_TEXT,
    )
    draw_centered_multiline(
        draw,
        column_centers[1],
        row_top_y,
        status_text,
        table_value_font,
        PRIMARY_TEXT,
    )
    draw_centered_multiline(
        draw,
        column_centers[2],
        row_top_y,
        time_text,
        table_value_font,
        PRIMARY_TEXT,
    )

    note_top_y = 690
    draw.text((table_left, note_top_y), record.note_title, font=note_title_font, fill=PRIMARY_TEXT, anchor="la")
    body_lines = wrap_text(draw, record.note_body, note_body_font, table_width)
    body_text = "\n".join(body_lines[:2])
    draw.multiline_text(
        (table_left, note_top_y + 54),
        body_text,
        font=note_body_font,
        fill=NOTE_TEXT,
        spacing=10,
    )

    return image


def copy_image_to_clipboard(image: Image.Image) -> tuple[bool, str]:
    if platform.system() != "Windows":
        return False, "当前仅支持 Windows 图片剪贴板。"

    try:
        import ctypes

        CF_DIB = 8
        GMEM_MOVEABLE = 0x0002

        output = io.BytesIO()
        image.convert("RGB").save(output, format="BMP")
        data = output.getvalue()[14:]

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not handle:
            return False, "申请剪贴板内存失败。"

        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            kernel32.GlobalFree(handle)
            return False, "锁定剪贴板内存失败。"

        ctypes.memmove(pointer, data, len(data))
        kernel32.GlobalUnlock(handle)

        if not user32.OpenClipboard(None):
            kernel32.GlobalFree(handle)
            return False, "打开系统剪贴板失败。"

        try:
            user32.EmptyClipboard()
            if not user32.SetClipboardData(CF_DIB, handle):
                kernel32.GlobalFree(handle)
                return False, "写入图片到剪贴板失败。"
            handle = None
        finally:
            user32.CloseClipboard()

        return True, "图片已复制到剪贴板，可以直接粘贴。"
    except Exception as exc:
        return False, f"复制到剪贴板失败: {exc}"


class RewardImageApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(WINDOW_TITLE)
        self.root.geometry("1280x860")
        self.root.minsize(1120, 760)
        self.root.configure(bg="#EEF2F7")

        sample = default_record()
        self.device_var = tk.StringVar(value=sample.device_type)
        self.login_var = tk.StringVar(value=sample.login_type)
        self.game_name_var = tk.StringVar(value=sample.game_name)
        self.prize_var = tk.StringVar(value=sample.prize_name)
        self.status_var = tk.StringVar(value=sample.exchange_status)
        self.time_var = tk.StringVar(value=sample.exchange_time)
        self.page_title_var = tk.StringVar(value=sample.page_title)

        self.preview_label: tk.Label | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None
        self.current_image = create_reward_image(self.build_record())

        self.setup_styles()
        self.build_layout()
        self.render_preview()

    def setup_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Panel.TFrame", background="#FFFFFF")
        style.configure("Header.TLabel", background="#FFFFFF", foreground=PRIMARY_TEXT, font=("Arial", 13, "bold"))
        style.configure("Hint.TLabel", background="#FFFFFF", foreground="#667085", font=("Arial", 10))
        style.configure("Action.TButton", font=("Arial", 10, "bold"))
        style.configure("PanelText.TLabel", background="#FFFFFF", foreground=PRIMARY_TEXT)

    def build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=18, style="Panel.TFrame")
        container.pack(fill="both", expand=True, padx=18, pady=18)

        left_panel = ttk.Frame(container, padding=18, style="Panel.TFrame")
        left_panel.pack(side="left", fill="y")

        right_panel = ttk.Frame(container, padding=18, style="Panel.TFrame")
        right_panel.pack(side="left", fill="both", expand=True, padx=(18, 0))

        ttk.Label(left_panel, text="顶部标题", style="Header.TLabel").pack(anchor="w")
        ttk.Label(left_panel, text="平台和渠道为二选一，程序会自动拼成顶部蓝条标题。", style="Hint.TLabel").pack(anchor="w", pady=(4, 14))

        platform_row = ttk.Frame(left_panel, style="Panel.TFrame")
        platform_row.pack(fill="x", pady=4)
        ttk.Label(platform_row, text="平台", width=10, style="PanelText.TLabel").pack(side="left")
        device_box = ttk.Combobox(
            platform_row,
            textvariable=self.device_var,
            values=["安卓", "苹果"],
            state="readonly",
            width=26,
        )
        device_box.pack(side="left", fill="x", expand=True)
        device_box.bind("<<ComboboxSelected>>", self.on_form_change)

        login_row = ttk.Frame(left_panel, style="Panel.TFrame")
        login_row.pack(fill="x", pady=4)
        ttk.Label(login_row, text="渠道", width=10, style="PanelText.TLabel").pack(side="left")
        login_box = ttk.Combobox(
            login_row,
            textvariable=self.login_var,
            values=["Q", "微信"],
            state="readonly",
            width=26,
        )
        login_box.pack(side="left", fill="x", expand=True)
        login_box.bind("<<ComboboxSelected>>", self.on_form_change)

        game_row = ttk.Frame(left_panel, style="Panel.TFrame")
        game_row.pack(fill="x", pady=4)
        ttk.Label(game_row, text="游戏名", width=10, style="PanelText.TLabel").pack(side="left")
        game_entry = ttk.Entry(game_row, textvariable=self.game_name_var, width=28)
        game_entry.pack(side="left", fill="x", expand=True)
        game_entry.bind("<KeyRelease>", self.on_form_change)

        ttk.Separator(left_panel).pack(fill="x", pady=18)

        fields = [
            ("页面标题", self.page_title_var),
            ("奖品名称", self.prize_var),
            ("兑换状态", self.status_var),
            ("兑换时间", self.time_var),
        ]
        ttk.Label(left_panel, text="记录内容", style="Header.TLabel").pack(anchor="w", pady=(0, 12))
        for label_text, variable in fields:
            row = ttk.Frame(left_panel, style="Panel.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label_text, width=10, style="PanelText.TLabel").pack(side="left")
            entry = ttk.Entry(row, textvariable=variable, width=28)
            entry.pack(side="left", fill="x", expand=True)
            entry.bind("<KeyRelease>", self.on_form_change)

        button_row = ttk.Frame(left_panel, style="Panel.TFrame")
        button_row.pack(fill="x", pady=(20, 10))
        ttk.Button(button_row, text="刷新预览", command=self.render_preview, style="Action.TButton").pack(side="left")
        ttk.Button(button_row, text="当前时间", command=self.fill_current_time, style="Action.TButton").pack(side="left", padx=8)
        ttk.Button(button_row, text="恢复默认", command=self.reset_form, style="Action.TButton").pack(side="left")

        ttk.Button(left_panel, text="复制到剪贴板", command=self.copy_preview_to_clipboard, style="Action.TButton").pack(fill="x", pady=(8, 0))
        ttk.Button(left_panel, text="保存图片", command=self.save_image, style="Action.TButton").pack(fill="x", pady=(8, 0))

        ttk.Label(right_panel, text="图片预览", style="Header.TLabel").pack(anchor="w")
        ttk.Label(right_panel, text="生成的是 1280 x 900 的 PNG，右侧预览会按比例缩放。", style="Hint.TLabel").pack(anchor="w", pady=(4, 14))

        preview_frame = ttk.Frame(right_panel, style="Panel.TFrame")
        preview_frame.pack(fill="both", expand=True)
        self.preview_label = tk.Label(preview_frame, bg="#DCE3EE", anchor="center")
        self.preview_label.pack(fill="both", expand=True)

    def build_record(self) -> RewardRecord:
        return RewardRecord(
            device_type=self.device_var.get().strip(),
            login_type=self.login_var.get().strip(),
            game_name=self.game_name_var.get().strip(),
            prize_name=self.prize_var.get().strip(),
            exchange_status=self.status_var.get().strip(),
            exchange_time=self.time_var.get().strip(),
            page_title=self.page_title_var.get().strip() or "兑换记录",
        )

    def render_preview(self, *_args: object) -> None:
        self.current_image = create_reward_image(self.build_record())
        preview = self.current_image.copy()
        preview.thumbnail(PREVIEW_SIZE)
        self.preview_photo = ImageTk.PhotoImage(preview)
        if self.preview_label is not None:
            self.preview_label.configure(image=self.preview_photo)

    def on_form_change(self, _event: tk.Event[tk.Misc]) -> None:
        self.render_preview()

    def fill_current_time(self) -> None:
        self.time_var.set(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.render_preview()

    def reset_form(self) -> None:
        defaults = default_record()
        self.device_var.set(defaults.device_type)
        self.login_var.set(defaults.login_type)
        self.game_name_var.set(defaults.game_name)
        self.prize_var.set(defaults.prize_name)
        self.status_var.set(defaults.exchange_status)
        self.time_var.set(defaults.exchange_time)
        self.page_title_var.set(defaults.page_title)
        self.render_preview()

    def save_image(self) -> None:
        self.render_preview()
        output_path = filedialog.asksaveasfilename(
            title="保存兑换记录图片",
            defaultextension=".png",
            filetypes=[("PNG 图片", "*.png")],
            initialfile="兑换记录.png",
        )
        if not output_path:
            return

        self.current_image.save(output_path, format="PNG")
        messagebox.showinfo("保存成功", f"图片已保存到:\n{output_path}")

    def copy_preview_to_clipboard(self) -> None:
        self.render_preview()
        success, message = copy_image_to_clipboard(self.current_image)
        if success:
            messagebox.showinfo("复制成功", message)
            return
        messagebox.showwarning("复制失败", message)


def export_sample(output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    image = create_reward_image(default_record())
    image.save(output, format="PNG")
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="兑换记录图片生成器")
    parser.add_argument(
        "--export-sample",
        type=Path,
        help="不打开 GUI，直接导出一张默认样例图到指定路径。",
    )
    return parser.parse_args()


def run_gui() -> None:
    root = tk.Tk()
    app = RewardImageApp(root)
    root.mainloop()


def main() -> None:
    args = parse_args()
    if args.export_sample:
        output = export_sample(args.export_sample)
        print(f"Sample image exported: {output}")
        return

    run_gui()


if __name__ == "__main__":
    main()
