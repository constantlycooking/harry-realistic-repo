# epicrealism xl on modal notebooks

this repository contains a gradio application for generating images with the epicrealism xl model, optimized to run within a [modal notebook](https://modal.com/notebooks).

## project overview

this project provides a simple web interface to generate images from text prompts using the epicrealism xl stable diffusion model. it's designed to be run in a modal notebook, leveraging modal's serverless gpu infrastructure.

### how it works: `app.py`

the `app.py` script is the core of this application. it uses several key libraries to achieve its functionality:

1.  **model loading**: the script loads the pre-trained `epicrealismxl` model using the `StableDiffusionXLPipeline` from the `diffusers` library. the model is immediately moved to the gpu (`.to("cuda")`) to ensure fast inference.

2.  **image generation function**: the `generate` function is where the image creation happens. it takes a text prompt, a negative prompt, and other settings (like image dimensions and quality steps), and passes them to the stable diffusion pipeline to generate an image.

3.  **web interface**: the user interface is built with `gradio`. it provides simple components like text boxes for prompts, sliders for advanced settings, a button to trigger generation, and an image element to display the result.

4.  **launching**: when `app.py` is run, it launches a gradio web server and, because of the `--share` flag, creates a temporary public url that you can use to access the interface from your browser.

### dependencies

the `requirements.txt` file lists all the python packages needed for this project:

*   **`diffusers`**: a core library from hugging face that makes it easy to download and use pre-trained diffusion models for image generation.
*   **`torch`**: the underlying deep learning framework that `diffusers` is built on. it handles all the complex mathematical computations on the gpu.
*   **`gradio`**: the library used to create and host the interactive web ui for the model.
*   **`accelerate`**: a helper library from hugging face that optimizes pytorch code for different hardware, ensuring the model runs as efficiently as possible.
*   **`transformers`**: provides necessary components for the stable diffusion pipeline, specifically for understanding the text prompts.
*   **`peft`**: parameter-efficient fine-tuning library, often a dependency for advanced `diffusers` pipelines.

## how to run

to get this application running, follow these simple steps.

### 1. set up your private repository

this project is designed to be used with a private github repository.

1.  **make this repository private**: if you have forked or cloned this repository, go to its settings on github and make it private.
2.  **create a github personal access token (pat)**:
    *   go to your [github developer settings](https://github.com/settings/tokens?type=beta) to create a new fine-grained personal access token.
    *   give the token a name (e.g., "modal-notebook").
    *   grant it the `repo` scope to allow access to your private repositories.
    *   copy the generated token.

### 2. create a modal secret

you need to store your github pat as a secret in modal so your notebook can access it securely.

*   go to the [modal secrets page](https://modal.com/secrets) and create a new secret.
*   name the secret `github-token`.
*   create a secret with the key `GITHUB_TOKEN` and paste your github pat as the value.

alternatively, if you have the modal cli installed, you can run this command in your terminal:

```bash
modal secret create github-token GITHUB_TOKEN="your_github_pat"
```

### 3. run in a modal notebook

now you're ready to run the application.

1.  **create a new modal notebook**: go to [modal.com/notebooks](https://modal.com/notebooks) and create a new notebook.
2.  **configure the kernel**: in the notebook's sidebar, make sure to select a gpu. any gpu will work.
3.  **attach the secret**: in the sidebar, attach the `github-token` secret you created.
4.  **run the code**: copy and paste the following code into a single cell in your notebook and run it:

```bash
%cd /root
!rm -rf harry-realistic-repo
!git clone https://${GITHUB_TOKEN}@github.com/constantlycooking/harry-realistic-repo.git
%cd harry-realistic-repo

%pip install -r requirements.txt

!python app.py --share
```

after running the cell, the necessary packages will be installed, and the gradio application will start. you'll see a public url in the output. click on that link to open the image generation interface in your browser.