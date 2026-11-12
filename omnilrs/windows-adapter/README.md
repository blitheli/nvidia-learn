# Windows 适配草稿

面向已经装好的工作站版 Isaac Sim 6.2（默认 `C:\isaacsim\python.bat`）。这里的脚本没有在 Windows 上跑过。能导入、能开窗、画面对不对，都要等接上本机再看。

官方 `run.py` 没有无 ROS 的模式。`cfg/config.yaml` 的默认 `mode` 是 `ROS2`，启动后会 `import rclpy`。这个目录用 `visual_preview.py` 覆盖启动：读同一套 Hydra 配置，只构建 Lunalab 或 Lunaryard，不启用 ROS 2、Yamcs、Zenoh、LargeScale。这不是完全复现。

## 文件

| 文件 | 作用 |
| --- | --- |
| `run_lunalab.bat` | 调用 `python.bat` 打开 Lunalab |
| `run_lunaryard.bat` | 调用 `python.bat` 打开 `lunaryard_20m` |
| `visual_preview.py` | 实际的覆盖启动器 |
| `requirements-windows.txt` | 还要手工安装的 pip 包，以及 GDAL 风险 |
| `差异清单.md` | 上游里偏 Linux 的脚本、路径和启动方式 |
| `本机验证清单.md` | 接上机器后按什么顺序看 |
| `patches/` | 现在是空的。不要把改过的 submodule 提交回来 |

## 使用前

1. `git submodule update --init --recursive`
2. 在 `omnilrs\upstream` 里 `git lfs install` 然后 `git lfs pull`。`.mdl` 已经在普通 git 里，贴图、USD、星历、`npy`/`pkl` 不拉就还是 LFS 指针。脚本发现指针会直接退出。
3. 用 Isaac 自带的 Python 装依赖：

```bat
C:\isaacsim\python.bat -m pip install -r omnilrs\windows-adapter\requirements-windows.txt
```

路径可以用环境变量换掉：

| 变量 | 默认 |
| --- | --- |
| `ISAAC_PYTHON` | `C:\isaacsim\python.bat` |
| `OMNILRS_ROOT` | 本目录上一级的 `upstream` |

批处理会设置 `OMNI_KIT_ACCEPT_EULA=YES`，和上游 pixi 一样，避免卡在 EULA 提示。这不代表已经接受过、也不代表程序已经跑通。

## 命令

```bat
omnilrs\windows-adapter\run_lunalab.bat --check-imports
omnilrs\windows-adapter\run_lunalab.bat
omnilrs\windows-adapter\run_lunalab.bat --no-robot
omnilrs\windows-adapter\run_lunaryard.bat
```

批处理里的提示是英文，避免 Windows 命令行的代码页把 UTF-8 中文拆开。中文说明在本目录的 Markdown 和 `visual_preview.py` 的输出里。上游 `CraterGeneratorConf` 初始化时会打印一份陨石坑配置，那是官方代码自己的 `print`，不是这个草稿额外加的调试。

`%*` 会原样传给 `visual_preview.py`。Hydra 覆盖写在后面，例如：

```bat
run_lunalab.bat rendering.renderer.multi_gpu=false
```

默认叠加 `robot=husky`。`cfg/robot/husky.yaml` 使用 `assets/USD_Assets/robots/nograph_husky.usd`。环境 yaml 里自带的是 `ros2_husky_PhysX_vlp16.usd`，里面有 ROS OmniGraph。要对比那份资源，加 `--stock-robot`。

`husky.yaml` 里当前写下的出生点是 Lunalab 的 `[5.0, 5.0, 0.1]`。Lunaryard 草稿也会用这个点，不是 `lunaryard_20m.yaml` 里的 `[10.0, 10.0, 0.5]`。

## 这个草稿不做的事

- 不跑 `pixi`，也不安装 `isaacsim==6.2.0.0` 的 Linux wheel
- 不启动 ROS 2 Jazzy、Yamcs、Grafana、Zenoh
- 不打开 LargeScale，不同步 S3 DEM
- 循环里不调用 `deform_terrain()`
- 不修改 `omnilrs/upstream` 的任何文件
