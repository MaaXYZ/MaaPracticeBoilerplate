import ctypes
import os
import platform
import sys
import zipfile
from ctypes import wintypes
from pathlib import Path
from typing import Optional

import requests


def detect_os():
    """Detect the current operating system.

    Returns:
        str: "android" | "linux" | "macos" | "win" | "unknown"
    """
    sys_platform = sys.platform
    if sys_platform.startswith("linux"):
        # 判断是不是安卓（Termux）
        import os
        if "ANDROID_ROOT" in os.environ:
            return "android"
        return "linux"
    elif sys_platform == "darwin":
        return "macos"
    elif sys_platform in ("win32", "cygwin"):
        return "win"
    else:
        return "unknown"


def detect_arch():
    """
    Detect the architecture of the current machine.

    Returns:
        str: "x86_64" if the machine is 64-bit Intel/AMD architecture,
             "aarch64" if the machine is 64-bit ARM architecture,
             or "unknown" if the architecture cannot be determined.
    """

    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    elif "aarch64" in machine or "arm64" in machine:
        return "aarch64"
    else:
        return "unknown"


def get_local_version_from_dll(dll_path: str) -> Optional[str]:
    """安全地从本地 DLL 获取 maafw 版本并卸载 DLL

    Arguments:
        dll_path {str} -- DLL 路径

    Returns:
        Optional[str] -- DLL 版本，失败时返回 None
    """
    # 确保路径是绝对路径
    dll_path = os.path.abspath(dll_path)

    # 1. 尝试加载 DLL
    try:
        # 使用 WinDLL 以便获取句柄
        lib = ctypes.WinDLL(dll_path)
    except OSError as e:
        print(f"加载 DLL 失败: {e}", file=sys.stderr)
        return "NONE"

    # 记录句柄用于后续卸载
    dll_handle = lib._handle

    try:
        # 2. 检查是否存在 MaaVersion 函数
        if not hasattr(lib, 'MaaVersion'):
            print(f"DLL 缺少 MaaVersion 函数: {dll_path}", file=sys.stderr)
            return "NONE"

        # 3. 设置函数签名
        lib.MaaVersion.restype = ctypes.c_char_p
        lib.MaaVersion.argtypes = []

        # 4. 调用函数获取版本
        version_bytes = lib.MaaVersion()

        # 确保返回的是 bytes
        if not isinstance(version_bytes, bytes):
            print("MaaVersion 返回无效类型", file=sys.stderr)
            return "NONE"

        return version_bytes.decode('utf-8')

    except (AttributeError, ctypes.ArgumentError) as e:
        print(f"调用 DLL 函数出错: {e}", file=sys.stderr)
        return "NONE"

    finally:
        # 5. 无论如何都尝试卸载 DLL
        _safe_unload_dll(dll_handle)


def _safe_unload_dll(handle: int) -> bool:
    """安全卸载 DLL

    Arguments:
        handle {int} -- DLL 句柄

    Returns:
        bool -- 是否成功卸载
    """
    try:
        if handle and kernel32.FreeLibrary(handle):
            return True
        return False
    except Exception as e:
        print(f"卸载 DLL 失败: {e}", file=sys.stderr)
        return False
    finally:
        # 清除引用，帮助垃圾回收
        del handle


def get_local_platform():
    """获取本地版本地址

    Returns:
        str -- 版本号
    """
    os_name = detect_os()
    arch_name = detect_arch()
    combo_key = f"{os_name}-{arch_name}"
    print("检测结果:", combo_key)
    return combo_key


def auto_ver_select(resource_list, combo_key):
    """自动选择版本

    Arguments:
        resource_list {list} -- 通过Release获取到的列表
        combo_key {str} -- 识别到的版本

    Returns:
        str -- 下载路径或者是False
        如果是False则不进行下载
    """
    matched = next(
        (item for item in resource_list if combo_key in item['name']), None)
    if matched:
        print(f"找到下载包: {matched['name']}")
        print(f"下载链接: {matched['url']}")
        print(f"大小: {matched['size_mb']} MB")
        return matched['url']
    else:
        print("没有找到适配的版本。")
        return False


def custum_ver_select(resource_list):
    """用户自行选择下载包

    Arguments:
        resource_list {list} -- 通过Release获取到的列表

    Returns:
        str -- 下载路径或者是False
        如果是False则不进行下载
    """
    while True:
        try:
            choice = input("\n请输入要下载的选项编号 (输入 'q' 退出): ")
            if choice.lower() == 'q':
                return False
            choice_idx = int(choice)  # 转换为0开始的索引
            if 0 <= choice_idx < len(resource_list):
                print(f"下载链接: {resource_list[choice_idx]['url']}")
                return resource_list[choice_idx]["url"]
            else:
                print(f"无效的选择，请输入 1-{len(resource_list)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")


def get_github_download_options():
    """获取Github的下载选项（前5个版本）"""
    url = "https://api.github.com/repos/MaaXYZ/MaaFramework/releases"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        releases = response.json()[:5]
    except requests.exceptions.RequestException as e:
        print(f"获取发布信息失败: {str(e)}")
        return None

    if not releases:
        print("未找到任何发布版本")
        return None

    resource_list = []
    print("\n可用的版本：")
    for idx, release in enumerate(releases):
        version = release['tag_name']
        print(f"{idx}. {version}")
        assets = release.get("assets", [])
        asset_list = [
            {
                "index": i,
                "name": asset['name'],
                "url": asset['browser_download_url'],
                "size": asset['size'],
                "size_mb": asset['size'] / (1024 * 1024)
            } for i, asset in enumerate(assets)
        ]
        resource_list.append({"version": version, "assets": asset_list})

    return resource_list


def select_download_resource(resource_list, auto=False):
    """
    选择下载资源

    1. 如果 `auto` 是 True，我们将自动选择最新的版本
    2. 如果 `auto` 是 False，我们将手动选择版本
       1. 显示所有可用的版本
       2. 用户选择一个版本
       3. 显示该版本的所有可用的资源
       4. 用户选择一个资源

    Args:
        resource_list (list): 一个包含 Release 信息的列表
        auto (bool, optional): 是否自动选择最新的版本. Defaults to False.

    Returns:
        str: 下载资源的 URL，如果用户取消，将返回 False
    """
    if not resource_list:
        print("没有可用的下载资源")
        return None

    # 自动模式：使用最新版本
    if auto:
        # resource_list[0] 是最新的版本
        latest_release = resource_list[0]
        assets = latest_release['assets']
        combo_key = get_local_platform()
        return auto_ver_select(assets, combo_key)

    # 手动模式：选择版本
    print("\n请选择版本：")
    for idx, release in enumerate(resource_list):
        print(f"{idx}. {release['version']}")

    while True:
        try:
            choice = input("\n请输入版本编号 (输入 'q' 退出): ")
            if choice.lower() == 'q':
                return None

            version_idx = int(choice)
            if 0 <= version_idx < len(resource_list):
                selected_release = resource_list[version_idx]
                print(f"\n已选择版本: {selected_release['version']}")

                # 显示该版本的资源
                assets = selected_release['assets']
                if not assets:
                    print("该版本没有可用的资源")
                    return None

                print("\n可用的资源：")
                for idx, asset in enumerate(assets):
                    print(
                        f"{idx}. {asset['name']} ({asset['size_mb']:.2f} MB)")

                return custum_ver_select(assets)
            else:
                print(f"无效的选择，请输入 0-{len(resource_list)-1} 之间的数字")
        except ValueError:
            print("请输入有效的数字")


def check_version(file_ver, url_ver):
    """检查是否包含对应版本

    Arguments:
        file_ver {str} -- 本地dll版本
        url_ver {str} -- 网页链接

    Returns:
        bool -- 如果包含,返回True,是最新版本
        如果不包含,返回False,不是最新版本
    """
    return file_ver in url_ver


def download_file(url):
    r = requests.get(
        url,
        allow_redirects=True,
        stream=True,
        timeout=10
    )
    with open("MaaFramework.zip", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)


def unzip(filename, target_dir=None):
    """
    解压ZIP文件到指定目录

    参数:
    filename -- 要解压的ZIP文件名
    target_dir -- 解压目标目录（默认为当前目录）
    """
    # 如果没有指定目标目录，询问用户
    if target_dir is None:
        target_dir = input("请输入解压路径（留空则解压到上两级目录）: ").strip()

    # 如果留空，使用当前目录(或者在此自定义路径)
    if not target_dir:
        target_dir = "../../"

    # 创建目标目录（如果不存在）
    os.makedirs(target_dir, exist_ok=True)

    print(f"正在解压 {filename} 到 {os.path.abspath(target_dir)}...")

    try:
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)

            for i, file in enumerate(file_list, 1):
                zip_ref.extract(file, target_dir)

                # 计算进度百分比
                progress = i / total_files
                # 构造进度条字符串（50字符宽度）
                bar_length = 50
                bar = '█' * int(bar_length * progress)
                percent = f"{progress:.0%}"
                # 使用回车符覆盖当前行
                print(
                    f"\r解压进度: [{bar:<{bar_length}}] {percent} ({i}/{total_files})", end="")

            # 最后换行
            print("\n解压完成！")
            return True
    except zipfile.BadZipFile:
        print(f"错误: {filename} 不是有效的ZIP文件")
        return False
    except FileNotFoundError:
        print(f"错误: 文件 {filename} 不存在")
        return False
    except Exception as e:
        print(f"解压过程中发生错误: {str(e)}")
        return False


def delete_file(filename):
    """安全删除文件并处理所有异常"""
    try:
        # 使用 pathlib 处理路径更安全
        file_path = Path(filename)

        # 检查是否为文件（避免误删目录）
        if file_path.is_file():
            # 实际删除文件
            file_path.unlink()
            print(f"文件 '{filename}' 已成功删除")
            return True
        elif file_path.exists():
            print(f"'{filename}' 是目录而非文件")
            return False
        else:
            print(f"文件 '{filename}' 不存在，无需删除")
            return False

    except PermissionError:
        print(f"没有权限删除 '{filename}'")
        return False
    except Exception as e:
        print(f"删除文件时出错: {e}")
        return False


def main(is_debug=False, is_delete=True):
    print("正在获取最新版本信息", end=":\t")
    download_options = get_github_download_options()
    if download_options is None:
        print("网络错误或者手动退出,无法更新")
        return None

    auto_update = auto_update_check()

    print("正在获取本地版本信息", end=":\n")
    file_ver = get_local_version_from_dll(dll_path)
    print(f"当前版本:{file_ver}")

    url_ver = select_download_resource(download_options, auto_update)
    if url_ver is None:
        print("无法找到最新版本，无法更新")
        return None
    print(f"本地版本:{file_ver}")
    print(f"网络最新版本:{url_ver}")

    # 反转检查结果,为是否最新版本做准备
    checked_version = not check_version(file_ver, url_ver)
    if checked_version or is_debug or not is_delete:
        print("\n当前版本与选中版本不符，需要更新\n")
        print("正在下载文件MaaFramework.zip")
        download_file(url_ver)
        print("正在解压文件")
        unzip("MaaFramework.zip")
        print("解压完成")
    else:
        print("已是最新版本，无需更新")

    if is_debug:
        pass
    elif is_delete:
        print("正在删除文件MaaFramework.zip")
        delete_file("MaaFramework.zip")


def auto_update_check():
    auto_update = input("\n输入n或者N并且按回车\n关闭自动选择更新包功能\n") in ["N", "n"]
    return not auto_update


print("正在切换工作路径至exe所在路径")
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
dll_path = os.path.abspath("../../bin/MaaFramework.dll")


if __name__ == "__main__":
    if "--unzip" in sys.argv:  # 仅进行本地压缩包解压，不下载
        print("仅进行本地压缩包解压，不下载")
        unzip("MaaFramework.zip")
    elif "--check_version" in sys.argv:  # 仅进行版本检查,不下载
        print("仅进行版本检查,不下载")
        file_ver = get_local_version_from_dll(dll_path)
        print(file_ver)
        url_ver = select_download_resource(
            get_github_download_options(), False)
        print(url_ver)
        check_resalt = check_version(file_ver, url_ver)
        print(check_resalt)
    else:
        is_debug = False
        is_delete = True
        if "--debug" in sys.argv:  # 无视版本进行下载,下载完成后不删除压缩包
            print("--debug 将无视版本检查进行下载,下载完成后不删除压缩包")
            is_debug = True
        if "--not_delete" in sys.argv:  # 解压完成后不删除压缩包
            print("--not_delete 解压完成后不删除压缩包")
            is_delete = False
        main(is_debug=is_debug, is_delete=is_delete)
    os.system("pause")
