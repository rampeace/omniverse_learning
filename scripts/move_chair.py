#!/usr/bin/env python
"""
Move a USD prim by a small vector and write a new USD file.

Usage examples:
  python scripts/move_chair.py --usd "C:\Projects\omniverse_learning\assets\Chair\Chair.usd" --list
  python scripts/move_chair.py --usd "C:\Projects\omniverse_learning\assets\Chair\Chair.usd" --prim "/World/Chair"
  python scripts/move_chair.py --usd "...\Chair.usd" --prim "/World/Chair" --dx 0.1 --dy 0 --dz -0.05
"""

import argparse
import os
from pxr import Usd, UsdGeom, Gf


def list_prims(stage):
    for prim in stage.Traverse():
        print(prim.GetPath())

def get_primary_prim_path(usd_path):
    stage = Usd.Stage.Open(usd_path)
    if stage is None:
        raise RuntimeError(f"Failed to open USD: {usd_path}")

    prim = pick_default_prim(stage)
    if prim is None:
        raise RuntimeError("No Xformable prims found in USD.")

    return str(prim.GetPath())


def pick_default_prim(stage):
    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.IsValid() and UsdGeom.Xformable(default_prim):
        return default_prim

    for prim in stage.Traverse():
        if prim.GetPath() == "/":
            continue
        if UsdGeom.Xformable(prim):
            return prim
    return None


def move_prim(prim, delta_vec):
    xformable = UsdGeom.Xformable(prim)
    if not xformable:
        raise ValueError(f"Prim is not Xformable: {prim.GetPath()}")

    translate_op = None
    for op in xformable.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            translate_op = op
            break

    if translate_op is None:
        translate_op = xformable.AddTranslateOp()
        current = Gf.Vec3d(0.0, 0.0, 0.0)
    else:
        current = translate_op.Get()
        if current is None:
            current = Gf.Vec3d(0.0, 0.0, 0.0)

    translate_op.Set(current + delta_vec)


def main():
    parser = argparse.ArgumentParser(description="Move a USD prim by a small vector.")
    parser.add_argument("--usd", required=True, help="Path to input USD file.")
    parser.add_argument("--prim", help="Prim path to move, e.g. /World/Chair.")
    parser.add_argument("--dx", type=float, default=0.05, help="Delta X (default: 0.05).")
    parser.add_argument("--dy", type=float, default=0.0, help="Delta Y (default: 0.0).")
    parser.add_argument("--dz", type=float, default=0.0, help="Delta Z (default: 0.0).")
    parser.add_argument("--output", help="Output USD path. Defaults to *_moved.usd.")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the input USD file.")
    parser.add_argument("--list", action="store_true", help="List prim paths and exit.")
    args = parser.parse_args()

    stage = Usd.Stage.Open(args.usd)
    if stage is None:
        raise RuntimeError(f"Failed to open USD: {args.usd}")

    if args.list:
        list_prims(stage)
        return

    if args.prim:
        prim = stage.GetPrimAtPath(args.prim)
        if not prim or not prim.IsValid():
            raise ValueError(f"Prim not found: {args.prim}")
    else:
        prim_path = get_primary_prim_path(args.usd)
        prim = stage.GetPrimAtPath(prim_path)
        print(f"No --prim provided. Using default/first Xformable prim: {prim_path}")

    move_prim(prim, Gf.Vec3d(args.dx, args.dy, args.dz))

    if args.in_place:
        stage.GetRootLayer().Save()
        print(f"Saved in place: {args.usd}")
        return

    if args.output:
        output_path = args.output
    else:
        base, ext = os.path.splitext(args.usd)
        output_path = f"{base}_moved{ext or '.usd'}"

    stage.GetRootLayer().Export(output_path)
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
