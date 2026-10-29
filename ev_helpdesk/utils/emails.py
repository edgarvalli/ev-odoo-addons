def normalize_emails(values: list[str] | None) -> list[str]:
    return list(
        dict.fromkeys(
            email.strip() for email in (values or []) if email and email.strip()
        )
    )
