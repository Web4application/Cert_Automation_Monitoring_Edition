import subprocess

def sign_apk(apk_path, keystore_path, alias, storepass):
    try:
        command = [
            "apksigner", "sign",
            "--ks", keystore_path,
            "--ks-key-alias", alias,
            "--ks-pass", f"pass:{storepass}",
            apk_path
        ]
        subprocess.run(command, check=True)
        return True, "APK signed successfully."
    except Exception as e:
        return False, f"Error signing APK: {str(e)}"
