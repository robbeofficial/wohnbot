import logging

import importlib

logger = logging.getLogger(__name__)

def dynamic_import(site):
    module_name = f"wohnbot.modules.{site}"
    logger.info(f"Importing {module_name}")
    return importlib.import_module(module_name)