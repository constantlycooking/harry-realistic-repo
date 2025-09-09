# Modal Notebooks

Notebooks allow you to write and execute Python code in Modal's cloud, within your browser. It's a hosted Jupyter notebook with:

- Serverless pricing and automatic idle shutdown
- Access to Modal GPUs and compute
- Real-time collaborative editing
- Python Intellisense/LSP support and AI autocomplete

<center>
<video controls autoplay muted playsinline>
<source src="https://modal-cdn.com/Modal-Notebooks-Beta.mp4" type="video/mp4">
</video>
</center>

## Getting started

Open [modal.com/notebooks](/notebooks) in your browser and create a new notebook. You can also upload an `.ipynb` file from your computer.

Once you create a notebook, you can start running cells. Try a simple statement like

```python
print("Hello, Modal!")
```

Or, import a library and create a plot:

```python notest
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-20, 20, 500)
plt.plot(np.cos(x / 3.7 + 0.3), x * np.sin(x))
```

The default notebook image comes with a number of Python packages pre-installed, so you can get started right away. Popular ones include PyTorch, NumPy, Pandas, JAX, Transformers, and Matplotlib. You can find the full image definition [here](https://github.com/modal-labs/modal-client/blob/v1.1.3/modal/experimental/__init__.py#L234-L342). If you need another package, just install it:

```shell
!uv pip install --system [my-package]
```

All output types work out-of-the-box, including rich HTML, images, [Jupyter Widgets](https://ipywidgets.readthedocs.io/en/latest/), and interactive plots.

## Kernel resources

Just like with Modal Functions, notebooks run in serverless containers. This means you pay only for the CPU cores and memory you use.

If you need more resources, you can change kernel settings in the sidebar. This lets you set the number of CPU cores, memory, and GPU type for your notebook. You can also set a timeout for idle shutdown, which defaults to 10 minutes.

Use any GPU type available in Modal, including up to 8 Nvidia A100s or H100s. You can switch the kernel configuration in seconds!

![Compute profile tab in notebook sidebar](https://modal-cdn.com/cdnbot/compute-profilev9rvmmvw_365a1197.webp)

Note that the CPU and memory settings are _reservations_, so you can usually burst above the request. For example, if you've set the notebook to have 0.5 CPU cores, you'll be billed for that continuously, but you can use up to any available cores on the machine (e.g., 32 CPUs) and will be billed for only the time you use them.

### Notebook pricing

Modal Notebooks are priced simply, by compute usage while the kernel is running. See the [pricing page](https://modal.com/pricing) for rates. Currently the CPU and Memory costs are priced according to Sandboxes. They appear in your [usage dashboard](/settings/usage) under "Sandboxes" as well.

Inactive notebooks do not incur any cost. You are only billed for time the notebook is actively running.

## Custom images, volumes and secrets

Modal Notebooks supports custom images, volumes, and secrets, just like Modal Functions. You can use these to install additional packages, mount persistent storage, or access secrets.

- To use a custom image, you need to have a [deployed Modal Function](/docs/guide/managing-deployments) using that image. Then, search for that function in the sidebar.
- To use a Secret, simply create a [Modal Secret](/secrets) using our wizard and attach it to the notebook, so it can be injected as an environment variable automatically.
- To use a Volume, create a [Modal Volume](/docs/guide/volumes) and attach it to the notebook. This lets you mount high-performance, persistent storage that can be shared across multiple notebooks or functions. They will appear as folders in the `/mnt` directory by default.

### Creating a Custom Image

If you don't have a suitable deployed Modal App already, you can set up your environment to deploy custom images in under a minute using the Modal CLI. First, run `pip install modal`, and define your image in a file like:

```python
import modal


# Image definition here:
image = (
    modal.Image.from_registry("python:3.13-slim")
    .pip_install("requests", "numpy")
    .apt_install("curl", "wget")
    .run_commands(
        "echo 'foo' > /root/hello.txt",
        # ... other commands
    )
)

app = modal.App("notebook-images")

@app.function(image=image)  # You need a Function object to reference the image.
def notebook_image():
    pass
```

Then, make sure you have the Modal CLI (`pip install modal`) and run this command to build and deploy the image:

```bash
modal deploy notebook_images.py
```

For more information on custom images in Modal, see our [guide on defining images](/docs/guide/images).

(Advanced) Note that if you use the [`add_local_file()` or `add_local_dir()` functions](/docs/guide/images#add-local-files-with-add_local_dir-and-add_local_file), you'll need to pass `copy=True` for them to work in Modal Notebooks. This is because they skip creating a custom image and instead mount the files into the function at startup, which won't work in notebooks.

### Creating a Secret

Secrets can be created from the dashboard at [modal.com/secrets](/secrets). We have templates for common credential types, and they are saved as encrypted objects until container startup.

Attacahed secrets become available as environment variables in your notebook.

### Creating a Volume

[Volumes](/docs/guide/volumes) can only be created from the CLI right now. You can run this CLI from your computer, or in a notebook cell:

```bash
modal volume create my-notebook-volume
```

Any volumes are attached in the `/mnt` folder in your notebook, and files saved there will be persisted across kernel startups or other usage.

## Access and sharing

Need a colleague—or the whole internet—to see your work? Just click **Share** in the top‑right corner of the notebook editor.

Notebooks are editable by you and teammates in your workspace. To make the notebook view-only to collaborators, the creator of the notebook can change access settings in the "Share" menu. Workspace managers are also allowed to change this setting.

You can also turn on sharing by public, unlisted link. If you toggle this, it allows _anyone with the link_ to open the notebook, even if they are not logged in. Pick **Can view** (default) or **Can view and run** based on your preference. Viewers don’t need a Modal account, so this is perfect for collaborating with stakeholders outside your workspace.

No matter how the notebook is shared, anyone with access can fork and run their own version of it.

## Interactive file viewer

The panel on the left-hand side of the notebook shows a **live view of the container’s filesystem**:

| Feature                 | Details                                                                                                                                                                    |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Browse & preview**    | Click through folders to inspect any file that your code has created or downloaded.                                                                                        |
| **Upload & download**   | Drag-and-drop files from your desktop, or click the **⬆** / **⬇** icons to add new data sets, notebooks, or models—or to save results back to your machine.              |
| **One-click refresh**   | Changes made by your code (for example, writing a CSV) appear instantly; hit the refresh icon if you want to force an update.                                              |
| **Context-aware paths** | The viewer always reflects _exactly_ what your code sees (e.g. `/root`, `/mnt/…`), so you can double-check that that file you just wrote really landed where you expected. |

**Important:** the underlying container is **ephemeral**. Anything stored outside an attached [Volume](/docs/guide/volumes) disappears when the kernel shuts down (after your idle-timeout or when you hit **Stop kernel**). Mount a Volume for data you want to keep across sessions.

The viewer itself is only active while the kernel is running—if the notebook is stopped you’ll see an “empty” state until you start it again.

## Editor features

Modal Notebooks bundle the same productivity tooling you’d expect from a modern IDE.

With Pyright, you get autocomplete, signature help, and on-hover documentation for every installed library.

We also implemented AI-powered code completion using Anthropic's **Claude 4** model. This keeps you in the flow for everything from small snippets to multi-line functions. Just press `Tab` to accept suggestions or `Esc` to dismiss them.

Familiar Jupyter shortcuts (`A`, `B`, `X`, `Y`, `M`, etc.) all work within the notebook, so you can quickly add new cells, delete existing ones, or change cell types.

Finally, we have real-time collaborative editing, so you can work with your team in the same notebook. You can see other users' cursors and edits in real-time, and you can see when others are running cells with you. This makes it easy to pair program or review code together.

## Cell magic

Modal Notebooks have built-in support for the `%modal` cell magic. This lets you run code in any [deployed Modal Function or Cls](/docs/guide/trigger-deployed-functions), right from your notebook.

For example, if you have previously run `modal deploy` for an app like:

```python notest
import modal

app = modal.App("my-app")


@app.function()
def my_function(s: str):
    return len(s)
```

Then you could access this function from your notebook:

```python notest
%modal from my-app import my_function

my_function.remote("hello, world!")  # returns 13
```

Run `%modal` to see all options. This works for Cls as well, and you can import from different environments or alias them with the `as` keyword.

## Roadmap

The product is in beta, and we're planning to make a lot of improvements over the coming months. Some bigger features on mind:

- **Modal cloud integrations**
  - Expose ports with [Tunnels](/docs/guide/tunnels)
  - Memory snapshots to restore from past notebook sessions
  - Create notebooks from the `modal` CLI
  - Custom image registry
- **Notebook editor**
  - Interactive outline, collapsing sections by headings
  - Reactive cell execution
  - Edit history
  - Integrated debugger (pdb and `%debug`)
- **Documents and sharing**
  - Restore recently deleted notebooks
  - Folders and tags for grouping notebooks
  - Sync with Git repositories

Let us know via [Slack](/slack) if you have any feedback.


# Introducing Notebooks

[Back](https://modal.com/blog)
News

September 9, 2025•5 minute read

**Modal Notebooks** is a collaborative environment for high-performance interactive computing. It lets you explore data, run code, and test ideas in a shared editor. This is powered by a GPU-enabled Python kernel that launches in seconds on Modal’s AI infrastructure.

In most cloud notebooks, kernels take minutes to start, environments aren’t preserved, idle sessions waste money, and you’re stuck on oversized GPU instances. Modal Notebooks removes these points of friction, so you can focus on cutting-edge work.

After a limited beta last month, Notebooks are now generally available to all Modal customers.

A better way to iterate on code and research
--------------------------------------------

“

Modal Notebooks have been incredible for sharing ML research across Suno. Engineers and designers can start playing with cutting-edge models within minutes after training runs are completed.

”

— Victor Tao,ML Research Engineer

Today, tens of millions of end-users interact with applications built on Modal, from AI-generated music at [Suno](https://suno.com/), to payments at [Ramp](https://ramp.com/), to consumer apps like [Lovable](https://lovable.dev/) and [Substack](https://substack.com/).

Notebooks represent a new way to develop with Modal. They are designed for research and experimentation—not just writing code, but _rapidly developing and refining ideas_ with your team. We believe this process is an important part of AI development and deserves equally good tooling as full-scale production workflows.

Features include:

*   **Fast time-to-first-cell.** Cold-start to ready in _less than 5 seconds_, on arbitrary container images and hardware ranging up to 256 vCPUs and 8 H100/B200 GPUs. Switch GPU type just as easily.
*   **No zombie boxes.** Kernels auto-idle and resume, so you only pay for when they’re running (configurable if you need control).
*   **One environment.** Access the same Volumes (distributed storage), Secrets, and deployed Functions as the rest of your Modal Apps.
*   **True collaborative editing.** Share live sessions with your team like in Google Docs—no more emailing `.ipynb` files around or suddenly seeing your code & outputs disappear after a delayed refresh.

Modal has already redefined how teams run and scale jobs in production. Notebooks aim to bring our core developer experience principles to the exploratory side of AI work.

What you can do
---------------

### Start instantly. Scale on demand.

*   Run from as little as **0.125 CPUs** up to **8 Nvidia A100/H100/B200 GPUs**.

_With CPU, you can also burst above configured resource usage and only pay for active compute cycles._

*   Bring a **custom image** or work from a curated AI base image.

_Modal’s content-addressed FUSE filesystem caches packages and loads them on demand, so kernels boot quickly even with large images._

*   Automatic idle-shutdown with fast resume (manual control is also available).

### Work together in real time

*   Multiple cursors, live presence, and seamless collaborative editing.
*   Share within your workspace with fine-grained permissions.
*   Use Jupyter Widgets to prototype and share interactive apps, which most other cloud notebook platforms don’t support.

### Use your Modal stack, directly

*   Attach **Volumes** (persistent storage) and **Secrets** from the UI; browse files inline or upload them via drag-and-drop. Volumes can store terabytes of data with relaxed consistency and are multi-writer accessible from around the world.

_Because Volumes and Secrets are shared across the workspace, you get reproducible results no matter who is running the notebook._

![Image 1: File viewer screenshot](https://modal-cdn.com/nb-assets-sept-8/filesystem-viewer.png)

*   **Call Modal Functions** from any cell without extra authentication.

*   Reuse the **same images and runtime primitives** you already deploy in production.

### Modern dev experience (LSP + AI)

*   **Pyright** language server for completions, types, and diagnostics.
*   **AI completions** when you’re exploring what to try next.
*   Rich HTML outputs for plots/media in libraries like Altair, Seaborn, Plotly, and py3Dmol.

Industry usage of Notebooks
---------------------------

During our short beta in August, **over 5,000 accounts** adopted Notebooks in their daily workflows, running **200,000 code cells** with instant startup and real-time collaboration. Early adopters included leading AI research and product startups—teams that need to move quickly from training to production.

Here’s what some of them had to say:

“

Testing different GPUs on the fly has massively accelerated our workflow for profiling models. Tasks that used to take days now take minutes.

”

— Simran Makariye,ML Engineer

“

Other platforms like Colab didn't have the capacity we needed. We love how Modal Notebooks lets us scale up any amount of GPUs and compute.

”

— Arda Göreci,Co-founder & CTO

“

Honestly, one of the best experiences I’ve had for casual and exploratory coding. The ability to live-swap hardware specs—including top-tier GPUs, and even multiple ones—is next-level. Super smooth and really fun to use.

”

— Stefano Giomo

“

We used to spend hours just setting up access and dealing with surprise costs. With Modal Notebooks, I set up a research environment for our intern and could give feedback on his experiment in real time.

”

— Alice Yu,Co-Founder & CEO @ OncoCardia

And while today marks general availability, we’re already thinking ahead. Upcoming features include:

*   **Memory snapshots** to suspend and later resume execution, while preserving variables and files.
*   **One-click export** of notebook code into Modal Apps.
*   **Scheduled runs and edit history** for better reproducibility.

Try it today, with $30 free credits
-----------------------------------

For the Modal team, Notebooks have become our default surface for experiments and collaborative work. Our hope is that their speed, usability, and compute flexibility enable researchers to work together and bring simpler, better products into the world.

Check out some of our featured examples:

[See the docs](https://modal.com/docs/guide/notebooks-modal) for more, or [send us feedback on Slack](https://modal.com/slack).