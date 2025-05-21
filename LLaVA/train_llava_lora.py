#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from llava.train.train import train

def main():
    # 设置训练参数
    args = {
        "lora_enable": True,
        "lora_r": 32,
        "lora_alpha": 64,
        "mm_projector_lr": 1e-5,
        "model_name_or_path": "./checkpoints/llava-v1.5-7b/",
        "version": "v1",
        "data_path": "./playground/data/test/train_llava.json",
        "image_folder": "./playground/data/test/images",
        "vision_tower": "./checkpoints/clip-vit-large-patch14-336",
        "mm_projector_type": "mlp2x_gelu",
        "mm_vision_select_layer": -2,
        "mm_use_im_start_end": False,
        "mm_use_im_patch_token": False,
        "image_aspect_ratio": "pad",
        "group_by_modality_length": True,
        "fp16": True,
        "bf16": False,
        "output_dir": "./checkpoints/llava-v1.5-7b-finetune-lora",
        "num_train_epochs": 1,
        "per_device_train_batch_size": 1,
        "per_device_eval_batch_size": 1,
        "gradient_accumulation_steps": 8,
        "evaluation_strategy": "no",
        "save_strategy": "steps",
        "save_steps": 500,
        "save_total_limit": 1,
        "learning_rate": 1e-4,
        "weight_decay": 0.,
        "warmup_ratio": 0.03,
        "lr_scheduler_type": "cosine",
        "logging_steps": 10,
        "model_max_length": 512,
        "gradient_checkpointing": True,
        "dataloader_num_workers": 0,
        "lazy_preprocess": True,
        # "load_in_8bit": True,
        # "bnb_4bit": False,
        # "device_map": "auto",
        "report_to": "none"
    }
    
    # 将字典转换为命令行参数形式
    cmd_args = []
    for k, v in args.items():
        if isinstance(v, bool):
            cmd_args.append(f"--{k}")
            if not v:  # 如果是False，添加False作为值
                cmd_args.append("False")
        else:
            cmd_args.append(f"--{k}")
            cmd_args.append(str(v))
    
    # 保存原始命令行参数
    original_argv = sys.argv.copy()
    
    # 替换为我们的参数
    sys.argv = [sys.argv[0]] + cmd_args
    
    # 调用训练函数，不使用flash attention
    try:
        train()  # 移除了flash attention参数
        print("训练完成！")
    except Exception as e:
        print(f"训练过程中出现错误: {e}")
    finally:
        # 恢复原始命令行参数
        sys.argv = original_argv

if __name__ == "__main__":
    print("开始LLaVA LoRA训练...")
    main()