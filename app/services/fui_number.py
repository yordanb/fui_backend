from datetime import datetime


def generate_fui_number():
    now = datetime.now()

    return (
        f"FUI-"
        f"{now.strftime('%Y%m%d')}-"
        f"{now.strftime('%H%M%S')}"
    )
