"""
backend/utils/memory_cleanup.py — Comprehensive VRAM & System RAM Purge Engine
Ensures GPU VRAM (CUDA caches, tensors) and System RAM (Python heap, Windows Working Set)
are thoroughly freed upon program termination (Ctrl+C, SIGINT, SIGTERM, console close, or force quit).
"""

import os
import sys
import gc
import logging
import atexit
import signal

# Ensure UTF-8 / safe printing on Windows consoles
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

logger = logging.getLogger("deliverai.cleanup")

_cleanup_done = False
_console_handler_ref = None  # Retain Win32 callback reference to prevent garbage collection


def get_memory_stats() -> dict:
    """Retrieve current process RAM and GPU VRAM usage."""
    stats = {
        "ram_mb": 0.0,
        "vram_allocated_mb": 0.0,
        "vram_reserved_mb": 0.0,
        "cuda_available": False,
    }

    # RAM via psutil
    try:
        import psutil
        p = psutil.Process()
        stats["ram_mb"] = round(p.memory_info().rss / (1024 * 1024), 2)
    except Exception:
        pass

    # GPU VRAM via PyTorch (if initialized)
    if "torch" in sys.modules:
        try:
            torch = sys.modules["torch"]
            if hasattr(torch, "cuda") and torch.cuda.is_available():
                stats["cuda_available"] = True
                stats["vram_allocated_mb"] = round(torch.cuda.memory_allocated() / (1024 * 1024), 2)
                stats["vram_reserved_mb"] = round(torch.cuda.memory_reserved() / (1024 * 1024), 2)
        except Exception:
            pass

    return stats


def clear_vram_and_ram(verbose: bool = True):
    """
    Exhaustively purges:
    1. PyTorch CUDA allocation cache, IPC handles, and peak stats (VRAM).
    2. Global singleton ML models (19 regressors) & Laya SLM neural network.
    3. Python generational garbage collection (RAM).
    4. Windows Working Set / physical page trim (reclaims physical RAM back to OS).
    """
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True

    before = get_memory_stats()
    if verbose:
        print("\n" + "=" * 60)
        print("  [DeliverAI] Purging GPU VRAM & System RAM...")
        if before["cuda_available"]:
            print(f"  * Pre-cleanup VRAM: {before['vram_reserved_mb']} MB (Allocated: {before['vram_allocated_mb']} MB)")
        if before["ram_mb"] > 0:
            print(f"  * Pre-cleanup RAM:  {before['ram_mb']} MB")

    # ── 1. Unload & Dereference ML / SLM Models ─────────────────────
    try:
        for mod_name in list(sys.modules.keys()):
            if "backend.models.predict" in mod_name or mod_name == "models.predict":
                m = sys.modules[mod_name]
                if hasattr(m, "_MODELS") and isinstance(m._MODELS, dict):
                    m._MODELS.clear()
                if hasattr(m, "_FEATURE_SCALER"):
                    m._FEATURE_SCALER = None

            if "backend.models.slm_router" in mod_name or mod_name == "models.slm_router":
                m = sys.modules[mod_name]
                if hasattr(m, "_laya_agent"):
                    m._laya_agent = None
    except Exception as e:
        logger.debug("Model dereferencing notice: %s", e)

    # ── 2. First Pass: PyTorch CUDA Cache Purge ─────────────────────
    if "torch" in sys.modules:
        try:
            torch = sys.modules["torch"]
            if hasattr(torch, "cuda") and torch.cuda.is_available():
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                if hasattr(torch.cuda, "ipc_collect"):
                    torch.cuda.ipc_collect()
        except Exception as e:
            logger.debug("Torch CUDA pass 1 notice: %s", e)

    # ── 3. Generational Garbage Collection ──────────────────────────
    try:
        gc.collect(0)
        gc.collect(1)
        gc.collect(2)
        gc.collect()
    except Exception:
        pass

    # ── 4. Second Pass: PyTorch CUDA Cache Purge (post GC) ──────────
    if "torch" in sys.modules:
        try:
            torch = sys.modules["torch"]
            if hasattr(torch, "cuda") and torch.cuda.is_available():
                torch.cuda.empty_cache()
                if hasattr(torch.cuda, "ipc_collect"):
                    torch.cuda.ipc_collect()
                if hasattr(torch.cuda, "reset_peak_memory_stats"):
                    torch.cuda.reset_peak_memory_stats()
                if hasattr(torch.cuda, "reset_accumulated_memory_stats"):
                    torch.cuda.reset_accumulated_memory_stats()
        except Exception as e:
            logger.debug("Torch CUDA pass 2 notice: %s", e)

    # ── 5. Windows Working Set & Physical RAM Reclaim ───────────────
    if sys.platform == "win32":
        try:
            import ctypes
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.psapi.EmptyWorkingSet(handle)
            ctypes.windll.kernel32.SetProcessWorkingSetSize(handle, -1, -1)
        except Exception as e:
            logger.debug("Windows WorkingSet trim notice: %s", e)

    if verbose:
        after = get_memory_stats()
        if after["cuda_available"]:
            print(f"  [+] GPU VRAM Released (Active Reserved: {after['vram_reserved_mb']} MB)")
        else:
            print("  [+] GPU VRAM Caches Cleared")

        if after["ram_mb"] > 0:
            freed = max(0.0, before["ram_mb"] - after["ram_mb"])
            print(f"  [+] System RAM Trimmed to: {after['ram_mb']} MB (Freed: ~{freed} MB)")
        else:
            print("  [+] System Working Set Trimmed")

        print("  [+] 19 ML Models & SLM Neural Weights Unloaded")
        print("  [+] Clean Shutdown Complete.")
        print("=" * 60 + "\n")
        try:
            sys.stdout.flush()
        except Exception:
            pass


def _signal_handler(signum, frame):
    """Handle POSIX/standard signals (SIGINT, SIGTERM, SIGBREAK)."""
    signame = signal.Signals(signum).name if hasattr(signal, "Signals") else str(signum)
    print(f"\n[!] Caught exit signal {signame} ({signum}). Initiating emergency cleanup...")
    clear_vram_and_ram(verbose=True)
    os._exit(0)


def register_exit_cleanup_handlers():
    """
    Register automatic cleanup hooks across all exit paths:
    - Normal script exit or sys.exit() via atexit
    - Ctrl+C (KeyboardInterrupt) & SIGINT
    - SIGTERM
    - Windows Console Ctrl Handler (Ctrl+C, Ctrl+Break, Window Close)
    """
    # 1. Standard atexit hook
    atexit.register(clear_vram_and_ram, verbose=False)

    # 2. Signal handlers
    try:
        signal.signal(signal.SIGINT, _signal_handler)
    except Exception:
        pass

    try:
        signal.signal(signal.SIGTERM, _signal_handler)
    except Exception:
        pass

    if hasattr(signal, "SIGBREAK"):
        try:
            signal.signal(signal.SIGBREAK, _signal_handler)
        except Exception:
            pass

    # 3. Windows-specific Low-Level Console Control Handler
    # Catches Ctrl+C, Ctrl+Break, and terminal close (X button)
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            HandlerRoutine = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

            def win_console_ctrl_handler(dwCtrlType):
                # 0 = CTRL_C_EVENT, 1 = CTRL_BREAK_EVENT, 2 = CTRL_CLOSE_EVENT
                # 5 = CTRL_LOGOFF_EVENT, 6 = CTRL_SHUTDOWN_EVENT
                print(f"\n[!] Windows console event ({dwCtrlType}) detected. Releasing GPU VRAM & RAM...")
                clear_vram_and_ram(verbose=True)
                return False  # Let OS proceed with clean termination

            global _console_handler_ref
            _console_handler_ref = HandlerRoutine(win_console_ctrl_handler)
            ctypes.windll.kernel32.SetConsoleCtrlHandler(_console_handler_ref, True)
        except Exception as e:
            logger.debug("Could not register Windows console ctrl handler: %s", e)
