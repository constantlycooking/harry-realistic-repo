# Workflow for Extending the Multi-Model Application

This document outlines the high-level, repeatable workflow for adding new models (e.g., text-to-video, new text-to-image) and LoRAs to this application.

## 1. General Workflow

The process is a collaboration between you (the user) and the LLM assistant. It's broken down into three main phases: providing the necessary information, implementing the code, and deploying the changes.

### Phase 1: Information Gathering (Your Role)

Your primary role is to provide the LLM with the necessary context and documentation for the new model or LoRA you want to add. The more high-quality information you provide upfront, the more likely the LLM is to succeed on the first try.

In order of importance, you need to provide:

1.  **The Hugging Face Page URL for the Model/LoRA**: This is the most critical piece of information. The page's README is the instruction manual.
2.  **A Code Snippet**: The code snippet from the Hugging Face README is invaluable. It tells the assistant:
    *   The exact model identifier string (e.g., `Qwen/Qwen-Image-Edit`).
    *   The specific `diffusers` pipeline required (e.g., `QwenImageEditPipeline`).
    *   Any special requirements, like a custom scheduler or a non-standard version of a library.
    *   The exact parameters the model's pipeline expects.
3.  **The Hugging Face Page URL for the Base Model** (if you're adding a LoRA): Sometimes a LoRA is applied to a different base model, so providing both URLs is helpful.
4.  **Tree Structure (Optional but helpful)**: Providing the `huggingtree` output gives the LLM a quick way to verify file paths and understand the repository structure, but it's less critical than the README and code snippets.
5.  **Direct Download Links (Optional)**: These are generally not needed, as the Hugging Face identifier is enough for the `diffusers` library to find and download the files.

### Phase 2: Code Implementation (LLM's Role)

Once you provide the information, the LLM will perform the following steps:

1.  **Update `requirements.txt`**: If the new model requires a different library version or a new dependency, the LLM will edit this file first.
2.  **Update `app.py`**: The LLM will then modify the core application to integrate the new model. This usually involves:
    *   Adding a new tab to the Gradio interface with the appropriate UI components (e.g., an image upload box for image-to-image, a video player for text-to-video).
    *   Adding a new case to the `get_pipeline` function to handle loading the new model and any associated LoRAs, making sure to use the persistent `cache_dir`.
    *   Creating a new `generate_*` function that calls the pipeline with the correct parameters from the new UI tab.
3.  **Update `README.md`**: The LLM will update the project's documentation to reflect the new addition.

### Phase 3: Deployment (Your Role)

After the LLM has made the code changes, the final steps are yours:

1.  **Push to GitHub**: You must commit the changes and push them to your private repository. This is a critical step that cannot be skipped.
2.  **Run the Modal Notebook**: Start your notebook, attach the necessary secrets and volumes in the UI, and run the commands from `Realistic.md`.

---

## 2. Case Study: Adding the Qwen Models

Here is how we applied this exact workflow to add the two Qwen models:

1.  **Information Gathering**: You provided the Hugging Face URLs for the `Qwen-Image` and `Qwen-Image-Edit` base models, as well as the `Qwen-Image-Lightning` LoRA. The READMEs and code snippets on those pages were crucial. They told us we needed a specific `diffusers` version (from GitHub), a custom scheduler, and the `QwenImageEditPipeline`.

2.  **Code Implementation**:
    *   I first updated `requirements.txt` to install `diffusers` from git.
    *   I then refactored `app.py` to use a tabbed interface.
    *   I added the logic for the `qwen` text-to-image model, including its LoRA and the custom scheduler.
    *   Later, I added a third tab for the `qwen-edit` model, which included adding an image upload UI and a new `generate_qwen_edit` function.
    *   Throughout this, I ensured all model-loading calls pointed to the persistent volume (`cache_dir`).

3.  **Deployment**: After the code was ready, the final step was for you to push the code to GitHub and then run it in your properly configured Modal Notebook.

This process is a robust template. By following it, you can systematically add almost any new model from the Hugging Face ecosystem to your application.
