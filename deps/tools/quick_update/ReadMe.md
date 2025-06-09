# 更新脚本
用于自动更新`MaaFramework`框架到本地的`deps`文件夹

逻辑采用覆盖安装

运行的时候会自行切换到py文件所在路径

运行时附带后缀`--debug`将无视本地已有文件进行下载

运行时附带后缀`--unzip`将无视所有代码只进行解压测试

运行时附带后缀`--check_version`将进行一次版本检查，不会下载

默认更新`releases/latest`所提供的`MaaFramework`框架

默认自动选择更新包

如需手动选择请遵循提示按n或者N然后回车

手动选择请遵循提示进行选择

更新完成后会在`.\deps\tools\quick_update`路径下
保留一份`MaaFramework.zip`和一份`version.txt`用来快速解压和校验版本
```
deps
│
└─tools
    │
    └─quick_update
            MaaFramework.zip
            version.txt
```
