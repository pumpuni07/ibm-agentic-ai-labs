"""Step 12 — Capstone assembly: requirement agent + handoff + calculator,
constructed end-to-end (execution requires a live model backend)."""
from importlib import import_module

def build() :
    build_system = import_module("10_handoff_multi_agent").build_system
    return build_system()

if __name__ == "__main__":
    print("Full system assembled:", type(build()).__name__)
