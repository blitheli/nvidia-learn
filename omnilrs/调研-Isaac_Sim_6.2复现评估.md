# OmniLRS 在 Windows + Isaac Sim 6.2 上的复现评估

评估日期：2026-11-12。上游默认分支 `main`，锁定提交：

`916b0dc29dc62e51fc18df072db8c73c3173b6c7`

提交时间：2026-11-10 19:43:06 +0900（UTC 2026-11-10 10:43:07）。提交说明：Fix Artefacts CI after #162（#170）。`git ls-remote` 看到的 `refs/heads/main` 就是这个 SHA。没有更晚的提交。先前口头说的「最近推送约 2026-11-11」按这个时间戳核对后，就是 11 月 10 日这次 #170。

本文只根据当时读到的文件、Wiki 和两个旁路仓库。没有在 Windows 上执行 `C:\isaacsim\python.bat`，没有 nvidia-smi，因此不写这台机器的 GPU 型号或驱动版本。用户自己的 `D:\Nvidia\isaac-lunar-lite` 也不在本次阅读范围内。

## 分能力结论

在这台已经装好工作站版 Isaac Sim 6.2 的 Windows 上，**不能按官方现行方式完整复现 OmniLRS**。Isaac 的大版本已经对齐到 6.2，这一点要和 2026-11-04 时「官方只写 2023.1.1 / 4.1.0」的旧结论分开：那句话今天只还留在滞后的 Wiki 里，不再是 README 和 `pixi.toml` 的内容。

| 能力 | 结论 | 依据 |
| --- | --- | --- |
| 按 README 用 pixi 完整安装并跑官方任务 | 否 | `platforms` 只有 `linux-64` / glibc 2.35，没有 `win-64` |
| 官方安装接管 `C:\isaacsim` | 否 | pixi 另装 `isaacsim==6.2.0.0`（extras `all` + `extscache`）的 Linux wheel |
| Wiki 所说的 Windows 支持 | 否 | Installation 页仍写 Windows is not supported |
| Isaac 版本与用户的 6.2 对齐 | 是 | README、`pixi.toml`、CHANGELOG、迁移文档的目标都是 Isaac Sim 6.2 / Python 3.12 |
| Lunalab 无 ROS 视觉 | 条件 | 要用 `python.bat` 走 `windows-adapter`，补齐 pip、LFS 贴图和 USD。未在本机跑过，不能算复现 |
| Lunaryard 星历光照 | 条件 | 同上，另加 LFS 星历和 skyfield。未在本机跑过 |
| 轮-壤变形 | 否 | 代码在，默认配置 `enable: False`；迁移文档把 deformable 场景标成只做静态分析。没有 Windows 官方路径。适配循环不调用 `deform_terrain()` |
| LargeScale、GeoClipmap、S3 DEM | 否 | Linux 上 `test-ros2-largescale` 与 `test-yamcs-largescale` 有通过记录。Windows 没有对应安装路径，DEM 也不在 git 里 |
| ROS 2 Jazzy | 否 | 激活脚本、库路径和 pixi 任务都是 Linux。外部示例仓库仍是 Humble |
| Yamcs / Grafana 任务控制 | 否 | pixi 任务和 Java 服务器都按 Linux 文档写。没有 Windows 官方路径 |
| SDG / SDG dataset | 否（本次 Windows 目标） | 代码在 main 上（#155）。迁移文档把 SDG 标为 analysis-only，捕获本身未列入四条运行门禁 |
| Zenoh | 否（本次 Windows 目标） | 有 pixi 任务。迁移矩阵里是 analysis-only |
| SpaceROS / 旧用户 Docker | 否 | `omnilrs.docker/` 已删除。`spaceros_demo.docker/` 仍是 Isaac 5.0 时代的 ROS 2 Humble 演示，未迁 6.2 |
| 最接近完整复现的路径 | 条件 | Ubuntu 24.04 实机，或 GPU 能可靠直通的 WSL2，按 README 用 pixi。不要按 Wiki 去建已经删除的用户 Docker 镜像 |

## 仓库现状与版本时间线

官方仓库：<https://github.com/OmniLRS/OmniLRS>，默认分支 `main`。

CHANGELOG 与 README 对得上的版本线：

| 标记 | 日期 | 内容 |
| --- | --- | --- |
| 1.0.0 | 2024-07-24 | Lunalab、Lunaryard、程序化陨石坑和岩石、SDG、ROS1/ROS2、地形变形、Docker、SpaceROS、Wiki |
| 2.0.0 | 2024-09-11 | LargeScale geometry clipmap、恒星引擎、Git LFS 资产、SpaceROS（Humble） |
| 2.5.0 | 2025-11-13 | 迁到 Isaac Sim 5.0。README 的 V2.5 图注也是这一次 |
| 3.0.0 | 2026-06-29 | Yamcs、Pragyaan / Husky 控制器、功率/通信/热模型、pixi 多环境 |
| Unreleased（已在 main） | 2026-11-09 至 2026-11-10 | Isaac Sim 5.0 到 6.2。Python 3.12、numpy 2.3.1、numba 0.63、Warp 1.17、ROS 2 Jazzy、用户 Docker 删除 |

锁定点附近、本文核对过的提交：

| PR | SHA | 时间（+0900） | 标题 |
| --- | --- | --- | --- |
| #164 | `e90cc5076d8b474c3beb9f3ee33a26ba143ea3e8` | 2026-11-09 11:33:55 | Migrate to Isaac Sim 6.2 |
| #165 | `c89c6c279ab60c4dd10f4af63980d4b6dc0f7077` | 2026-11-09 11:41:37 | 把 World / Articulation / Camera 迁出已弃用 API |
| #167 | `db50d580c566b0ff9fdbaf5e04d58674ec880c4c` | 2026-11-09 13:48:42 | 全模式多相机；Yamcs 从服务器读 MDB |
| #162 | `2726b01610fa45327a6ea216135016e43269f430` | 2026-11-10 13:55:35 | Lunaryard 与 LargeScale 的 Infinite PBR 月壤 |
| #170 | `916b0dc29dc62e51fc18df072db8c73c3173b6c7` | 2026-11-10 19:43:06 | `.mdl` 退出 Git LFS；CI 基础镜像改为 `omni-ci-0.5.1` |

嵌套 submodule `WorldBuilders` 停在 `c68be6782356f9c51b5c7c70edcffa83d8126b3e`（2026-10-29，WorldBuilders #8）。迁移文档写明这是弃用导入和 ruff 修复之后的指针。

`docs/migration_plan_6.2.md` 的开头仍写着 “Implemented on branch `migrate/isaacsim-6.2`”，文末勾选框也还是空的，第 0 节还有一句 Open：CI 基础镜像 `omni-ci-0.4.0` 需要构建。以 git 历史为准，#164 及后续已经在 `main` 上。#170 的说明和 `ci.docker/README.md` 使用的是 `omni-ci-0.5.1`，那句 Open 已经过时。CHANGELOG 的 Unreleased 把这次迁移写成已经落地的破坏性变更：用户安装改为 pixi，Docker 只留给 CI。

迁移文档记录的官方运行结果，平台是 Linux，不是 Windows：

- `test-ros2`（ROS2，lunalab）：6 passed，8 个 topic 检查因开发机没有系统 ROS CLI 而 skip
- `test-ros2-largescale`：8 passed，9 skipped
- `test-yamcs`（`lunaryard_40m_workshop`，pragyaan）：17 passed
- `test-yamcs-largescale`：21 passed
- 驱动从 580.178.04 升到 **595.99.02** 之后，上述四条在 595 上再跑过（6p/8s、8p/9s、17p、21p）
- 文档表格里的 “Tested driver” 另写了 NVIDIA 测试过的 **595.58.03**，并注明当时主机已有 580.178，高于容器 `MIN_DRIVER_VERSION=570.169`
- README 的安装节写驱动 ≥ 580，并写 Isaac Sim 6.2 在 595.58 上测试过
- Isaac 7.x 明确不在范围内
- torch 解析到 cu130 构建，需要驱动 ≥ 580

这些驱动号都是上游在 Linux 上写下的。不要挪到这台 Windows 上。

issue #140（2026-08-18 打开，2026-11-10 关闭，标签 question）：Isaac Sim 5.0 加雷达，或 Isaac Sim 6.0 打开 `enable_motion_bvh`，会出现错误的阴影和岩石。2026-11-09 有维护者说自己在 Isaac Sim 6.2 上没能复现；报告者次日表示更新 Isaac 之后问题消失并关闭。把它当作已知风险即可，不要写成 Windows 6.2 上一定还会出现，也不要写成已经在这台机器上验证消失。

## 官方支持矩阵

数字和名称都来自锁定提交里的 README、`pixi.toml`、CHANGELOG、`docs/migration_plan_6.2.md`，以及同一次抓取的 Wiki。

### 系统与安装

| 项 | 现行（README + pixi + 迁移文档） |
| --- | --- |
| 操作系统 | Linux x86_64，glibc ≥ 2.35。推荐 Ubuntu 24.04。Ubuntu 22.04 被 Isaac Sim 6.2 视为过时，6.2 里仍可用 |
| GPU | RTX。README 写驱动 ≥ 580，并在 595.58 上测试过。迁移文档还有 595.99.02 的再验证记录 |
| Python | 3.12（`python = "3.12.*"`） |
| Isaac Sim | 6.2.0.0，extras `all` 与 `extscache` |
| 安装方式 | pixi。用户向 Docker 目录 `omnilrs.docker/` 已删除。Docker 只用于 `ci.docker/` 和 `artefacts.Dockerfile` |
| ROS 2 | Isaac 自带的 Jazzy。`ROS_DISTRO=jazzy`，`RMW_IMPLEMENTATION=rmw_fastrtps_cpp`，`cfg/mode/ROS2.yaml` 的 `bridge_name: jazzy`。外部节点也应使用 Jazzy |
| 关键 Python / conda 依赖 | numpy==2.3.1，warp-lang==1.17.0，numba==0.63.*，conda 的 gdal/libgdal，以及 hydra-core、omegaconf、skyfield、zfpy、numpy-quaternion |

常用任务：

```bash
pixi run -e ros2 ros2
pixi run -e yamcs yamcs
pixi run -e yamcs yamcs-largescale
```

`ros2` 任务是 `python run.py mode=ROS2`。`yamcs` 任务是 `mode=Yamcs environment=lunaryard_40m_workshop robot=pragyaan controller=pragyaan-controller`。

### 三类场景

| 场景 | 官方描述 | 和 6.2 验证的关系 |
| --- | --- | --- |
| Lunalab | 卢森堡大学月面模拟场的数字孪生，支持行驶时的地形变形 | `test-ros2` 在 Linux 上跑过 lunalab + ROS2 |
| Lunaryard | 小尺度程序化月面。给定月面坐标和日期后，用星历放地球和太阳。也支持变形 | `test-yamcs` 跑的是 `lunaryard_40m_workshop` |
| LargeScale | 约 5 m/像素的真实 DEM，程序化补到约 2.5 cm/像素，再用 geometry clipmap 画大范围 | `test-ros2-largescale` 与 `test-yamcs-largescale` 在 Linux 上通过。DEM 目录不在 git 中 |

Lunalab 与 Lunaryard 的环境 yaml 里，`deformation_engine.enable` 默认是 `False`。带 `_deformable` 的配置才打开。迁移文档 §8.1 把 deformable 环境列为分析过、没有放进四条运行门禁。

### 任务控制与 SDG

| 项 | 现状 |
| --- | --- |
| ROS 2 | 一等模式。管理器在 `src/environments_wrappers/ros2/`。Jazzy 的 `rclpy` 由 Isaac 扩展提供 |
| Yamcs + Grafana | 一等模式。遥测/遥控、多相机桶、启动时对照服务器 MDB（#167）。服务器在独立仓库 |
| Zenoh | pixi 环境 `zenoh`，任务 `zenoh_lunaryard` / `zenoh_lab` / `zenoh_largescale`。迁移矩阵标为 analysis-only |
| SDG | `mode=SDG`。#155 增加了不依赖 Isaac 的后处理路径 `scripts/sdg_dataset`。迁移文档写明捕获过程没有跑，57 个不启动 Isaac 的单元测试在 numpy 2.3.1 下通过 |
| 渲染 | `cfg/rendering/ray_tracing.yaml` 的 renderer 已是 `RealTimePathTracing`，不再是旧的 `RayTracedLighting` |

## 与用户环境对照

用户给出的本机条件：

- Windows
- 工作站版 Isaac Sim 6.2，路径 `C:\isaacsim`，用 `python.bat` 跑脚本
- 另有自制精简月面演示 `D:\Nvidia\isaac-lunar-lite`（本次未读，不比较）

对照结果：

1. **版本号对齐。** 官方现行目标就是 Isaac Sim 6.2、Python 3.12。2026-11-04 那种「文档只支持 2023.1.1 和 4.1.0」只适用于当时的 Wiki/旧安装脚本，不适用于今天的 README。`scripts/install_native.sh` 仍残留 2023.1.1 的 `python.sh` 路径，迁移文档把它标成预先存在、与这次迁移无关。
2. **安装方式不对齐。** 官方不使用已经装好的工作站目录。pixi 在 Linux 环境里安装自己的 `isaacsim` wheel。Windows 上既没有声明的 pixi 平台，也不能用那份 wheel 替换 `C:\isaacsim`。
3. **系统不对齐。** 官方只声明 Linux。Wiki 明确写 Windows is not supported。
4. **ROS、任务控制和 LargeScale 不对齐。** 这些都挂在 pixi 的 Linux 环境、bash 激活脚本、Jazzy 库路径、Java/Yamcs 和 S3 DEM 上。
5. **只有场景视觉有一条未验证的旁路。** 用现成的 `python.bat` 加载 Lunalab 或 Lunaryard，不走 ROS。官方 `run.py` 本身没有这个模式，所以旁路放在 `windows-adapter/`，而不是改上游。

## Wiki 与 README 的滞后点

现行标准是 README、`pixi.toml`、CHANGELOG、`docs/migration_plan_6.2.md`。Wiki 没有跟着 6.2 改完。2026-11-12 抓到的页面内容如下。

Installation（页面上可见日期 2026-03-03）：

- Operating System 写 Linux，类似 Ubuntu 22.04 或 24.04
- 明确写 **Windows is not supported**
- 仍建议优先 Docker：`./omnilrs.docker/build_docker.sh`
- Native 一节的 TODO 还写着 “update this section with Isaacsim 4.5”
- 仍写支持的工作站版本是 **2023.1.1 和 4.1.0**，并建议留在 2023.1.1，因为 4.1.0 有渲染问题
- pip 示例仍是 `~/.local/share/ov/pkg/isaac_sim-2023.1.1/python.sh`
- LFS 与 SouthPole 的 `aws s3 sync` 命令仍在这一页，这两条和代码现状还一致

getting_started：

- 第一步仍是 `./omnilrs.docker/run_docker.sh`
- 示例命令仍是 `/isaac-sim/python.sh run.py`，并说明默认等于 lunalab + ROS2 + ray tracing
- 页尾有一段 “Native Installation”：把 `/isaac-sim/python.sh` 换成 `pixi run`，例如 `pixi run ros2 environment=lunaryard_40m`

也就是说，同一份 Wiki 里 Docker/`python.sh` 的旧流程和 pixi 的新提示叠在一起。用户向 Docker 目录在锁定提交里已经不存在。按 Wiki 的 Docker 章节做，会找不到 `omnilrs.docker/`。

## 资产、LFS 与 S3

`.gitattributes` 把 `usd`、`usdz`、`usdc`、`npy`、`pkl`、`png`、`jpg`、`tif`、`exr`、`ies`、`bsp`、`tf`、`bpc`、`tpc` 交给 Git LFS。本次以 `GIT_LFS_SKIP_SMUDGE=1` 克隆时，`git lfs ls-files` 为 **1275** 条。抽样的 `assets/Ephemeris/de421.bsp` 是 LFS 指针文本。

`.mdl` 不在 LFS 规则里。#170 说明 18 个 `.mdl` 合计约 134 KB，改回普通 git。锁定提交的工作区里数到 18 个 `.mdl`，`LunarRegolithInfinite.mdl` 的开头是 `mdl 1.8;`，不是指针。因此 submodule 不拉 LFS 也能带上材质源码。这些材质引用的 PNG（例如 `assets/Textures/LunarRegolith8k/LunarRegolith8k_diff.png`）仍是 LFS。不 `git lfs pull`，材质代码在，贴图不在。

Lunalab 还依赖 LFS 的 `assets/USD_Assets/environments/Lunalab.usd`，以及 `assets/Terrains/Lunalab/Terrain_lidar01` 和 `Terrain_lidar02` 下的 `dem.npy` / `mask.npy`。陨石坑样条 `assets/Terrains/crater_spline_profiles.pkl` 也是 LFS，并且是用 SciPy 1.17 重新序列化的。

Lunaryard 的 `assets/Terrains/Lunaryard/` 只有 `.keepme`，地形靠程序生成。光照依赖四份星历：`de421.bsp`、`moon_080317.tf`、`pck00008.tpc`、`moon_pa_de421_1900-2050.bpc`。`scripts/get_ephemeris_data.sh` 可以用 wget 从 NAIF 再下一次，脚本本身是 bash。

LargeScale 的 DEM 不进 git。上游 `.gitignore` 含 `assets/Terrains/SouthPole/`。`ci.docker/README.md` 写 largescale 测试需要 Site20 DEM，可以从开发机复制，或 “re-download from s3”。桶 URL 写在 Wiki，不在 git 树里：

```bash
aws s3 sync s3://jaops-omnilrs-dataset/SouthPole ./assets/Terrains/SouthPole --no-sign-request
aws s3 sync s3://jaops-omnilrs-dataset-jp/SouthPole ./assets/Terrains/SouthPole --no-sign-request
```

nvidia-learn 用 submodule 指向上述 SHA，不把 LFS 对象或 SouthPole DEM 提交进来。`pixi.lock` 只留在 submodule 内。

本机补齐步骤写在 [omnilrs/README.md](README.md)。

## 旁路仓库的版本

| 仓库 | 核对时的 HEAD | 和 OmniLRS 6.2 的关系 |
| --- | --- | --- |
| <https://github.com/jnskkmhr/omnilrs_ros2_demo> | `9d09ff1e6b7ead7d761dda37f2e84c59268b3e91`，2026-05-05 | README 仍要求先跑 OmniLRS 的 `./omnilrs.docker/run_docker.sh` 和 `/isaac-sim/python.sh`。`docker/Dockerfile` 是 `osrf/ros:humble-desktop`，工作区目录名是 `humble_ws`。迁移文档把这个仓库迁到 Jazzy/pixi 列为后续工作，不在 6.2 迁移范围内 |
| <https://github.com/OmniLRS/yamcs-mission-control-pragyaan> | `bdc1c134e7dc14cd0c12e74a6da624083ab42f87`，2026-11-06，PR #4 | README 已经按 OmniLRS 的 `cfg/robot`、`cfg/controller` 和 `src/tmtc/yamcs_naming.py` 生成 MDB，并用 `OMNILRS_ROOT` 指向一份 OmniLRS 检出。这个提交早于 OmniLRS 的 #167（2026-11-09）和 #164。接口方向一致，本次没有做联调，不能写成已经对 `916b0dc` 逐项跑通。README 的安装示例是 `apt install openjdk-25-jdk` 和 bash，没有 Windows 步骤。仓库正文没有写 Isaac 6.2 |
| `spaceros_demo.docker/` | 随 OmniLRS `916b0dc` | `FROM osrf/space-ros:humble-2024.10.0`。README 写明这是未维护演示，目标仍是 Isaac Sim 5.0 / ROS 2 Humble |

## Windows 适配策略

完整复现不要在 Windows 上硬做。要跑官方的 ROS 2、Yamcs、LargeScale 和四条测试，用 Ubuntu 24.04，或 GPU 直通可靠的 WSL2，然后只按 README 的 pixi 流程。不要跟着 Wiki 重建 `omnilrs.docker`。

Windows 上只准备一条部分路径，见 [windows-adapter/README.md](windows-adapter/README.md)：

- 差异表：[windows-adapter/差异清单.md](windows-adapter/差异清单.md)
- `run_lunalab.bat` / `run_lunaryard.bat` 调用 `ISAAC_PYTHON`（默认 `C:\isaacsim\python.bat`）
- `visual_preview.py` 读取上游 Hydra 配置，只构建 Lunalab 或 Lunaryard
- 默认机器人配置是 `robot=husky`，USD 为 `nograph_husky.usd`，避开环境 yaml 里的 `ros2_husky_PhysX_vlp16.usd`
- 发现 LFS 指针就退出，避免把指针文件交给 USD 或 `np.load`
- `requirements-windows.txt` 列出 hydra-core、omegaconf、skyfield、matplotlib、numpy-quaternion，并说明 numba、zfpy、GDAL 不要为了这条视觉路径先装
- `patches/` 目前没有补丁。不把修改过的 submodule 工作区提交回 nvidia-learn

接上本机后的顺序写在 [windows-adapter/本机验证清单.md](windows-adapter/本机验证清单.md)：确认 `python.bat` 的版本、拉 LFS、`--check-imports`、无机器人的 Lunalab、再加机器人、看材质和阴影、Lunaryard 星历光照，然后决定 ROS 2 是放弃还是改去 WSL/Ubuntu。

写这份草稿时，在 Linux 上做了两件不启动 Isaac 的检查：工作区里的 LFS 指针会让 `visual_preview.py` 直接退出；装上 Hydra 之后，`lunalab` 与 `lunaryard_20m` 能解析成 Lunalab / Lunaryard，`robot=husky` 使用 `nograph_husky.usd`，`--stock-robot` 仍指向环境 yaml 里的 `ros2_husky_PhysX_vlp16.usd`。这不能代替 Windows 上的 `python.bat`。

## 参考

- 锁定的 README：<https://github.com/OmniLRS/OmniLRS/blob/916b0dc29dc62e51fc18df072db8c73c3173b6c7/README.md>
- 迁移文档：<https://github.com/OmniLRS/OmniLRS/blob/916b0dc29dc62e51fc18df072db8c73c3173b6c7/docs/migration_plan_6.2.md>
- `pixi.toml`：<https://github.com/OmniLRS/OmniLRS/blob/916b0dc29dc62e51fc18df072db8c73c3173b6c7/pixi.toml>
- Wiki Installation：<https://github.com/OmniLRS/OmniLRS/wiki/Installation>
- Wiki getting_started：<https://github.com/OmniLRS/OmniLRS/wiki/getting_started>
- #164：<https://github.com/OmniLRS/OmniLRS/pull/164>
- #165：<https://github.com/OmniLRS/OmniLRS/pull/165>
- #167：<https://github.com/OmniLRS/OmniLRS/pull/167>
- #162：<https://github.com/OmniLRS/OmniLRS/pull/162>
- #170：<https://github.com/OmniLRS/OmniLRS/pull/170>
- #140：<https://github.com/OmniLRS/OmniLRS/issues/140>
