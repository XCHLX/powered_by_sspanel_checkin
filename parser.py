from utils import is_url, is_cookie, parse_cookie


def parse_accounts(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    result = {}
    current = None
    i = 0

    while i < len(lines):
        line = lines[i]

        if is_url(line):
            current = line
            result[current] = []
            i += 1
            continue

        if current:
            acc = {
                "username": None,
                "password": None,
                "cookie": None,
            }

            if is_cookie(line):
                acc["cookie"] = parse_cookie(line)
                result[current].append(acc)
                i += 1
                continue

            if i + 1 < len(lines) and not is_url(lines[i + 1]):
                acc["username"] = line
                acc["password"] = lines[i + 1]

                if is_cookie(acc["password"]):
                    acc["cookie"] = parse_cookie(acc["password"])

                result[current].append(acc)
                i += 2
                continue

        i += 1

    return result
