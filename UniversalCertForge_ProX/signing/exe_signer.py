import subprocess

def sign_exe(exe_path, cert_path, timestamp_url=None):
    try:
        command = [
            "osslsigncode", "sign",
            "-certs", cert_path,
            "-in", exe_path,
            "-out", exe_path.replace(".exe", "_signed.exe")
        ]
        if timestamp_url:
            command += ["-t", timestamp_url]
        subprocess.run(command, check=True)
        return True, "EXE signed successfully."
    except Exception as e:
        return False, f"Error signing EXE: {str(e)}"

