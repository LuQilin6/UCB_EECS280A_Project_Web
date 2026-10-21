# Project 3 — Flow Models: Full Requirements (CS280A)

Sources (fetched 2026-10-19; the PDFs in this folder are image-only scans of these pages):
- Part A: https://cal-cs180.github.io/fa26/hw/proj3-flow/parta.html
- Part B: https://cal-cs180.github.io/fa26/hw/proj3-flow/partb.html

**Due: October 20, 2026** (both parts).
**Taking CS280A:** the Bells & Whistles marked "required for CS280A" are **mandatory** in both parts.

## Submission
| | Part A | Part B |
|---|---|---|
| Code → Gradescope | yes | yes |
| Website PDF → Gradescope | yes | yes |
| Google Form (webpage URL to class gallery) | not required | **required** (submit once, after both parts; the page must contain A **and** B) |

- Website must include **every deliverable** in every section (checklist at bottom).
- Save checkpoints and notebook outputs. Keep notebook outputs when submitting the code.

---

# PART B — Flow Matching from Scratch (MNIST)

Conventions (from notebook): MNIST pixels in **[0,1]**. Flow time goes from Gaussian noise at **t=0** to data at **t=1**. Predict velocity **x1 − x0** (not noise). CFG in Part B: **u = u_uncond + γ(u_cond − u_uncond)**, γ = 5 (this differs from Part A's convention).

## Part 1: Single-Step Denoising UNet
Objective (B.1): L = E_{z,x} ‖D_θ(z) − x‖²

### 1.1 Implementing the UNet
**Simple ops** (Fig. 2, confirmed from the diagram):
| # | Op | Definition | Shape |
|---|---|---|---|
| 1 | Conv | Conv2d(k=3, s=1, p=1) + BN + GELU | D_in×H×W → D_out×H×W |
| 2 | DownConv | Conv2d(k=3, s=2, p=1) + BN + GELU | → D_out×H/2×W/2 |
| 3 | UpConv | ConvTranspose2d(k=4, s=2, p=1) + BN + GELU | → D_out×2H×2W |
| 4 | Flatten | AvgPool2d(7) + GELU | D×7×7 → D×1×1 |
| 5 | Unflatten | ConvTranspose2d(k=7, s=7, p=0) + BN + GELU | D×1×1 → D×7×7 |
| 6 | Concat | torch.cat along channels | (D1, D2) → D1+D2 |

**Composed ops:**
| # | Op | Definition |
|---|---|---|
| 7 | ConvBlock | Conv(D_in→D_out) → Conv(D_out→D_out) |
| 8 | DownBlock | DownConv(D_in→D_out) → ConvBlock(D_out→D_out) |
| 9 | UpBlock | UpConv(D_in→D_out) → ConvBlock(D_out→D_out) |
| 10 | FCBlock | Linear(F_in→F_out) + GELU → Linear(F_out→F_out) |

**Unconditional UNet (Fig. 1):**
```
x 1×28×28
 └ ConvBlock(1→D)            → e0: D×28×28
 └ DownBlock(D→D)            → e1: D×14×14
 └ DownBlock(D→2D)           → e2: 2D×7×7
 └ Flatten                   → b : 2D×1×1
 └ Unflatten(2D→2D)          → u0: 2D×7×7
 cat(e2, u0)                 → 4D×7×7
 └ UpBlock(4D→D)             → u1: D×14×14
 cat(e1, u1)                 → 2D×14×14
 └ UpBlock(2D→D)             → u2: D×28×28
 cat(e0, u2)                 → 2D×28×28
 └ ConvBlock(2D→D)           → D×28×28
 └ Conv2d(3,1,1)(D→1)        → 1×28×28
```

### 1.2 Using the UNet to Train a Denoiser
Noising (B.2): **z = x + σε, ε ~ N(0, I)**, x ∈ [0,1].
- **Deliverable:** visualization of noising for **σ = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]** (noisier as σ grows).

### 1.2.1 Training
- Denoise **σ = 0.5**.
- `torchvision.datasets.MNIST`, **train set only**, **shuffle**, batch size **256**, **5 epochs**.
- Add noise **only when a batch is fetched** (fresh ε every epoch).
- UNet from 1.1, hidden dim **D = 128**.
- Adam, **lr = 1e-4**.
- Staff reference: about 3 min for 5 epochs on a Colab T4.
- **Deliverables:**
  - [ ] Training loss curve, logged every few iterations over the whole run (σ=0.5)
  - [ ] Test-set results at σ=0.5 after **epoch 1** and **epoch 5** (noisy input / output / clean)

### 1.2.2 Out-of-Distribution Testing
- **Deliverable:**
  - [ ] Trained denoiser on test digits with **σ = [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]**, keeping the **same image** while σ varies

### 1.2.3 Denoising Pure Noise
- Same training as 1.2.1, but input **z = ε ~ N(0,I)** (pure noise), target the clean digit, **5 epochs**. Notebook: fresh D=128 UNet, Adam lr 1e-4, batch 256.
- **Deliverables:**
  - [ ] Training loss curve
  - [ ] Samples on pure noise after **epoch 1** and **epoch 5**
  - [ ] Short description of the patterns and why they occur. Hint: MSE makes the model predict the point minimizing the summed squared distance to all training examples, a centroid, so the outputs look like the **average of all digits**, a blurry overlay that barely depends on the input noise.

## Part 2: Flow Matching Model
- Interpolation (B.3): **x_t = (1−t)x0 + t·x1**, x0 ~ N(0, I), t ∈ [0,1]
- Flow (B.4): **u(x_t, t) = x1 − x0**
- Objective (B.5): **L = E ‖(x1 − x0) − u_θ(x_t, t)‖²**, t ~ U[0,1]
- The UNet predicts the **flow**, not the clean image.

### 2.1 Time Conditioning (Fig. 4)
- FCBlock (#10) injects scalar t, so **F_in = 1**. t must be **normalized to [0,1]**.
- fc1_t: 1 → 2D (modulates the 2D×7×7 unflatten); fc2_t: 1 → D (modulates the D×14×14 output of the first UpBlock).
```
t1 = fc1_t(t); t2 = fc2_t(t)
unflatten = unflatten * t1        # multiplicative
up1       = up1 * t2              # up1 = output of first UpBlock (D×14×14)
```

### 2.2 Training (Algorithm B.1)
```
repeat:
  x1 ~ training set; t ~ U[0,1]; x0 ~ N(0,I)
  x_t = (1−t)x0 + t·x1
  gradient step on ‖(x1 − x0) − u_θ(x_t, t)‖²
until happy
```
- MNIST train only, shuffle, batch **64**; noise only when a batch is fetched.
- Time-conditioned UNet, **D = 64**.
- Adam, initial **lr = 1e-2**; `ExponentialLR(gamma = 0.1 ** (1.0 / num_epochs))`, `scheduler.step()` **after every epoch**. Notebook: **10 epochs**.
- **Deliverable:**
  - [ ] Loss curve over the whole training run

### 2.3 Sampling (Algorithm B.2)
```
x = x0 ~ N(0,I)
for t from 0 to 1, step 1/T:   x = x + (1/T)·u_θ(x, t)
return x
```
Notebook default T = num_ts = 50 for the time-only model.
- **Deliverables:**
  - [ ] Samples after **epochs 1, 5, 10** (should be reasonably good, need not be perfect)
  - [ ] (CS280A) see B&W: a better time-only UNet

### 2.4 Class Conditioning
- c = **one-hot** (10 classes, digits 0–9). Add 2 more FCBlocks, 4 in total: fc1_t, fc1_c, fc2_t, fc2_c.
- **p_uncond = 0.1**: set c to the zero vector 10% of the time.
```
t1 = fc1_t(t); c1 = fc1_c(c); t2 = fc2_t(t); c2 = fc2_c(c)
unflatten = c1 * unflatten + t1
up1       = c2 * up1 + t2
```

### 2.5 Training (Algorithm B.3)
```
repeat:
  x1, c ~ training set; c → one-hot; with prob p_uncond, c = 0
  t ~ U[0,1]; x0 ~ N(0,I); x_t = (1−t)x0 + t·x1
  gradient step on ‖(x1 − x0) − u_θ(x_t, t, c)‖²
until happy
```
Same hyperparameters as 2.2 (D=64, batch 64, Adam 1e-2, ExponentialLR γ=0.1^(1/10), 10 epochs). Save checkpoints at epochs 1, 5, 10.
- **Deliverable:**
  - [ ] Loss curve over the whole training run

### 2.6 Sampling (Algorithm B.4), CFG γ = 5.0
```
x = x0 ~ N(0,I)
for t from 0 to 1, step 1/T:
  u_u = u_θ(x, t, 0); u_c = u_θ(x, t, c)
  u = u_u + γ(u_c − u_u)
  x = x + (1/T)·u
return x
```
Notebook: **T = 300** Euler steps, fixed seeds for comparisons.
- **Deliverables:**
  - [ ] Samples after **epochs 1, 5, 10**: **4 instances of each digit 0–9** (40 images)
  - [ ] **No-scheduler ablation:** remove ExponentialLR, keep similar quality, show the visualization, and **describe what was changed to compensate** (e.g. a lower constant lr, more epochs, warmup, grad clipping)

## Part 3: Bells & Whistles (Part B)
- **REQUIRED for CS280A: a better time-conditioned-only UNet.** The 2.3 model is much worse than the class-conditioned one. Show a better visualization. Ideas: longer training, a more expressive architecture (wider D, sinusoidal time embedding, FiLM scale+shift, more blocks), EMA, more sampling steps.
- Optional: other datasets (SVHN, Fashion-MNIST, CIFAR-10) or your own ideas (e.g. sampling GIFs).

---

# PART A — Exploring the Power of Flow Models (pretrained PixNerd-XXL-P16-T2I)

Model generates **512×512**; RGB in **[−1, 1]**; **t=0 noise, t=1 clean**; no training needed. `model.encode(prompt)` gives Qwen3 prompt embeddings (cached).
Background: x_t = (1−t)x0 + t·x1; train to predict x1 − x0; sample by integrating dx/dt = v_θ(x_t,t,c) from 0 to 1 with Euler steps, recomputing velocity at each step.

## 1. Visualizing Training and Sampling
### 1.1 Constructing Noisy Training Inputs
(A.1) **x_t = (1−t)ε + t·x1**, ε ~ N(0,I). Use **one image of your own** (not the Campanile) for 1.1–1.5; supplied preprocessing center-crops to 512² in [−1,1]. Sample **one** ε and reuse it for **t ∈ {0.25, 0.50, 0.75}**.
- [ ] Implement `interpolate(image, noise, t)` (check both endpoints)
- [ ] Show the original + 3 noisy images, labeled by t
- Save the image, ε, and noisy tensors for 1.2–1.5

### 1.2 Classical Denoising
x_t/t = x1 + ((1−t)/t)ε; **x̂_blur = G_σ(x_t / t)** (`torchvision.transforms.functional.gaussian_blur`).
- [ ] For each t ∈ {0.25, 0.5, 0.75}: noisy input next to the best Gaussian-denoised result

### 1.3 One-Step Denoising
(A.2) **x̂1 = x_t + (1−t)·v_θ(x_t, t, c)**, prompt **"a high quality photo"**. Velocity, not noise. Check shape/dtype/device, keep float32, use no_grad.
- [ ] Implement `one_step_denoise`
- [ ] For each t: original, noisy, and one-step estimate side by side

### 1.4 Visualizing Velocity
Same image and noisy inputs, "a high quality photo". v̂ = v_θ(x_t,t,c); v_gt = x1 − ε, so (1−t)v_gt = x1 − x_t.
Error map **E_t = sqrt(mean_RGB([(1−t)(v̂ − v_gt)]²))** per pixel, computed before display scaling or clipping.
- [ ] Show the original image **once**
- [ ] For each t (labeled): x_t, predicted update (1−t)v̂, GT update (1−t)v_gt, error heatmap
- Updates on **one shared symmetric RGB scale, zero = middle gray**; errors via `plt.imshow`, linear, **same vmin/vmax** at all three t
- Implement `velocity_diagnostics` → (pred_update (B,3,H,W), gt_update (B,3,H,W), error (B,H,W))

### 1.5 Iterative Denoising with Euler Sampling
(A.3) **x_{t+h} = x_t + h·v_θ(x_t, t, c)**, **h = 0.02**; **shorten the last step** to land exactly at t=1; recompute velocity each step; return the final image and saved states [(t, x), …].
- [ ] Implement `euler_sample(x_start, t_start, step_size, velocity)`
- [ ] From the saved t=0.50 input: 25 updates; show the initial state, **every 5th update**, and the final image, labeled by t (0.50, 0.60, …, 1.00)
- [ ] Compare original / Gaussian blur / one-step / Euler on the same input
- Test: constant velocity field (notebook asserts 50 steps from 0, 25 from 0.5, 4 from 0.93)

### 1.6 Generating Images from Noise
t_start = 0, x_start = `torch.randn` (float32, on device), "a high quality photo", 50 Euler updates.
- [ ] Show **5 samples** (record seeds) and **report observations** (e.g. subject bias of the generic prompt)

## 2. Conditional Generation and Guidance
### 2.1 Classifier-Free Guidance
(A.4) **v_cfg = v_c + w(v_c − v_u)**, v_u from the **empty-string** prompt at the **same x_t and t**; **w = 7**, h = 0.02; w=0 means plain conditional.
- [ ] Implement `cfg_velocity` (check that w=0 reproduces conditional)
- [ ] 5 CFG samples with "a high quality photo" using the **same initial noises as 1.6**; compare with 1.6

## 3. Creative Applications (always h = 0.02, w = 7, unconditional = "")
### 3.1 Image-to-Image Editing (SDEdit)
`edit`: x = (1−t_s)ε + t_s·x1, then CFG-Euler from t_s to 1. **Start times [0.02, 0.04, 0.06, 0.10, 0.14, 0.25, 0.50]**, prompt "a high quality photo". Label each by starting time.
- [ ] Implement `edit`
- [ ] Campanile at all 7 start times
- [ ] **2 of your own images** at all 7 start times
- [ ] **1 web image** at all 7 start times (more allowed)
- [ ] **2 hand-drawn images** (drawn centered) at all 7 start times (more allowed)

### 3.2 Text-Guided Image Editing
Same as 3.1 with **your own prompt** in place of "a high quality photo".
- [ ] Campanile with your prompt, 7 start times, **show the prompt**
- [ ] 2 of your own images, **one prompt each**, 7 start times, show the prompts

### 3.3 Visual Anagrams
v1 = CFG(x_t, t, p1); **v2 = flip(CFG(flip(x_t), t, p2))**; v = (v1 + v2)/2. flip = **180° rotation** (both spatial axes).
- [ ] Implement `visual_anagrams`
- [ ] **2 illusions**: each upright + rotated, labeled with both prompts (multiple runs/seeds may be needed)

### 3.4 Hybrid Images (Factorized Diffusion)
v1 = CFG(x_t,t,p1); v2 = CFG(x_t,t,p2); **v = lowpass(v1) + (v2 − lowpass(v2))**; Gaussian blur **kernel 265, σ 16** at 512² (provided `lowpass`). p1 = distant/low-frequency, p2 = close-up/high-frequency.
- [ ] Implement `make_hybrids`
- [ ] **2 hybrid images**, each shown at **full size and reduced size**, labeled with both prompts

## Bells & Whistles (Part A)
- **REQUIRED for CS280A:**
  - [ ] **More visual anagrams:** pick **two more transformations** from *Visual Anagrams* (arXiv 2311.17919), i.e. orthogonal transforms or pixel permutations such as 90° rotation, horizontal flip, jigsaw permutation, inner-circle rotation, skew, color inversion. Make anagrams with each.
  - [ ] **Course logo:** text-conditioned image-to-image translation (SDEdit + prompt) on the UCB logo or your own drawing
- Optional: your own ideas.

---

# Master Deliverable Checklist (for the webpage)
**Part A:** 1.1 noisy inputs · 1.2 blur pairs · 1.3 one-step triplets · 1.4 velocity panels + heatmaps · 1.5 trajectory + 4-way comparison · 1.6 five samples + observations · 2.1 five CFG samples + comparison · 3.1 Campanile, 2 own, 1 web, 2 drawings (×7 times) · 3.2 Campanile + 2 own with prompts (×7) · 3.3 two anagrams · 3.4 two hybrids (full + small) · B&W: two extra anagram transforms, course logo.
**Part B:** 1.2 noise levels · 1.2.1 loss + epoch 1/5 results · 1.2.2 OOD sweep · 1.2.3 loss + epoch 1/5 + explanation · 2.2 loss · 2.3 samples epoch 1/5/10 · 2.5 loss · 2.6 samples epoch 1/5/10 (4 per digit) · no-scheduler result + explanation · B&W: better time-only UNet.
