from pathlib import Path
from maa.resource import Resource

working_dir = Path(__file__).parent
install_path = working_dir / Path("install")

def validate_resource():
    print("尝试加载资源")
    status = Resource().post_bundle(install_path / "resource" / "base").wait().succeeded
    if not status:
        print("Resource validation failed.")
        print("资源校验失败。")
        sys.exit(1)
    
    print("Resource validation succeeded.")
    print("资源校验成功。")

if __name__ == "__main__":
    validate_resource()