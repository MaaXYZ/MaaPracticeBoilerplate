import json

from maa.agent.agent_server import AgentServer
from maa.context import Context
from maa.custom_action import CustomAction


@AgentServer.custom_action("click_target")
class ClickTargetAction(CustomAction):
    def run(
        self,
        context: Context,
        argv: CustomAction.RunArg,
    ) -> bool:

        print("ClickTargetAction is running!")

        param = json.loads(argv.custom_action_param or "{}") or {}
        target = param.get("target")
        if not isinstance(target, list) or len(target) != 2:
            return False

        # 执行点击
        click_job = context.tasker.controller.post_click(target[0], target[1])
        # 等待点击完成，这一步必须有！
        click_job.wait()

        return True
