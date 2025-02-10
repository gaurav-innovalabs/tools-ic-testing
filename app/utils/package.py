
def install_package(package: str) -> bool:
    _flag = False
    import subprocess

    try:
        result = subprocess.run(
            ["poetry", "add", package, "--group", "dev"], check=True, capture_output=True, text=True
        )
        print(result.stdout)
        print(result.stderr)
        _flag = True
    except Exception as e:
        print(f"Error occurred while installing package '{package}': {e!s}")
    finally:
        print("------------------------------------------------------------------------")
    return _flag
