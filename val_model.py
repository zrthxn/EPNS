import os
import argparse
import numpy as np
import torch
from torch import nn
from tqdm import tqdm
from configs import load_config


@torch.no_grad
def validate_model(state_dict, config: dict, pred_stepsize = 1):
    if 'limit_num_data_points_to' in config.keys():
        num_data_points = config['limit_num_data_points_to']
    else:
        num_data_points = np.inf

    _, _, test_dataloader = config['dataset'].get_data_loaders(
        config, 
        additional_loaders=[],
        limit_num_data_points_to=num_data_points)
    
    model: nn.Module = config['model'](**config['model_params'], 
                                       im_dim=config['im_dim'],
                                       dynamic_channels=config['dynamic_channels'], 
                                       pred_stepsize=config['pred_stepsize'])
    model.load_state_dict(state_dict)
    device = config['device']
    model.to(device)
    model = model.eval()
    
    # initialize lazy layers by calling a fw pass:
    one_example_batch = next(iter(test_dataloader))  #(bs, c, t, h, w)
    model(one_example_batch[:, :, 0].to(device), one_example_batch[:, :, 1].to(device))
    
    for rx, sample in tqdm(enumerate(test_dataloader)):
        #  shape of data: (bs, channels, time, spatial_x, spatial_y)
        end_of_sim_time = sample.size(2) - pred_stepsize
        x = sample[range(sample.size(0)), :, 0].to(device)
        
        save_fnames = [f"run_{(rx * sample.size(0)) + j}.npy" for j in range(sample.size(0))]
        videos = [[] for _ in range(sample.size(0))]
        
        for _ in range(end_of_sim_time):
            # y_pred: (bs, channels, H, W)
            _, _, y_pred, *_ = model(x)
            x = y_pred[range(sample.size(0)), :].to(device)
            
            for j in range(y_pred.size(0)):
                frame = y_pred[j, 1, :, :].cpu().numpy()
                videos[j].append(frame)
        
        for fname, video in zip(save_fnames, videos):    
            np.save(os.path.join(config["save_path"], fname), np.array(video))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Training config')
    parser.add_argument('config', type=str, help='config file path')
    parser.add_argument('state_dict', type=str, help='state dict path')
    
    args, remaining_args = parser.parse_known_args()
    config = load_config(args.config).config_dict

    def parse_to_int_or_float(str):
        try:
            return int(str)
        except ValueError:
            return float(str)

    for arg in remaining_args:  # any argument given as --kwarg=x after the config file will be parsed
        # and added to the config dict or overwrite the parameters in the config dict it they are already present
        arg: str
        arg = arg.strip('-')
        k, v = arg.split('=')
        try:
            v = parse_to_int_or_float(v)
        except:
            v = v
        if k in config.keys():
            config[k] = v
            print(f'set {k} to {v} in main config!', flush=True)
        elif k in config['model_params'].keys():
            config['model_params'][k] = v
            print(f'set {k} to {v} in model_params config!', flush=True)
        elif k in config['opt_kwargs'].keys():
            config['opt_kwargs'][k] = v
            print(f'set {k} to {v} in optimizer parameters config!', flush=True)
        else:
            config[k] = v
            print(f'did not find {k} in main or model param config keys -- set {k} to {v} in main config nevertheless', flush=True)

        if k != 'data_directory' and k != 'starting_weight_state_dict':
            # we update the state dict name with the command line params
            old_state_dict_fname = config['experiment']['state_dict_fname']
            config['experiment']['state_dict_fname'] = old_state_dict_fname[:-3] + f'--{k[:5]}{v}' + old_state_dict_fname[-3:]

    state_dict = torch.load(args.state_dict, map_location=config['device'])
    validate_model(state_dict, config)
