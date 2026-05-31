import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nte import generate_signature

params = {
    'roleId': '218025001005',
    'gameId': '1289',
}
print(generate_signature(params))
