def _build_condition(domain):
    field, operator, value = domain
    operator = operator.lower()

    if operator in ("like", "ilike"):
        return f"{field} LIKE ?", [f"%{value}%"]

    elif operator == "=":
        return f"{field} = ?", [value]

    elif operator == "!=":
        return f"{field} <> ?", [value]

    elif operator == ">":
        return f"{field} > ?", [value]

    elif operator == ">=":
        return f"{field} >= ?", [value]

    elif operator == "<":
        return f"{field} < ?", [value]

    elif operator == "<=":
        return f"{field} <= ?", [value]

    elif operator == "in":
        if not value:
            return "1=0", []
        placeholders = ",".join(["?"] * len(value))
        return f"{field} IN ({placeholders})", list(value)

    elif operator == "not in":
        if not value:
            return "1=1", []
        placeholders = ",".join(["?"] * len(value))
        return f"{field} NOT IN ({placeholders})", list(value)

    elif operator == "is null":
        return f"{field} IS NULL", []

    elif operator == "is not null":
        return f"{field} IS NOT NULL", []

    else:
        raise ValueError(f"Operador no soportado: {operator}")


def _parse_domain(domain):
    token = domain.pop(0)

    if token == "|":
        left_sql, left_params = _parse_domain(domain)
        right_sql, right_params = _parse_domain(domain)
        return f"({left_sql} OR {right_sql})", left_params + right_params

    elif token == "&":
        left_sql, left_params = _parse_domain(domain)
        right_sql, right_params = _parse_domain(domain)
        return f"({left_sql} AND {right_sql})", left_params + right_params

    elif token == "!":
        sql, params = _parse_domain(domain)
        return f"(NOT {sql})", params

    elif isinstance(token, (list, tuple)):
        return _build_condition(token)

    else:
        raise ValueError(f"Token inválido en domain: {token}")


def _normalize_domain(domain):
    if not domain:
        return []

    if isinstance(domain[0], str) and domain[0] in ("|", "&", "!"):
        return domain

    result = domain[0]
    for cond in domain[1:]:
        result = ["&", result, cond]

    return result


def build_where_from_domain(domain):
    domain = _normalize_domain(domain)
    domain_copy = list(domain)
    sql, params = _parse_domain(domain_copy)

    return sql, params
