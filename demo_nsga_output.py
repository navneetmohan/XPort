"""
XPort — NSGA-II Multi-Objective Portfolio Optimizer Demonstration Script Launcher
"""
import subprocess
import sys

if __name__ == "__main__":
    cmd = [sys.executable, "-m", "backend.demo_nsga_output"]
    sys.exit(subprocess.call(cmd))
