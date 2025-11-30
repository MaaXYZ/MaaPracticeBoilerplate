from pathlib import Path

import platform
import shutil
import sys

try:
    import jsonc
except ModuleNotFoundError as e:
    raise ImportError(
        "Missing dependency 'json-with-comments' (imported as 'jsonc').\n"
        f"Install it with:\n  {sys.executable} -m pip install json-with-comments\n"
        "Or add it to your project's requirements."
    ) from e

from configure import configure_ocr_model

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

working_dir = Path(__file__).parent
install_path = working_dir / Path("install")
version = len(sys.argv) > 1 and sys.argv[1] or "v0.0.1"

def is_android():
    """判断当前是否为安卓系统"""
    # 安卓基于Linux内核，先判断是否为Linux
    if platform.system() != 'Linux':
        return False
    # 安卓内核版本通常包含 'android' 关键词（区分普通Linux）
    release = platform.release().lower()
    if 'android' in release:
        return True
    # 补充：Termux（安卓终端）的特征
    if 'termux' in release or 'termux' in platform.uname().node:
        return True
    return False


def get_dotnet_platform_tag():
    """自动检测当前平台并返回对应的平台标签"""
    os_type = platform.system()
    os_arch = platform.machine()

    print(f"检测到操作系统: {os_type}, 架构: {os_arch}")

    if os_type == "Windows":
        # 在Windows ARM64环境中，platform.machine()可能错误返回AMD64
        # 我们需要检查处理器标识符来确定真实架构
        processor_identifier = os.environ.get("PROCESSOR_IDENTIFIER", "")

        # 检查是否为ARM64处理器
        if "ARMv8" in processor_identifier or "ARM64" in processor_identifier:
            print(f"检测到ARM64处理器: {processor_identifier}")
            os_arch = "ARM64"

        # 映射platform.machine()到pip的平台标签
        arch_mapping = {
            "AMD64": "win-x64",
            "x86_64": "win-x64",
            "ARM64": "win-arm64",
            "aarch64": "win-arm64",
        }
        platform_tag = arch_mapping.get(os_arch, f"win-{os_arch.lower()}")

    elif os_type == "Darwin":  # macOS
        # 映射platform.machine()到pip的平台标签
        arch_mapping = {
            "x86_64": "osx-x64",
            "arm64": "osx-arm64",
            "aarch64": "osx-arm64",
        }
        platform_tag = arch_mapping.get(os_arch, f"osx-{os_arch.lower()}")

    elif os_type == "Linux":
        # 映射platform.machine()到pip的平台标签
        arch_mapping = {
            "x86_64": "linux-x64",
            "aarch64": "linux-arm64",
            "arm64": "linux-arm64",
        }
        platform_tag = arch_mapping.get(os_arch, f"linux-{os_arch.lower()}")

    else:
        raise ValueError(f"不支持的操作系统: {os_type}")

    print(f"使用平台标签: {platform_tag}")
    return platform_tag


def install_deps():
    if not (working_dir / "deps" / "bin").exists():
        print("Please download the MaaFramework to \"deps\" first.")
        print("请先下载 MaaFramework 到 \"deps\"。")
        sys.exit(1)

    if is_android():
        maafw_dir = install_path 
    else: 
        maafw_dir = install_path/ "runtimes" / get_dotnet_platform_tag() / "native"
    

    shutil.copytree(
        working_dir / "deps" / "bin",
        maafw_dir,
        ignore=shutil.ignore_patterns(
            "*MaaDbgControlUnit*",
            "*MaaThriftControlUnit*",
            "*MaaRpc*",
            "*MaaHttp*",
        ),
        dirs_exist_ok=True,
    )
    shutil.copytree(
        working_dir / "deps" / "share" / "MaaAgentBinary",
        install_path / "MaaAgentBinary",
        dirs_exist_ok=True,
    )


def install_resource():

    configure_ocr_model()

    shutil.copytree(
        working_dir / "assets" / "resource",
        install_path / "resource",
        dirs_exist_ok=True,
    )
    shutil.copy2(
        working_dir / "assets" / "interface.json",
        install_path,
    )

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = jsonc.load(f)

    interface["version"] = version

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        jsonc.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    shutil.copy2(
        working_dir / "README.md",
        install_path,
    )
    shutil.copy2(
        working_dir / "LICENSE",
        install_path,
    )


def install_agent():
    shutil.copytree(
        working_dir / "agent",
        install_path / "agent",
        dirs_exist_ok=True,
    )


if __name__ == "__main__":
    install_deps()
    install_resource()
    install_chores()
    install_agent()

    print(f"Install to {install_path} successfully.")
