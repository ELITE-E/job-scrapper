from fastapi import Request


def request_key_builder(
    func,
    namespace: str = "",
    *,
    request: Request = None,
    response=None,
    **kwargs,
) -> str:
    query_params = "&".join(
        f"{k}={v}" for k, v in sorted(request.query_params.items())
    )

    return f"{namespace}:{request.method}:{request.url.path}?{query_params}"