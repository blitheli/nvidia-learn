"""用已安装的 Isaac Sim 打开 Lunalab 或 Lunaryard，不启动 ROS 2 / Yamcs / Zenoh。

这是 nvidia-learn 里的覆盖脚本，不修改 omnilrs/upstream。
官方 run.py 没有「只看场景」的模式，默认 mode 是 ROS2。

本文件没有在 Windows 上运行过。退出码 0 只表示进程自己走完了循环，
不表示画面、材质或物理已经正确。
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

VISUAL_ENVS = {
    "lunalab",
    "lunalab_deformable",
    "lunalab4SDG",
    "lunaryard_20m",
    "lunaryard_40m",
    "lunaryard_80m",
    "lunaryard_20m_deformable",
    "lunaryard_40m_deformable",
    "lunaryard_40m_workshop",
    "lunaryard_40m_workshop_full",
}

BANNER = (
    "[windows-adapter] 未在 Windows 上验证。"
    "这个脚本不调用官方 run.py，也不启动 ROS 2 / Yamcs / Zenoh / LargeScale。"
)


def upstream_root() -> Path:
    env = os.environ.get("OMNILRS_ROOT")
    if env:
        return Path(env).resolve()
    return (Path(__file__).resolve().parent.parent / "upstream").resolve()


def is_lfs_pointer(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            head = handle.read(80)
    except OSError:
        return False
    return head.startswith(b"version https://git-lfs.github.com/spec/")


def pointer_files(assets: Path) -> list[Path]:
    found = []
    if not assets.is_dir():
        return found
    for dirpath, dirnames, filenames in os.walk(assets):
        dirnames[:] = [name for name in dirnames if name != "SouthPole"]
        for name in filenames:
            path = Path(dirpath) / name
            if is_lfs_pointer(path):
                found.append(path)
    return found


def check_imports() -> int:
    print("[windows-adapter] --check-imports 只检查 Python 模块，不启动 Isaac Sim。")
    print(f"[windows-adapter] 解释器: {sys.executable}")
    print(f"[windows-adapter] 版本: {sys.version.replace(chr(10), ' ')}")
    modules = [
        ("hydra", "视觉草稿需要。pip: hydra-core"),
        ("omegaconf", "视觉草稿需要。pip: omegaconf"),
        ("matplotlib", "地形模块在 import 时加载。pip: matplotlib"),
        ("skyfield", "Lunaryard 星历需要。pip: skyfield"),
        ("quaternion", "WorldBuilders 岩石采样需要。pip: numpy-quaternion"),
        ("numpy", "应由 Isaac Sim 6.2 提供，期望 2.3.1，不要用 pip 另装一份"),
        ("scipy", "应由 Isaac Sim 6.2 提供，迁移文档记录为 1.17.0"),
        ("cv2", "应由 Isaac Sim 6.2 提供。不要再装一套 opencv-python"),
        ("warp", "Lunalab 地形 import warp。Isaac 6.2 的 omni.warp.core 是 1.17.0"),
        ("numba", "LargeScale 才需要。视觉草稿默认不 import。若要装，只能是 0.63.x"),
        ("zfpy", "LargeScale 压缩 DEM 才需要。视觉草稿默认不 import"),
        ("osgeo.gdal", "运行 src/ 不需要。Windows 上安装风险见 requirements-windows.txt"),
    ]
    failed = 0
    for name, note in modules:
        try:
            module = __import__(name)
        except Exception as exc:
            failed += 1
            print(f"  FAIL  {name}: {exc.__class__.__name__}: {exc}")
            print(f"        {note}")
            continue
        version = getattr(module, "__version__", None)
        if version is None and name == "osgeo.gdal":
            version = getattr(module, "__version__", None)
        extra = f" {version}" if version else ""
        print(f"  OK    {name}{extra}")
    if failed:
        print(f"[windows-adapter] {failed} 个模块导入失败。这还不是场景启动测试。")
        return 1
    print("[windows-adapter] 列出的模块都能导入。下一步才是启动 Lunalab。")
    return 0


def load_config(root: Path, environment: str, stock_robot: bool, hydra_overrides: list[str]) -> dict:
    os.chdir(root)
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    import run  # 注册 as_tuple，并复用官方的配置实例化
    from hydra import compose, initialize_config_dir

    overrides = [f"environment={environment}"]
    if not stock_robot:
        overrides.append("robot=husky")
    overrides.extend(hydra_overrides)
    with initialize_config_dir(config_dir=str(root / "cfg"), version_base="1.3"):
        cfg = compose(config_name="config", overrides=overrides)
    cfg = run.omegaconfToDict(cfg)
    return run.instantiateConfigs(cfg)


def require_assets(root: Path) -> None:
    pointers = pointer_files(root / "assets")
    if not pointers:
        return
    print("[windows-adapter] 资产仍是 Git LFS 指针，场景文件还不是真二进制。")
    print("[windows-adapter] 在 omnilrs/upstream 里执行 git lfs install && git lfs pull")
    print("[windows-adapter] 不要把拉下来的二进制提交进 nvidia-learn。")
    for path in pointers[:12]:
        print(f"  pointer  {path.relative_to(root)}")
    if len(pointers) > 12:
        print(f"  ... 另有 {len(pointers) - 12} 个指针文件")
    raise SystemExit(2)


def launch_app(cfg: dict):
    from isaacsim import SimulationApp

    from src.environments.rendering import (
        set_chromatic_aberrations,
        set_lens_flares,
        set_motion_blur,
        set_tbn_frame_mode,
    )
    from src.environments_wrappers import _enable_required_extensions

    class SimulationAppWait(SimulationApp):
        """与上游 SimulationApp_wait 相同的关闭钩子。定义在本文件里，不改 submodule。"""

        def __init__(self, launch_config: dict) -> None:
            super().__init__(launch_config)
            self.wait_for_threads = []

        def add_wait(self, waiting_functions: list) -> None:
            self.wait_for_threads += waiting_functions

        def close(self, wait_for_replicator: bool = True, **kwargs) -> None:
            if not self._exiting:
                for wait in self.wait_for_threads:
                    wait()
                self.wait_for_threads = []
            super().close(wait_for_replicator=wait_for_replicator, **kwargs)

    renderer_cfg = cfg["rendering"]["renderer"]
    launch_config = dict(renderer_cfg.__dict__)
    tbn_frame_mode = launch_config.pop("tbn_frame_mode")
    simulation_app = SimulationAppWait(launch_config)
    _enable_required_extensions()
    set_tbn_frame_mode(tbn_frame_mode)
    set_lens_flares(cfg)
    set_motion_blur(cfg)
    set_chromatic_aberrations(cfg)
    return simulation_app


def build_scene(cfg: dict, simulation_app, no_robot: bool):
    import omni.timeline

    from src.configurations.simulator_mode_enum import SimulatorMode
    from src.environments.lunalab import LunalabController
    from src.environments.lunaryard import LunaryardController
    from src.environments.stellar_engine_env_mixin import StellarEngineEnvMixin
    from src.environments.utils import set_moon_env_name
    from src.environments_wrappers.rate import Rate
    from src.robots.robot import RobotManager
    from src.simulation import Simulation

    env_cfg = cfg["environment"]
    env_name = env_cfg["name"]
    if env_name not in ("Lunalab", "Lunaryard"):
        raise SystemExit(f"[windows-adapter] 不启动 {env_name}。LargeScale / ROS / Yamcs 不在这个草稿里。")

    sim = Simulation(
        physics_dt=env_cfg["physics_dt"],
        rendering_dt=env_cfg["rendering_dt"],
        physics_scene=cfg["physics"]["physics_scene"],
    )
    set_moon_env_name(env_name)
    for _ in range(100):
        sim.step()
    sim.reset()

    # SDG 只是「不是 ROS2」的现成枚举。这里不用 SDG 管理器，避免 is_ROS2 去写 ROS domain。
    # 控制器在 Simulation 热身之后再创建，和上游 Yamcs 管理器一样，避免拿到旧 stage。
    mode = SimulatorMode.SDG
    if env_name == "Lunalab":
        controller = LunalabController(mode=mode, **env_cfg)
    else:
        controller = LunaryardController(
            mode=mode,
            **env_cfg,
            is_simulation_alive=simulation_app.is_running,
            close_simulation=simulation_app.close,
        )
    controller.load()
    simulation_app.add_wait(controller.get_wait_for_threads())

    robot_manager = None
    if not no_robot:
        robot_manager = RobotManager(env_cfg["robots_settings"], mode=mode)
        usd_path = robot_manager.robot_parameters.usd_path
        print(f"[windows-adapter] 机器人 USD: {usd_path}")
        if is_lfs_pointer(Path(usd_path)):
            raise SystemExit("[windows-adapter] 机器人 USD 仍是 LFS 指针。先 git lfs pull。")
        robot_manager.preload_robot(sim, get_height_func=controller.get_terrain_height)
        if isinstance(controller, StellarEngineEnvMixin) and robot_manager.robot.subsystems is not None:
            robot_manager.robot.subsystems.set_sun_prim_path(controller.get_sun_prim_path())
        controller.add_robot_manager(robot_manager)
        for _ in range(100):
            sim.step()
        sim.reset()

    if env_cfg["enforce_realtime"]:
        rate = Rate(dt=env_cfg["physics_dt"])
    else:
        rate = Rate(is_disabled=True)
    timeline = omni.timeline.get_timeline_interface()
    return sim, controller, robot_manager, rate, timeline


def run_loop(simulation_app, sim, controller, robot_manager, rate, timeline) -> None:
    timeline.play()
    while simulation_app.is_running():
        rate.reset()
        sim.step()
        if sim.is_playing():
            if getattr(controller, "enable_stellar_engine", False):
                controller.update_stellar_engine(dt=sim.get_physics_dt())
            restarted = sim.consume_restart()
            robot = None if robot_manager is None else robot_manager.robot
            if restarted:
                sim.reset()
                if robot is not None:
                    robot.invalidate_articulation_api()
            else:
                if robot is not None:
                    robot.update_articulation_api()
                controller.update()
        if not controller.monitor_thread_is_alive():
            print("[windows-adapter] 环境后台线程停了，结束循环。")
            break
        rate.sleep()
    if robot_manager is not None and robot_manager.robot is not None:
        robot_manager.robot.invalidate_articulation_api()
    sim.stop()
    timeline.stop()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="未验证的 Lunalab / Lunaryard 视觉草稿")
    parser.add_argument("--environment", default="lunalab", choices=sorted(VISUAL_ENVS))
    parser.add_argument("--check-imports", action="store_true")
    parser.add_argument("--no-robot", action="store_true")
    parser.add_argument(
        "--stock-robot",
        action="store_true",
        help="使用环境 yaml 自带的机器人，而不是 robot=husky（nograph_husky.usd）",
    )
    parser.add_argument("hydra_overrides", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    args.hydra_overrides = [item for item in args.hydra_overrides if item != "--"]
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    print(BANNER)
    if args.check_imports:
        return check_imports()

    root = upstream_root()
    if not (root / "run.py").is_file():
        print(f"[windows-adapter] 找不到上游 run.py: {root}")
        print("[windows-adapter] 先 git submodule update --init --recursive")
        return 2
    print(f"[windows-adapter] 上游: {root}")
    print(f"[windows-adapter] 解释器: {sys.executable}")
    print(f"[windows-adapter] 场景配置: {args.environment}")
    print("[windows-adapter] 机器人配置: " + ("环境 yaml 自带" if args.stock_robot else "robot=husky / nograph_husky.usd"))
    require_assets(root)
    cfg = load_config(root, args.environment, args.stock_robot, args.hydra_overrides)
    label = cfg["environment"]["name"]
    if label not in ("Lunalab", "Lunaryard"):
        print(f"[windows-adapter] {args.environment} 解析成 {label}，这个草稿不启动它。")
        return 2
    if cfg["environment"]["terrain_manager"].moon_yard.deformation_engine.enable:
        print("[windows-adapter] 这份配置打开了轮-壤变形。本循环不调用 deform_terrain()，官方也没有 Windows 验证。")

    simulation_app = launch_app(cfg)
    try:
        sim, controller, robot_manager, rate, timeline = build_scene(cfg, simulation_app, args.no_robot)
        print("[windows-adapter] 场景已加载。窗口关闭前，下面的循环只是在步进，不能当成已经复现成功。")
        run_loop(simulation_app, sim, controller, robot_manager, rate, timeline)
    finally:
        simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
