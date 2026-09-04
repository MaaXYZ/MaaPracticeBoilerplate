from pathlib import Path

import shutil

project_root = Path(__file__).parent.parent.resolve()


def configure_ocr_model():
    source_ocr_dir = project_root / "assets" / "MaaCommonAssets" / "OCR"
    if not source_ocr_dir.exists():
        print(f"File Not Found: {source_ocr_dir}")
        exit(1)

    ocr_dir = project_root / "resource" / "base" / "model" / "ocr"
    if not ocr_dir.exists():  # copy default OCR model only if dir does not exist
        shutil.copytree(
            source_ocr_dir / "ppocr_v6" / "small",
            ocr_dir,
            dirs_exist_ok=True,
        )
    else:
        print("Found existing OCR directory, skipping default OCR model import.")


if __name__ == "__main__":
    configure_ocr_model()

    print("OCR model configured.")
