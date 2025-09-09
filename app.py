import gradio as gr
import torch
from diffusers import StableDiffusionXLPipeline, DiffusionPipeline, FlowMatchEulerDiscreteScheduler, QwenImageEditPipeline
import math
import os

# Define the cache directory for the models
CACHE_DIR = "/mnt/my-models-volume"
os.makedirs(CACHE_DIR, exist_ok=True)

# Global variable to cache the pipeline
pipeline_cache = None
current_model_name = None

def get_pipeline(model_name):
    global pipeline_cache, current_model_name
    if current_model_name == model_name and pipeline_cache is not None:
        return pipeline_cache

    # Common scheduler for Qwen models
    scheduler_config = {
        "base_image_seq_len": 256,
        "base_shift": math.log(3),
        "invert_sigmas": False,
        "max_image_seq_len": 8192,
        "max_shift": math.log(3),
        "num_train_timesteps": 1000,
        "shift": 1.0,
        "shift_terminal": None,
        "stochastic_sampling": False,
        "time_shift_type": "exponential",
        "use_beta_sigmas": False,
        "use_dynamic_shifting": True,
        "use_exponential_sigmas": False,
        "use_karras_sigmas": False,
    }
    scheduler = FlowMatchEulerDiscreteScheduler.from_config(scheduler_config)

    if model_name == "epicrealism":
        pipeline = StableDiffusionXLPipeline.from_pretrained("glides/epicrealismxl", cache_dir=CACHE_DIR).to("cuda")
    elif model_name == "qwen":
        pipeline = DiffusionPipeline.from_pretrained(
            "Qwen/Qwen-Image", scheduler=scheduler, torch_dtype=torch.bfloat16, cache_dir=CACHE_DIR
        ).to("cuda")
        pipeline.load_lora_weights(
            "lightx2v/Qwen-Image-Lightning", weight_name="Qwen-Image-Lightning-8steps-V1.0.safetensors", cache_dir=CACHE_DIR
        )
    elif model_name == "qwen-edit":
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise gr.Error("Hugging Face token not found. Please attach the `huggingface-secret` to your Modal Notebook.")

        pipeline = QwenImageEditPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit", scheduler=scheduler, torch_dtype=torch.bfloat16, cache_dir=CACHE_DIR, token=hf_token
        ).to("cuda")
        
        # Load the mandatory lightning LoRA
        pipeline.load_lora_weights(
            "lightx2v/Qwen-Image-Lightning", weight_name="Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors", cache_dir=CACHE_DIR, adapter_name="lightning"
        )

        # Load optional LoRAs
        lora_repo = "ibuildproducts/loras"
        pipeline.load_lora_weights(lora_repo, weight_name="qwen_image_edit_remove-clothing_v1.0.safetensors", cache_dir=CACHE_DIR, adapter_name="remove_clothing", token=hf_token)
        pipeline.load_lora_weights(lora_repo, weight_name="bumpynipples1.safetensors", cache_dir=CACHE_DIR, adapter_name="bumpy_nipples", token=hf_token)
        pipeline.load_lora_weights(lora_repo, weight_name="p0ssy_lora_v1.safetensors", cache_dir=CACHE_DIR, adapter_name="pussy_lora", token=hf_token)

    else:
        raise ValueError("Unknown model name")
    
    pipeline_cache = pipeline
    current_model_name = model_name
    return pipeline

def generate_epicrealism(prompt, negative_prompt, width, height, sample_steps):
    pipeline = get_pipeline("epicrealism")
    return pipeline(prompt=prompt, negative_prompt=negative_prompt, width=width, height=height, num_inference_steps=sample_steps).images[0]

def generate_qwen(prompt, negative_prompt, width, height, sample_steps):
    pipeline = get_pipeline("qwen")
    return pipeline(prompt=prompt, negative_prompt=negative_prompt, width=width, height=height, num_inference_steps=sample_steps, true_cfg_scale=1.0).images[0]

def generate_qwen_edit(image, prompt, negative_prompt, sample_steps, lora_name, lora_strength):
    if image is None:
        raise gr.Error("Please upload an image to edit.")
    pipeline = get_pipeline("qwen-edit")

    # Dynamically set the active LoRAs and their weights
    if lora_name == "None":
        pipeline.set_adapters(["lightning"], adapter_weights=[1.0])
    else:
        pipeline.set_adapters(["lightning", lora_name], adapter_weights=[1.0, lora_strength])

    return pipeline(image=image, prompt=prompt, negative_prompt=negative_prompt, num_inference_steps=sample_steps, true_cfg_scale=4.0, generator=torch.manual_seed(0)).images[0]


with gr.Blocks() as interface:
    with gr.Tabs():
        with gr.TabItem("epicrealism xl"):
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        prompt_epic = gr.Textbox(label="Prompt", info="What do you want?", value="A perfectly red apple, 32k HDR, studio lighting", lines=4, interactive=True)
                        negative_prompt_epic = gr.Textbox(label="Negative Prompt", info="What do you want to exclude from the image?", value="ugly, low quality", lines=4, interactive=True)
                    with gr.Column():
                        generate_button_epic = gr.Button("Generate")
                        output_epic = gr.Image()
                with gr.Row():
                    with gr.Accordion(label="Advanced Settings", open=False):
                        with gr.Row():
                            with gr.Column():
                                width_epic = gr.Slider(label="Width", info="The width in pixels of the generated image.", value=1024, minimum=128, maximum=4096, step=64, interactive=True)
                                height_epic = gr.Slider(label="Height", info="The height in pixels of the generated image.", value=1024, minimum=128, maximum=4096, step=64, interactive=True)
                            with gr.Column():
                                sampling_steps_epic = gr.Slider(label="Sampling Steps", info="The number of denoising steps.", value=20, minimum=4, maximum=50, step=1, interactive=True)
            generate_button_epic.click(fn=generate_epicrealism, inputs=[prompt_epic, negative_prompt_epic, width_epic, height_epic, sampling_steps_epic], outputs=[output_epic])

        with gr.TabItem("qwen-image + lightning"):
            with gr.Column():
                with gr.Row():
                    with gr.Column():
                        prompt_qwen = gr.Textbox(label="Prompt", info="What do you want?", value="a tiny astronaut hatching from an egg on the moon, Ultra HD, 4K, cinematic composition.", lines=4, interactive=True)
                        negative_prompt_qwen = gr.Textbox(label="Negative Prompt", info="What do you want to exclude from the image?", value=" ", lines=4, interactive=True)
                    with gr.Column():
                        generate_button_qwen = gr.Button("Generate")
                        output_qwen = gr.Image()
                with gr.Row():
                    with gr.Accordion(label="Advanced Settings", open=False):
                        with gr.Row():
                            with gr.Column():
                                width_qwen = gr.Slider(label="Width", info="The width in pixels of the generated image.", value=1024, minimum=128, maximum=4096, step=64, interactive=True)
                                height_qwen = gr.Slider(label="Height", info="The height in pixels of the generated image.", value=1024, minimum=128, maximum=4096, step=64, interactive=True)
                            with gr.Column():
                                sampling_steps_qwen = gr.Slider(label="Sampling Steps", info="The number of denoising steps.", value=8, minimum=1, maximum=20, step=1, interactive=True)
            generate_button_qwen.click(fn=generate_qwen, inputs=[prompt_qwen, negative_prompt_qwen, width_qwen, height_qwen, sampling_steps_qwen], outputs=[output_qwen])

        with gr.TabItem("qwen-image-edit + lightning"):
            with gr.Row():
                with gr.Column():
                    input_image_edit = gr.Image(type="pil", label="Input Image")
                    prompt_edit = gr.Textbox(label="Prompt", info="What do you want to change?", value="Change the rabbit's color to purple, with a flash light background.", lines=3, interactive=True)
                    negative_prompt_edit = gr.Textbox(label="Negative Prompt", info="What do you want to exclude from the image?", value=" ", lines=3, interactive=True)
                    
                    with gr.Accordion(label="Optional LoRA", open=True):
                        lora_name_edit = gr.Dropdown(
                            label="Select Optional LoRA", 
                            choices=["None", "remove_clothing", "bumpy_nipples", "pussy_lora"], 
                            value="None", 
                            interactive=True
                        )
                        lora_strength_edit = gr.Slider(
                            label="LoRA Strength", 
                            info="Adjust the influence of the optional LoRA.", 
                            value=1.0, 
                            minimum=0.0, 
                            maximum=2.0, 
                            step=0.1, 
                            interactive=True
                        )

                    sampling_steps_edit = gr.Slider(label="Sampling Steps", info="The number of denoising steps.", value=8, minimum=1, maximum=20, step=1, interactive=True)
                    generate_button_edit = gr.Button("Generate")
                with gr.Column():
                    output_edit = gr.Image()
            generate_button_edit.click(fn=generate_qwen_edit, inputs=[input_image_edit, prompt_edit, negative_prompt_edit, sampling_steps_edit, lora_name_edit, lora_strength_edit], outputs=[output_edit])


if __name__ == "__main__":
    interface.launch(share=True)
