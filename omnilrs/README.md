# OmniLRS 笔记

这里保存三样东西：

1. 中文调研：[调研-Isaac_Sim_6.2复现评估.md](调研-Isaac_Sim_6.2复现评估.md)
2. 上游代码：`upstream/`，git submodule，指向 <https://github.com/OmniLRS/OmniLRS>，锁定 main `916b0dc29dc62e51fc18df072db8c73c3173b6c7`（2026-11-10 19:43:06 +0900）
3. 本机适配草稿：[windows-adapter/](windows-adapter/README.md)，调用 `C:\isaacsim\python.bat`。没有改上游历史，也没有把补丁写进 submodule 工作区

`upstream/` 里另有嵌套 submodule `WorldBuilders`（<https://github.com/AntoineRichard/WorldBuilders>，`c68be6782356f9c51b5c7c70edcffa83d8126b3e`）。官方 `pixi.lock` 只存在于这个 submodule 里，不要复制到 nvidia-learn 根目录。

## 克隆

```bash
git clone --recurse-submodules https://github.com/blitheli/nvidia-learn.git
cd nvidia-learn
```

如果仓库已经克隆、子模块是空目录：

```bash
git submodule update --init --recursive
```

只做上面两步时，Git LFS 大文件不会进工作区（本仓库添加 submodule 时设置了 `GIT_LFS_SKIP_SMUDGE=1`）。`.mdl` 材质是普通 git 文本，会随 submodule 下来。贴图、USD、星历、`*.npy` / `*.pkl` 仍是 LFS 指针，要在本机单独拉取。

## 本机补齐资产

在 `omnilrs/upstream` 里执行。这些文件留在 OmniLRS 自己的 LFS / S3 上，不要提交进 nvidia-learn。

```bash
cd omnilrs/upstream
git lfs install
git lfs pull
```

LargeScale 的南极 DEM 不在 git 里（上游 `.gitignore` 忽略 `assets/Terrains/SouthPole/`）。官方 Wiki 的下载命令是：

```bash
aws s3 sync s3://jaops-omnilrs-dataset/SouthPole ./assets/Terrains/SouthPole --no-sign-request
# 离日本更近时：
# aws s3 sync s3://jaops-omnilrs-dataset-jp/SouthPole ./assets/Terrains/SouthPole --no-sign-request
```

桶地址写在 Wiki Installation 页。上游 git 树里的 `ci.docker/README.md` 只写了 “re-download from s3”，没有重复这个 URL。

## 和本机的关系

用户本机是 Windows，Isaac Sim 6.2 装在 `C:\isaacsim`，用 `python.bat` 跑脚本。另有自制演示 `D:\Nvidia\isaac-lunar-lite`。本目录没有读取那份演示，也不把它放进仓库。

官方现行安装是 Linux + pixi，不会接管 `C:\isaacsim`。Windows 上能试的只有 [windows-adapter](windows-adapter/README.md) 里的无 ROS 视觉草稿，而且接上本机之前都还没验证。
