# LLM Assistant Project Guide: Multi-Model Gradio App on Modal

**Objective**: This document provides a technical overview and operational instructions for an AI assistant managing this repository. The project's goal is to run a multi-model image generation Gradio application within a Modal Notebook environment, using a private GitHub repository and a persistent Modal Volume for model caching.

---

## 1. File Breakdown

This repository contains the following key files:

### `app.py`
- **Purpose**: This is the core application script. It creates and launches a multi-tab Gradio web interface.
- **Functionality**:
    - **UI**: Implements a `gradio.Tabs` interface, with each tab dedicated to a specific AI model.
        - **Tab 1: `epicrealism xl`**: High-quality text-to-image generation.
        - **Tab 2: `qwen-image + lightning`**: Fast text-to-image generation using a LoRA.
        - **Tab 3: `qwen-image-edit + lightning`**: Fast image-to-image editing using a LoRA.
    - **Model Loading (`get_pipeline` function)**:
        - Dynamically loads the appropriate model pipeline based on the selected tab.
        - Implements a simple in-memory cache (`pipeline_cache`) to keep the last used model ready.
        - **Crucially, it uses a persistent Modal Volume by setting `cache_dir="/mnt/my-models-volume"` for all `from_pretrained` and `load_lora_weights` calls. This ensures model files are downloaded only once.**
    - **Dependencies**: Relies on `diffusers`, `torch`, and `gradio`.

### `requirements.txt`
- **Purpose**: Lists the Python dependencies required to run `app.py`.
- **Key Detail**: It specifies a custom installation of the `diffusers` library directly from its GitHub repository (`diffusers @ git+https://github.com/huggingface/diffusers.git`). This is a non-standard requirement mandated by the Qwen models for access to the latest features and pipelines.

### `Realistic.md`
- **Purpose**: This Markdown file contains the sequence of shell commands that the user pastes into a Modal Notebook cell to set up the environment and run the application.
- **Role**: This file serves as the **sole target for any modifications to the notebook execution flow**. It is the user's preferred format for receiving notebook code.

### `modal-notebooks-docs.md`
- **Purpose**: This file is a local, static copy of the official documentation for the Modal Notebooks feature.
- **Role**: This document should be treated as the **primary source of truth** for any questions regarding the capabilities, limitations, or proper usage of Modal Notebooks. As this is a new feature, you must prioritize the information in this file over your internal knowledge base to avoid providing outdated or incorrect advice. Refer to it to answer questions about features like persistent volumes, secrets, and environment setup.

---

## 2. Instructions for LLM Assistant

When assisting with this repository, you must adhere to the following workflow and rules:

### **Primary Directive: Do Not Edit Notebook Files Directly**
The user has a strong and repeated preference that you **do not write or edit `.ipynb` (Jupyter Notebook) files.** [[memory:8529069]] [[memory:8528562]] Any code or commands intended to be run in a notebook cell must be written into a Markdown file, specifically `Realistic.md`. The user will manually transfer this code to their notebook.

### Standard Development Workflow:
1.  **Analyze Request**: The user will request a change, such as adding a new model or modifying the UI.
2.  **Edit Source Code**: Modify `app.py` and/or `requirements.txt` to implement the requested changes.
3.  **Update Notebook Commands (if necessary)**: If the setup or run commands change (e.g., a new environment variable is needed), edit the commands **only in `Realistic.md`**.
4.  **Remind User of Git Workflow**: After applying code changes, you **must** remind the user to push the modifications to their private GitHub repository. The Modal Notebook clones from this repo, so this step is critical. A sample reminder:
    > "I have applied the code changes. Please remember to push them to GitHub before running the notebook: `git add . && git commit -m 'Your message' && git push`"
5.  **Remind User of Modal Setup**: When providing the final instructions, always remind the user of the manual setup steps required in the Modal Notebook UI:
    *   Select a GPU.
    *   Attach the `github-token` secret.
    *   Attach the `huggingface-secret`.
    *   Attach the `my-models-volume` volume.

By following this guide, you will be able to interact with this repository in the user's preferred manner, ensuring a smooth and efficient workflow.
