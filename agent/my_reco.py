import json

from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context


@AgentServer.custom_recognition("find_smallest_number")
class SmallestNumberRecognition(CustomRecognition):
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:

        param = json.loads(argv.custom_recognition_param or "{}") or {}
        rois = param.get("candidate_rois")
        if not isinstance(rois, list) or not rois:
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail={"error": "candidate_rois 不能为空"},
            )

        res = []

        for roi in rois:
            # 找到 pipeline 中名为 "RecognizeNumber" 的节点，并执行它的识别逻辑
            reco_detail = context.run_recognition(
                "RecognizeNumber",
                argv.image,  # 使用当前获取到的图片
                pipeline_override={  # 临时覆盖节点参数
                    "RecognizeNumber": {  # 要覆盖的节点的名称
                        "roi": roi,  # 覆盖识别区域
                        "only_rec": True,  # 不进行文本检测，直接进行识别
                    }
                },
            )

            if reco_detail is None or not reco_detail.hit:
                print(f"无法读取到内容 {roi}")
                res.append(None)
                continue

            text = str(reco_detail.best_result.text)
            try:
                number = float(text)
            except ValueError:
                print(f"{text} 不是数字!")
                res.append(None)
                continue

            res.append(number)

        if not res or None in res:
            return CustomRecognition.AnalyzeResult(
                box=None,
                detail={"error": "存在无法读取到内容"},
            )

        min_index = res.index(min(res))
        return CustomRecognition.AnalyzeResult(
            box=rois[min_index],
            detail={"smallest_number": res[min_index]},
        )
