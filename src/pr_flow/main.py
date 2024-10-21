#!/usr/bin/env python
import asyncio
from .flow import run_flow, plot_flow

def main():
    asyncio.run(run_flow())


def plot():
    asyncio.run(plot_flow())



if __name__ == "__main__":
    main()