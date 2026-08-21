"""Small, dependency-free browser security protections for Django responses."""


class SecurityHeadersMiddleware:
    """Attach restrictive headers without changing API response bodies.

    Vue escapes interpolated text by default, and this Content-Security-Policy
    limits the impact if a future template accidentally introduces an XSS flaw.
    Inline styles remain allowed because the current frontend uses Tailwind's
    generated utility styles; scripts are intentionally never allowed inline.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers.setdefault(
            'Content-Security-Policy',
            "default-src 'self'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "img-src 'self' data: blob:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "connect-src 'self';",
        )
        response.headers.setdefault('Permissions-Policy', 'camera=(), geolocation=(), microphone=(), payment=(), usb=()')
        response.headers.setdefault('Cross-Origin-Opener-Policy', 'same-origin')
        response.headers.setdefault('Cross-Origin-Resource-Policy', 'same-origin')
        return response
