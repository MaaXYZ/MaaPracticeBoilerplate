import os
import sys
import zipfile
import ctypes
import requests
import platform
from typing import Optional, List, Generator


def detect_os():
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
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    elif "aarch64" in machine or "arm64" in machine:
        return "aarch64"
    else:
        return "unknown"


def get_local_version_from_dll(dll_path: str) -> Optional[str]:
    """尝试从本地dll获取maafw版本

    Arguments:
        dll_path {str} -- dll路径

    Returns:
        Optional[str] -- dll版本
    """
    try:
        # 尝试加载 DLL
        lib = ctypes.CDLL(dll_path)

        # 检查是否存在 MaaVersion 函数
        if not hasattr(lib, 'MaaVersion'):
            return None

        # 设置函数签名
        lib.MaaVersion.restype = ctypes.c_char_p
        lib.MaaVersion.argtypes = []

        # 调用函数并返回解码后的字符串
        version_bytes = lib.MaaVersion()
        return version_bytes.decode('utf-8')

    except (OSError, AttributeError, ctypes.ArgumentError):
        # 捕获所有可能的加载/调用异常
        return None


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
                return resource_list[choice_idx]["url"]
            else:
                print(f"无效的选择，请输入 1-{len(resource_list)} 之间的数字")
        except ValueError:
            print("请输入有效的数字")


def get_github_download_options():
    """获取Github的最新版本下载列表

    Returns:
        list -- 下载版本合集
        或者是None,说明下载出问题了
    """
    try:
        response = requests.get(
            "https://api.github.com/repos/MaaXYZ/MaaFramework/releases/latest",
            timeout=10
        )
        response.raise_for_status()  # 如果状态码不是200则抛出异常

        assets = response.json().get("assets", [])

        if not assets:
            print("该发布版未包含任何可下载资源")
            return None

        # 创建结构化资源列表
        resource_list = []
        print("\n可用的下载选项：")
        for idx, asset in enumerate(assets):
            size_mb = asset['size'] / (1024 * 1024)
            print(f"{idx}. {asset['name']} ({size_mb:.2f} MB)")

            # 将资源信息添加到列表
            resource_list.append({
                "index": idx,  # 从0开始的索引
                "name": asset['name'],
                "url": asset['browser_download_url'],
                "size": asset['size'],
                "size_mb": size_mb
            })

        return resource_list

    except requests.exceptions.RequestException as e:
        print(f"获取发布信息失败: {str(e)}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        print(f"解析数据出错: {str(e)}")
        return None


def select_download_resource(resource_list, auto=False):
    """选择下载包

    Arguments:
        resource_list {list} -- 通过Release获取到的列表

    Keyword Arguments:
        auto {bool} -- 是否自动选择下载包 (default: {False})

    Returns:
        str -- 下载路径或者是False
        如果是False则不进行下载
    """
    combo_key = None
    if not resource_list:
        print("没有可用的下载资源")
        return None
    elif auto:
        combo_key = get_local_platform()
        return auto_ver_select(resource_list, combo_key)
    else:
        return custum_ver_select(resource_list)


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
                # 每解压10个文件显示一次进度
                if i % 10 == 0 or i == total_files:
                    print(f"解压进度: {i}/{total_files} ({i/total_files:.0%})")

        print("解压完成！")
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


def main(isdebug=False):
    if isdebug:
        print("处于调试模式，将无视版本进行下载")

    print("正在获取最新版本信息", end=":\t")
    download_options = get_github_download_options()
    if download_options is None:
        print("网络错误或者手动退出,无法更新")
        return None

    auto_update = input("\n输入n或者N并且按回车\n关闭自动选择更新包功能\n")
    if auto_update in ["N", "n"]:
        auto_update = False
    else:
        auto_update = True

    print("正在获取本地版本信息", end=":\n")
    file_ver = get_local_version_from_dll("../../bin/MaaFramework.dll")
    print(f"本地版本:{file_ver}")

    url_ver = select_download_resource(download_options, auto_update)

    print("网络正常，与最新版本信息比较中")
    if check_version(file_ver, url_ver) is False or isdebug:
        url = url_ver
        print(url)
        print("正在下载文件")
        download_file(url)
        print("正在解压文件")
        unzip("MaaFramework.zip")
        print("解压完成")
    else:
        print("已是最新版本，无需更新")


print("正在切换工作路径至exe所在路径")
os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))
if "--debug" in sys.argv:
    main(True)
elif "--unzip" in sys.argv:  # 仅进行本地压缩包解压，不下载
    unzip("MaaFramework.zip")
elif "--check_version" in sys.argv:  # 仅进行版本检查,不下载
    file_ver = get_local_version_from_dll("../../bin/MaaFramework.dll")
    print(file_ver)
    url_ver = select_download_resource(get_github_download_options(), True)
    print(url_ver)
    check_resalt = check_version(file_ver, url_ver)
    print(check_resalt)
else:
    main()

os.system("pause")
