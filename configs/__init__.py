from . import n_body_dynamics_EPNS
from . import n_body_dynamics_PNS
from . import n_body_dynamics_PNS_MLP
from . import cell_dynamics_EPNS
from . import cell_dynamics_PNS


class Config():
    def __init__(self, config_dict):
        self.config_dict = config_dict

def load_config(cfg_str, state_dict=None):
    cfg = globals()[cfg_str]
    cfg_dict = dict(cfg.config_dict)

    if state_dict is not None:  # replace state dict str with new state dict
        old = cfg_dict['experiment']['state_dict_fname']
        new_state_dict_pointer = {'state_dict_fname': state_dict}
        cfg_dict['experiment'] = new_state_dict_pointer
        print(f'changed state dict from {old} \t\t\t to {state_dict} \t\t\t in {cfg_str}!')

    cfg = Config(config_dict=cfg_dict)
    return cfg