import carb
import omni.usd
from pxr import Gf, UsdGeom

MENU_LABEL = "Move"
MOVE_DELTA = Gf.Vec3d(100.0, 0.0, 0.0)


def _get_default_xformable(stage):
    default_prim = stage.GetDefaultPrim()
    if default_prim and default_prim.IsValid() and UsdGeom.Xformable(default_prim):
        return default_prim

    for prim in stage.Traverse():
        if prim.GetPath() == "/":
            continue
        if UsdGeom.Xformable(prim):
            return prim
    return None


def _move_prim(prim, delta_vec):
    xformable = UsdGeom.Xformable(prim)
    if not xformable:
        carb.log_warn(f"[omniverse_learning.tools] Prim is not Xformable: {prim.GetPath()}")
        return

    translate_op = None
    for op in xformable.GetOrderedXformOps():
        if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
            translate_op = op
            break

    if translate_op is None:
        translate_op = xformable.AddTranslateOp()
        current = Gf.Vec3d(0.0, 0.0, 0.0)
    else:
        current = translate_op.Get() or Gf.Vec3d(0.0, 0.0, 0.0)

    if isinstance(current, Gf.Vec3f):
        delta = Gf.Vec3f(delta_vec[0], delta_vec[1], delta_vec[2])
    else:
        delta = Gf.Vec3d(delta_vec[0], delta_vec[1], delta_vec[2])

    translate_op.Set(current + delta)


def _get_target_prim(stage):
    selection = omni.usd.get_context().get_selection()
    selected_paths = selection.get_selected_prim_paths()
    if selected_paths:
        prim = stage.GetPrimAtPath(selected_paths[0])
        while prim and prim.IsValid():
            if UsdGeom.Xformable(prim):
                return prim
            prim = prim.GetParent()

    prim = stage.GetPrimAtPath("/World/Chair")
    if prim and prim.IsValid():
        return prim

    return _get_default_xformable(stage)


def run():
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        carb.log_warn("[omniverse_learning.tools] No open stage found.")
        return

    selection = omni.usd.get_context().get_selection()
    carb.log_info(
        f"[omniverse_learning.tools] Selected prims: {selection.get_selected_prim_paths()}"
    )
    prim = _get_target_prim(stage)

    if not prim or not prim.IsValid():
        carb.log_warn("[omniverse_learning.tools] No Xformable prim found to move.")
        return

    carb.log_info(
        f"[omniverse_learning.tools] Moving prim: {prim.GetPath()} in stage "
        f"{stage.GetRootLayer().identifier}"
    )
    _move_prim(prim, MOVE_DELTA)
    carb.log_info(f"[omniverse_learning.tools] Moved prim: {prim.GetPath()}")
