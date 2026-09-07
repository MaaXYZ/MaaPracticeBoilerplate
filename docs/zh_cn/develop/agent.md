# AgentServer 编写指引

> [!NOTE]
> Agent 属于 MaaFramework 的高级功能之一。在学习本章节以前请确保你已经掌握以下技能，否则请先学习[基础](/docs/zh_cn/develop/how_to_develop.md)的编写方法。
>
> - 至少熟练掌握一门编程语言，并理解面向对象的实现方法。
> - 至少用 `Pipeline` 编写过一个完整的可用`通用UI` 执行的任务链，了解 `ProjectInterface 协议`和 `Pipeline`。
> - 本教程推荐使用 VSCode 进行编写。

本教程使用 Python 编写 AgentServer 示例。如果你有面向对象编程的经验，也可选用[任意 MaaFramework 支持的编程语言](https://github.com/MaaXYZ/MaaFramework/blob/main/docs/zh_cn/2.1-%E9%9B%86%E6%88%90%E6%96%87%E6%A1%A3.md)来实现，将示例代码套用到其他语言是一件很容易的事。

> [!TIP]
>
> 本教程可能会使用到 Python 的某些高级特性。如果你正在使用其他的编程语言，请查阅[源码](https://github.com/MaaXYZ/MaaFramework/blob/main/docs/zh_cn/2.1-%E9%9B%86%E6%88%90%E6%96%87%E6%A1%A3.md)以了解某些特殊写法的差异。

_（本篇为编写基础指引，仅介绍 custom recognition 和 custom action 的编写方法，如需了解更多，请参考 [其他内容](#其他内容)）_

## ProjectInterface

要使用 AgentServer 首先要在 interface.json 中补充相关的字段。

```json
{
    ...
    "agent": {
        // 执行命令，可以是 interface.json 所在目录的相对位置，也可以是Path中已有的路径
        "child_exec": "python",
        // 命令的参数
        "child_args": [
            "./agent/main.py"
        ]
    },
    ...
}
```

若按以上内容进行填写，则通用 UI 在启动时会尝试执行 `python ./agent/main.py`。（CWD为 interface.json 所在目录）

## 内容编写

本文将围绕仓库中附带的一个简单的 [demo](/agent) 示例进行讲解。

在开始前，请确保你已经安装了 Python 依赖。

```bash
pip install MaaFw
```

> [!CAUTION]
> **千万不要装错了！**

### 自定义识别

#### 基本结构

完整内容请参考 [my_reco.py](/agent/my_reco.py)。

```python
from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
# 如果 VSCode 在这里报错了说明你没仔细看上一步


@AgentServer.custom_recognition("find_smallest_number")  # 注册识别方法
class SmallestNumberRecognition(CustomRecognition):
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        # dosomething...

        return CustomRecognition.AnalyzeResult(
            box=(0, 0, 100, 100),  # 传回识别到的区域
            detail={"message": "Hello World!"},
        )
        # 或传回 None 表示识别失败
        # return CustomRecognition.AnalyzeResult(
        #     box=None, detail={"message": "World not found!"}
        # )
```

当在 pipeline 中进入 `FindSmallestNumber` 节点时，框架会按注册名调用 `SmallestNumberRecognition` 的 `analyze` 方法。

```json
{
    ...
    "FindSmallestNumber": {
        "recognition": "Custom",
        "custom_recognition": "find_smallest_number",
        "custom_recognition_param": {
            "candidate_rois": [
                [100, 100, 200, 100],
                [300, 100, 200, 100]
            ]
        },
        ...
    }
}
```

如果需要向自定义识别传入参数，可以在 pipeline 中填写 `custom_recognition_param`。Python 侧收到的 `argv.custom_recognition_param` 是 JSON 字符串，需要自行解析：

```python
param = json.loads(argv.custom_recognition_param)
rois = param["candidate_rois"]
```

本仓库的示例会把多个候选区域放在 `candidate_rois` 中，逐个调用 `RecognizeNumber` 节点进行 OCR，并返回数值最小的一个区域。

#### 高级用法

请参考[其他内容](#其他内容)）

### 自定义动作

#### 基本结构

完整内容请参考 [my_action.py](/agent/my_action.py)。

```python
# my_action.py
...


@AgentServer.custom_action("click_target")
class ClickTargetAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        # dosomething...

        return True
```

当在 pipeline 中进入 `FindSmallestNumber` 节点时，框架会按注册名调用 `ClickTargetAction` 的 `run` 方法。

```json
{
    ...
    "FindSmallestNumber": {
        ...
        "action": "Custom",
        "custom_action": "click_target",
        "custom_action_param": {
            "target": [10, 20]
        }
    }
}
```

#### 高级用法

请参考[其他内容](#其他内容)）

### 方法注册

在启动 AgentServer 前，需要先将方法注册到 AgentServer 中。

```python
# main.py
...
import my_action
import my_reco


def main():
    ...

    AgentServer.start_up(socket_id)
    AgentServer.join()
    AgentServer.shut_down()


if __name__ == "__main__":
    main()
```

<details>
  <summary><b>原理说明</b></summary>

```python
# my_action.py
...


@AgentServer.custom_action("click_target")
class ClickTargetAction(CustomAction): ...
```

虽然没有在 `main.py` 中进行显式调用，但这里利用了 Python 的特性，在导入时会自动执行 `my_action.py` 中的 `@AgentServer.custom_action` 装饰器，将 `ClickTargetAction` 注册到 `AgentServer` 中。

</details>

## 调试

> [!WARNING]
>
> 本教程推荐使用 VSCode 并安装 [Maa Pipeline Support 插件](https://marketplace.visualstudio.com/items?itemName=nekosu.maa-support) 进行调试，如果你正在使用 VSCode 以外的编辑器，请查阅其他[开发工具](https://github.com/MaaXYZ/MaaFramework#%E5%BC%80%E5%8F%91%E5%B7%A5%E5%85%B7)的文档。

在 VSCode 里通过 [Maa Pipeline Support 插件](https://marketplace.visualstudio.com/items?itemName=nekosu.maa-support) 正常启动 pipeline 调试即可。**无需手动启动 AgentServer**

<details>
  <summary><b>关于使用其他调试工具的差异</b></summary>

目前只有 [Maa Pipeline Support 插件](https://marketplace.visualstudio.com/items?itemName=nekosu.maa-support)支持在运行 pipeline 时自动启动 `debug session` 并自动插入 `socket id`。若要使用其他开发工具调试，请手动启动 AgentServer 并传入 socket id。

> [!TIP]
>
> 如果你看不懂上面这句话，那我建议你还是用 [Maa Pipeline Support 插件](https://marketplace.visualstudio.com/items?itemName=nekosu.maa-support)进行开发会更好。
</details>

## 打包

我们不能保证所有用户的电脑上都已经安装好了 Python，因此推荐的做法是直接在打包时附带上[便携式 Python 解释器](https://docs.python.org/zh-cn/3/using/windows.html#the-embeddable-package)以及需要用到的依赖。（由于打包后命令执行的对象与开发时不同，所以还要**在打包时修改** interface.json 中 agent 的 exec 字段）

具体流程可以参考这几个文件： [ci 配置文件](https://github.com/duorua/narutomobile/blob/19cc32fc81ef53da2476540c48a60b72f0e07f6a/.github/workflows/install.yml#L148)、[安装 Python](https://github.com/duorua/narutomobile/blob/main/tools/ci/setup_embed_python.py)、[安装依赖](https://github.com/duorua/narutomobile/blob/main/tools/ci/download_deps.py)、[修改interface.json](https://github.com/duorua/narutomobile/blob/55ab710e3293bdbcee8cfb696f4607bfefc2e0c1/tools/ci/install.py#L153)

> [!WARNING]
>
> 如果你正在使用其他编译型语言，请考虑编译链和调用包的跨平台能力。

## 其他内容

有关 AgentServer 的更多调用方法请参考[集成接口一览](https://github.com/MaaXYZ/MaaFramework/blob/main/docs/zh_cn/2.2-%E9%9B%86%E6%88%90%E6%8E%A5%E5%8F%A3%E4%B8%80%E8%A7%88.md)或[接口源码](https://github.com/MaaXYZ/MaaFramework/blob/main/docs/zh_cn/2.1-%E9%9B%86%E6%88%90%E6%96%87%E6%A1%A3.md)

推荐的参考项目：[M9A](https://github.com/MAA1999/M9A)（Python）、[MaaEnd](https://github.com/MaaEnd/MaaEnd)（Go）
