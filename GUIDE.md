# LLM Project Guide: Gradio App in a Modal Notebook

**Objective**: This document provides a comprehensive technical guide for an AI assistant. It covers both the general Modal Notebooks ecosystem and the specific implementation details of this repository. Its purpose is to serve as the single source of truth for all future development and maintenance.

---

## Part 1: The Modal Notebooks Ecosystem

This project runs within Modal Notebooks, a specific cloud environment with a unique set of features, advantages, and limitations.

### 1.1 Core Concept

Modal Notebooks provide a serverless, interactive computing environment that bridges the gap between simple CLI scripting and full-scale web application deployment. They are ideal for rapid prototyping, experimentation, and collaborative development of GPU-intensive applications.

### 1.2 Key Features & Terminology

*   **Serverless Kernel**: The Python environment (kernel) is serverless. It starts on demand, provides access to powerful CPUs and GPUs, and automatically shuts down when idle. This is highly cost-effective, as you only pay for active compute time.
*   **Persistent Volumes**: This is a critical feature we use. A Volume is like a network hard drive that can be attached to the notebook. It provides persistent storage that survives kernel restarts. **We use this to store the multi-gigabyte AI model files**, solving the problem of re-downloading them in every session.
*   **Secrets**: A secure way to manage credentials like API keys. We use Modal Secrets for both the `GITHUB_TOKEN` (to clone this private repo) and the `HF_TOKEN` (to download private LoRAs from Hugging Face). These are attached in the UI and become available as environment variables.
*   **Custom Images**: A feature that allows pre-baking all `pip` dependencies into a reusable container image. While we do not currently use this, it represents the final optimization step to eliminate the `pip install` time at startup.
*   **Ephemeral Filesystem**: The notebook's local filesystem is temporary. Any file written outside of an attached Volume will be deleted when the session ends. This is why we save all generated images to a directory inside our Volume.
*   **Memory Snapshots (Future Feature)**: As of now, GPU Memory Snapshots are **not available** for Modal Notebooks, only for deployed Modal Apps. This feature, when released, is expected to solve the long initial model loading time by saving the state of the GPU's memory. Until then, the "cold start" of loading a model from the Volume into VRAM is an unavoidable one-time cost per session.

### 1.3 Pros & Cons Summary

*   **Pros**:
    *   Instant access to a wide range of powerful GPUs.
    *   Cost-efficient, pay-per-use serverless model.
    *   Perfect for rapid prototyping with tools like Gradio, providing temporary public URLs for testing.
    *   Professional-grade features like Persistent Volumes and Secrets.
*   **Cons**:
    *   Not suitable for production hosting; it is a development/testing tool.
    *   The initial "cold start" time to load a model from a Volume into GPU memory is significant and unavoidable with current features.

---

## Part 2: This Project's Implementation

### 2.1 File Breakdown

*   **`app.py`**: The core application script. It builds a multi-tab Gradio UI.
    *   **UI**: Features three tabs: `epicrealism xl` (text-to-image), `qwen-image + lightning` (fast text-to-image), and `qwen-image-edit + lightning` (advanced image-to-image).
    *   **Key Features**:
        *   **Batch Processing**: The edit tab accepts multiple images.
        *   **Multi-LoRA**: The edit tab supports combining up to four LoRAs with individual strengths.
        *   **Auto-Saving**: All generated images are saved to `/mnt/my-models-volume/outputs`.
        *   **Auto-Resizing**: Large input images are automatically resized to a max dimension of 1024px to ensure fast performance.
    *   **Persistence**: All model loading uses `cache_dir="/mnt/my-models-volume/models"` to leverage our Persistent Volume.

*   **`requirements.txt`**: Lists Python dependencies. Notably, it installs `diffusers` directly from GitHub, a requirement for the Qwen models.

*   **`Realistic.md`**: Contains the shell commands for setting up and running the app in a notebook cell. **This is the user's preferred format for notebook code.**

*   **`modal-notebooks-docs.md`**: The local copy of the official documentation, which must be treated as the primary source of truth.

### 2.2 Instructions for LLM Assistant

*   **Primary Directive**: **Do not edit `.ipynb` files.** All notebook code must be provided in a Markdown file, preferably by editing `Realistic.md`. [[memory:8529069]] [[memory:8528562]]

*   **Standard Workflow**:
    1.  **Analyze Request**: Understand the user's goal.
    2.  **Edit Source Code**: Modify `app.py`, `requirements.txt`, etc.
    3.  **Update Notebook Commands**: If necessary, edit the commands **only** in `Realistic.md`.
    4.  **Remind User of Git Workflow**: Crucially, remind the user to push all code changes to GitHub.
    5.  **Remind User of Modal Setup**: Always provide the full list of manual UI steps: Select GPU, attach `github-token`, attach `huggingface-secret`, and attach `my-models-volume`.
