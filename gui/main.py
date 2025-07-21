import logging
from gui.module_test_data import ModuleTestData
import argparse
from gui.input_screen import LoadModuleInfo, TestSuite

logger = logging.getLogger(__name__)


def new_module(**kwargs):
    
    mod_data = ModuleTestData(cfg=kwargs['cfg'], dry_run=bool(int(kwargs['dry_run'])))
    win = LoadModuleInfo(mod_data)
    win.mainloop()
    win = TestSuite(mod_data)
    win.mainloop()
    
def parse_args(argv=None):
    """Parse command line arguments.
    Args:
        argv (list): List of string arguments to parse.
    Returns:
        dict: Dictionary of parameters.
    """
    parser = argparse.ArgumentParser(prog='ATLAS Module Electrical Testing', description='GUI to run electrical tests on ATLAS v1.1 and v2 modules')
    parser.add_argument('-c', '--config', dest='cfg', required=False, help='Path to config.json', default="./config.json")
    parser.add_argument('-d', "--dry-run", dest='dry_run', required=False, default=2) # 0 = FALSE (wet run), 1 = TRUE (dry run), 2 = unspecified, revert to config 
    parser.add_argument('-v', "--verbosity", dest='verb', required=False, default=20, help="Severity = [0, 10, 20, 30, 40, 50]") # TODO: fix
    args = vars(parser.parse_args(argv))
    logging.basicConfig(level=logging.DEBUG)
    return args

def main(argv=None):
    kwargs = parse_args()
    new_module(**kwargs)

if __name__ == "__main__":
    main()