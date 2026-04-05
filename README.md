# img-gen

Windows 桌面版兑换记录图片生成器。

## 功能

- 平台支持 `安卓 / 苹果` 二选一，渠道支持 `Q / 微信` 二选一
- 自动生成顶部标题，并附带 `[更换绑定角色]`、`[刷新]`
- 关闭按钮位于白色内容区域内部
- 只保留 `奖品名称`、`兑换状态`、`兑换时间` 三列
- 三列表格为居中布局
- 实时预览图片效果
- 支持一键复制图片到 Windows 剪贴板
- 一键保存为 PNG
- 支持命令行导出样例图，方便无界面验证

## 本地开发

```bash
uv sync
uv run python main.py
```

如果只想快速导出一张默认图片：

```bash
uv run python main.py --export-sample output/sample.png
```

## Windows 打包

建议先在 Windows 机器上打包，这样字体和 GUI 环境更接近最终用户。

### 安装打包依赖

```bash
uv sync --extra build
```

### 生成 exe

```bash
uv run pyinstaller --noconfirm --onefile --windowed --name reward-image-generator main.py
```

打包完成后，产物会出现在 `dist/reward-image-generator.exe`。

如果你希望首版更稳，也可以把 `--onefile` 改成目录模式：

```bash
uv run pyinstaller --noconfirm --windowed --name reward-image-generator main.py
```

## GitHub 云编译

仓库已经带了 GitHub Actions 工作流 [windows-build.yml](/Users/yml/codes/img_gen/.github/workflows/windows-build.yml)，把代码推送到 GitHub 后会自动触发 Windows 云编译，也可以在 GitHub 的 `Actions` 页面手动点 `Run workflow`。

编译完成后：

- 进入 GitHub 仓库的 `Actions`
- 打开最新一次 `Windows Build`
- 在页面底部下载 artifact `reward-image-generator-windows`

artifact 里包含：

- `reward-image-generator.exe`
- `output/sample.png`

## 字体说明

程序会优先读取系统里的中文字体：

- Windows: `微软雅黑 / 黑体 / 宋体 / 等线`
- macOS: `PingFang / 华文黑体`
- Linux: `Noto Sans CJK / 文泉驿`

如果目标 Windows 机器字体较精简，建议在打包阶段额外带一份中文字体文件，显示会更稳定。

## 常用命令

```bash
uv sync
uv run python main.py
uv run python main.py --export-sample output/sample.png
uv sync --extra build
uv run pyinstaller --noconfirm --onefile --windowed --name reward-image-generator main.py
```
