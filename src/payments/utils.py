import hashlib


def generate_signature(data: dict, secret: str) -> str:

    sorted_string = "".join(str(v) for k, v in sorted(data.items()) if v is not None)
    hashed_string = hashlib.sha1((sorted_string + secret).encode('utf-8')).hexdigest()
    return hashed_string
