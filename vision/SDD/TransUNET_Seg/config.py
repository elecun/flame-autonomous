from easydict import EasyDict

cfg = EasyDict()
cfg.batch_size = 4
cfg.epoch = 1000
cfg.learning_rate = 2e-2
cfg.momentum = 0.9
cfg.weight_decay = 1e-4
cfg.patience = 25
cfg.inference_threshold = 0.2

cfg.transunet = EasyDict()
cfg.transunet.img_dim = 640
cfg.transunet.in_channels = 3
cfg.transunet.out_channels = 128
cfg.transunet.head_num = 32
cfg.transunet.mlp_dim = 1024
cfg.transunet.block_num = 8
cfg.transunet.patch_dim = 16
cfg.transunet.class_num = 1
