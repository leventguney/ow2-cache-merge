import os
import sys
# insert parent directory of this file to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ow2_cache_merge.main import CacheMerger

 
def test_load_config(mocker):
    mocker.patch("builtins.input", return_value='y')
    c = CacheMerger()
    c._load_config()
    assert 'repos' in c.config.keys()