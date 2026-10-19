def registration_email_text(name: str):
    return f"""
Hello {name},

Your registration has been completed successfully.

Welcome to Final Whistle.

Regards,
Final Whistle Team
""".strip()


def login_email_text(name: str):
    return f"""
Hello {name},

You have successfully logged in to your account.

If this was not you, please contact support immediately.

Regards,
Final Whistle Team
""".strip()


def login_otp_email_text(name: str, otp: str):
    return f"""
Hello {name},

Your login verification OTP is: {otp}

Please do not share this OTP with anyone.

Regards,
Final Whistle Team
""".strip()