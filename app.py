import gradio as gr
import torch
from diffusers import StableDiffusionXLPipeline, DiffusionPipeline, FlowMatchEulerDiscreteScheduler
import math

# Global variable to cache the pipeline
pipeline_cache = None
current_model_name = None

def get_pipeline(model_name):
    global pipeline_cache, current_model_name
    if current_model_name == model_name and pipeline_cache is not None:
        return pipeline_cache

    if model_name == "epicrealism":
        pipeline = StableDiffusionXLPipeline.from_pretrained("glides/epicrealismxl", torch_dtype=torch.float16, variant="fp16").to("cuda")
    elif model_name == "qwen":
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
        pipeline = DiffusionPipeline.from_pretrained(
            "Qwen/Qwen-Image", scheduler=scheduler, torch_dtype=torch.bfloat16
        ).to("cuda")
        pipeline.load_lora_weights(
            "lightx2v/Qwen-Image-Lightning", weight_name="Qwen-Image-Lightning-8steps-V1.1.safetensors"
        )
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

if __name__ == "__main__":
    interface.launch(share=True)
