import gradio as gr
import torch
from diffusers import StableDiffusionXLPipeline, DiffusionPipeline, FlowMatchEulerDiscreteScheduler, QwenImageEditPipeline
import math
import os
from datetime import datetime
from PIL import Image

# Define the cache and output directories within the volume
CACHE_DIR = "/mnt/my-models-volume/models"
OUTPUT_DIR = "/mnt/my-models-volume/outputs"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
            "Qwen/Qwen-Image", scheduler=scheduler, dtype=torch.bfloat16, cache_dir=CACHE_DIR
        ).to("cuda")
        pipeline.load_lora_weights(
            "lightx2v/Qwen-Image-Lightning", weight_name="Qwen-Image-Lightning-8steps-V1.0.safetensors", cache_dir=CACHE_DIR
        )
    elif model_name == "qwen-edit":
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise gr.Error("Hugging Face token not found. Please attach the `huggingface-secret` to your Modal Notebook.")

        pipeline = QwenImageEditPipeline.from_pretrained(
            "Qwen/Qwen-Image-Edit", scheduler=scheduler, dtype=torch.bfloat16, cache_dir=CACHE_DIR, token=hf_token
        ).to("cuda")
        
        # Define all available LoRAs for this model
        loras = {
            "lightning": ("lightx2v/Qwen-Image-Lightning", "Qwen-Image-Edit-Lightning-8steps-V1.0.safetensors"),
            "remove_clothing": ("ibuildproducts/loras", "qwen_image_edit_remove-clothing_v1.0.safetensors"),
            "bumpy_nipples": ("ibuildproducts/loras", "bumpynipples1.safetensors"),
            "pussy_lora": ("ibuildproducts/loras", "p0ssy_lora_v1.safetensors"),
        }

        for name, (repo, weight) in loras.items():
            pipeline.load_lora_weights(repo, weight_name=weight, cache_dir=CACHE_DIR, adapter_name=name, token=hf_token)

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

def generate_qwen_edit(image_files, prompt, negative_prompt, sample_steps, 
                       lora1, strength1, lora2, strength2, lora3, strength3, lora4, strength4):
    if not image_files:
        raise gr.Error("Please upload at least one image to edit.")
    
    pipeline = get_pipeline("qwen-edit")
    
    # Build the list of active LoRAs and their strengths from the UI
    active_loras = []
    active_weights = []
    lora_selections = [(lora1, strength1), (lora2, strength2), (lora3, strength3), (lora4, strength4)]
    for name, strength in lora_selections:
        if name != "None":
            active_loras.append(name)
            active_weights.append(strength)

    # Set the adapters for the entire batch
    if active_loras:
        pipeline.set_adapters(active_loras, adapter_weights=active_weights)
        pipeline.enable_lora()
    else:
        pipeline.disable_lora()

    output_images = []
    for image_file in image_files:
        input_image = Image.open(image_file.name).convert("RGB")
        
        # Generate the new image
        output_image = pipeline(image=input_image, prompt=prompt, negative_prompt=negative_prompt, num_inference_steps=sample_steps, true_cfg_scale=4.0, generator=torch.manual_seed(0)).images[0]
        
        # Save the generated image to the persistent volume
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        filename = f"{OUTPUT_DIR}/{timestamp}.png"
        output_image.save(filename)
        
        output_images.append(output_image)

    return output_images


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
                        negative_prompt_qwen = gr.Textbox(label="Negative Prompt", info="What do you want to exclude from the image?", value=" ", lines=4, interactive=True, visible=False)
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
                    input_image_edit = gr.File(label="Upload Images", file_count="multiple", file_types=["image"])
                    prompt_edit = gr.Textbox(label="Prompt", info="What do you want to change?", value="A photo of a woman.", lines=3, interactive=True)
                    negative_prompt_edit = gr.Textbox(label="Negative Prompt", info="What do you want to exclude from the image?", value=" ", lines=3, interactive=True)
                    
                    lora_choices = ["None", "lightning", "remove_clothing", "bumpy_nipples", "pussy_lora"]
                    
                    with gr.Accordion(label="LoRA Configuration (Up to 4)", open=True):
                        with gr.Row():
                            lora1_name = gr.Dropdown(lora_choices, value="lightning", label="LoRA 1")
                            lora1_strength = gr.Slider(0.0, 2.0, 1.0, label="Strength 1")
                        with gr.Row():
                            lora2_name = gr.Dropdown(lora_choices, value="None", label="LoRA 2")
                            lora2_strength = gr.Slider(0.0, 2.0, 1.0, label="Strength 2")
                        with gr.Row():
                            lora3_name = gr.Dropdown(lora_choices, value="None", label="LoRA 3")
                            lora3_strength = gr.Slider(0.0, 2.0, 1.0, label="Strength 3")
                        with gr.Row():
                            lora4_name = gr.Dropdown(lora_choices, value="None", label="LoRA 4")
                            lora4_strength = gr.Slider(0.0, 2.0, 1.0, label="Strength 4")


                    sampling_steps_edit = gr.Slider(label="Sampling Steps", info="The number of denoising steps.", value=8, minimum=1, maximum=50, step=1, interactive=True)
                    generate_button_edit = gr.Button("Generate")
                with gr.Column():
                    output_edit = gr.Gallery(label="Generated Images", show_label=True, elem_id="gallery")
            generate_button_edit.click(fn=generate_qwen_edit, 
                                       inputs=[input_image_edit, prompt_edit, negative_prompt_edit, sampling_steps_edit, 
                                               lora1_name, lora1_strength, lora2_name, lora2_strength, 
                                               lora3_name, lora3_strength, lora4_name, lora4_strength], 
                                       outputs=[output_edit])


if __name__ == "__main__":
    interface.launch(share=True)
