"""
sitecustomize.py - disable TLS certificate verification for the whole container.

Patching the two httpx clients in models.py was not enough. httpx, requests,
urllib3, the openai client and langchain each build their own SSLContext, and a
lab that keeps tripping over a corporate TLS-inspecting proxy needs this to hold
for all of them without chasing each call site.

This is a deliberate, lab-only decision. It means the agent cannot detect a
man-in-the-middle on its API traffic. That is acceptable for a throwaway lab and
would be unacceptable anywhere else.

Set LAB_NO_TLS_VERIFY=0 to restore verification.
"""
import os
import ssl

if os.environ.get("LAB_NO_TLS_VERIFY", "1") != "0":
    # 1. the factory requests/urllib3 use for their default clients
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        ssl._create_stdlib_context = ssl._create_unverified_context
    except Exception:
        pass

    # 2. any explicit ssl.create_default_context(), which is what httpx,
    #    langchain and the openai client all call
    _orig = ssl.create_default_context

    def _no_verify(*args, **kwargs):
        kwargs["verify_mode"] = ssl.CERT_NONE
        kwargs["check_hostname"] = False
        try:
            ctx = _orig(*args, **kwargs)
        except TypeError:
            ctx = _orig()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    ssl.create_default_context = _no_verify

    # 3. and anything that constructs SSLContext directly
    _orig_ctx = ssl.SSLContext.__init__

    def _ctx_init(self, *args, **kwargs):
        kwargs["verify_mode"] = ssl.CERT_NONE
        kwargs.setdefault("check_hostname", False)
        try:
            _orig_ctx(self, *args, **kwargs)
        except TypeError:
            _orig_ctx(self)
        self.check_hostname = False
        self.verify_mode = ssl.CERT_NONE

    ssl.SSLContext.__init__ = _ctx_init



    # 4. urllib3 is the stubborn one. It builds its own context and then
    #    explicitly sets verify_mode afterwards, overriding everything above,
    #    and it binds the factory into urllib3.connection at import time. So the
    #    patch must land AFTER urllib3 is imported. Hook __import__ to do that
    #    at the right moment.
    #
    #    The hook is re-entrant by nature: _patch_urllib3() itself calls
    #    __import__, which is the patched one. Without a guard that recurses and
    #    the container hangs on startup, so _BUSY gates it.
    _BUSY = [False]

    def _patch_urllib3():
        if _BUSY[0]:
            return
        _BUSY[0] = True
        try:
            import urllib3.util.ssl_ as _u3s

            _cur = _u3s.create_urllib3_context
            if getattr(_cur, "_lab_patched", False):
                return

            def _u3(*args, **kwargs):
                ctx = _cur(*args, **kwargs)
                try:
                    ctx.check_hostname = False
                    ctx.verify_mode = ssl.CERT_NONE
                except Exception:
                    pass
                return ctx

            _u3._lab_patched = True
            _u3s.create_urllib3_context = _u3
            import sys
            for mod in ("urllib3", "urllib3.connection", "urllib3.poolmanager"):
                m = sys.modules.get(mod)
                if m is not None and hasattr(m, "create_urllib3_context"):
                    m.create_urllib3_context = _u3
        except Exception:
            pass
        finally:
            _BUSY[0] = False

    _patch_urllib3()

    import builtins

    _real_import = builtins.__import__

    def _import_hook(name, *args, **kwargs):
        mod = _real_import(name, *args, **kwargs)
        if name == "urllib3" or name.startswith("urllib3."):
            _patch_urllib3()
        return mod

    builtins.__import__ = _import_hook
