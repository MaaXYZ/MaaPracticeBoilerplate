from pathlib import Path

import shutil

assets_dir = Path(__file__).parent / "assets"


def configure_ocr_model():
    if not (assets_dir / "MaaCommonAssets" / "OCR").exists():
        print("Please clone this repository completely, don’t miss \"--recursive\", and don’t download the zip package!")
        print("请完整克隆本仓库，不要漏掉 \"--recursive\"，也不要下载 zip 包！")
        exit(1)

    ocr_dir = assets_dir / "resource" / "base" / "model" / "ocr"
    if not ocr_dir.exists():   # copy default OCR model only if dir does not exist
        shutil.copytree(
            assets_dir / "MaaCommonAssets" / "OCR" / "ppocr_v4" / "zh_cn",
            ocr_dir,
            dirs_exist_ok=True,
        )
    else:
        print("Found existing OCR directory, skipping default OCR model import.")


if __name__ == "__main__":
    configure_ocr_model()

    print("OCR model configured.")