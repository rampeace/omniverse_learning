import importlib
import pkgutil

import omni.ext
import omni.kit.menu.utils as menu_utils


# Functions and vars are available to other extension as usual in python: `example.python_ext.some_public_function(x)`
def some_public_function(x: int):
    print("[omniverse_learning.tools] some_public_function was called with x: ", x)
    return x ** x


# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class Omniverse_learningToolsExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        print("[omniverse_learning.tools] omniverse_learning tools startup")
        self._menu_items = []
        self._register_run_menu_items()

    def _register_run_menu_items(self):
        try:
            import omniverse_learning.tools.actions as actions_pkg
        except Exception as exc:
            print(f"[omniverse_learning.tools] Failed to import actions package: {exc}")
            return

        # Discover action modules under omniverse_learning.tools.actions.
        for module_info in pkgutil.iter_modules(actions_pkg.__path__):
            if module_info.ispkg:
                continue

            module_name = f"{actions_pkg.__name__}.{module_info.name}"
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                print(f"[omniverse_learning.tools] Failed to import {module_name}: {exc}")
                continue

            run_fn = getattr(module, "run", None)
            if not callable(run_fn):
                continue

            label = getattr(
                module,
                "MENU_LABEL",
                module_info.name.replace("_", " ").title(),
            )
            self._menu_items.append(
                menu_utils.MenuItemDescription(name=label, onclick_fn=run_fn)
            )

        if self._menu_items:
            menu_utils.add_menu_items(self._menu_items, "Run")
        else:
            print("[omniverse_learning.tools] No actions found to register in Run menu.")

    def on_shutdown(self):
        if self._menu_items:
            menu_utils.remove_menu_items(self._menu_items, "Run")
            self._menu_items = []
        print("[omniverse_learning.tools] omniverse_learning tools shutdown")
