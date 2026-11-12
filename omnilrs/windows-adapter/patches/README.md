# 补丁目录

当前没有打进 `omnilrs/upstream` 的补丁。

官方 `run.py` 的模式只有 ROS2、Yamcs、Zenoh、SDG，默认是 ROS2。Windows 草稿用旁边的 `visual_preview.py` 自己组 Lunalab / Lunaryard 循环，避免改 submodule 里的文件。

如果接上本机后必须改上游文件，把 diff 放在这个目录，在本机执行：

```bat
git -C omnilrs\upstream apply omnilrs\windows-adapter\patches\某个补丁.diff
```

改过的 submodule 工作区不要提交回 nvidia-learn。nvidia-learn 只应记录上游的 gitlink SHA。
