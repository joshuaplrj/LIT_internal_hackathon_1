# AIDS-3: OmniVision — Multi-Modal Medical Image Registration and Fusion

## Overview

Build a system that **registers and fuses** medical images from different modalities (CT, MRI, PET, Ultrasound) for improved diagnosis.

## Modalities

| Modality | Strengths | Weaknesses |
|---|---|---|
| CT | Bone detail, fast | Radiation, poor soft tissue |
| MRI | Soft tissue contrast | Slow, expensive |
| PET | Metabolic information | Low resolution |
| Ultrasound | Real-time, cheap | Operator dependent |

## Task

### 1. Rigid Registration

Align CT and MRI of same patient:
- Intensity-based (mutual information)
- Feature-based registration
- Handle different resolutions/FOV

### 2. Deformable Registration

Register images with anatomical variations:
- Optical flow
- Diffeomorphic demons
- Learning-based (VoxelMorph)
- Preserve topology

### 3. Multi-Modal Fusion

Fuse registered images:
- Wavelet-based fusion
- Laplacian pyramid
- Learned fusion

### 4. Evaluation

- Target Registration Error (TRE)
- Dice coefficient
- Visual assessment

## Mutual Information Registration

```python
import numpy as np
from scipy import ndimage

class MutualInformationRegistration:
    def __init__(self, bins=256):
        self.bins = bins
    
    def histogram2d(self, img1, img2, mask=None):
        """Joint histogram"""
        if mask is not None:
            img1 = img1[mask]
            img2 = img2[mask]
        
        hist, _, _ = np.histogram2d(
            img1.ravel(), img2.ravel(),
            bins=self.bins,
            range=[[0, 1], [0, 1]]
        )
        
        return hist / hist.sum()
    
    def mutual_information(self, img1, img2, mask=None):
        """
        Calculate mutual information
        
        MI = H(X) + H(Y) - H(X,Y)
        """
        joint_hist = self.histogram2d(img1, img2, mask)
        
        # Marginal entropies
        p_x = joint_hist.sum(axis=1)
        p_y = joint_hist.sum(axis=0)
        
        H_x = -np.sum(p_x[p_x > 0] * np.log2(p_x[p_x > 0]))
        H_y = -np.sum(p_y[p_y > 0] * np.log2(p_y[p_y > 0]))
        
        # Joint entropy
        H_xy = -np.sum(joint_hist[joint_hist > 0] * np.log2(joint_hist[joint_hist > 0]))
        
        return H_x + H_y - H_xy
    
    def register(self, fixed, moving, transform_type='rigid'):
        """
        Optimize transformation to maximize MI
        """
        from scipy.optimize import minimize
        
        def objective(params):
            # Apply transformation
            transformed = self.apply_transform(moving, params, transform_type)
            return -self.mutual_information(fixed, transformed)
        
        # Initial parameters
        if transform_type == 'rigid':
            x0 = [0, 0, 0]  # tx, ty, rotation
        elif transform_type == 'affine':
            x0 = [1, 0, 0, 0, 1, 0]  # 2D affine
        
        result = minimize(objective, x0, method='Powell')
        
        return result.x
```

## Deformable Registration

```python
class DeformableRegistration:
    def __init__(self, iterations=100, sigma=1.0):
        self.iterations = iterations
        self.sigma = sigma
    
    def demons(self, fixed, moving):
        """
        Diffeomorphic demons algorithm
        
        1. Compute update field
        2. Smooth field
        3. Compose with current transformation
        """
        # Initialize displacement field
        shape = fixed.shape
        displacement = np.zeros(shape + (len(shape),))
        
        for i in range(self.iterations):
            # Compute update field
            grad_fixed = np.gradient(fixed)
            grad_moving = np.gradient(moving)
            
            diff = moving - fixed
            
            # Update rule
            denom = grad_fixed[0]**2 + grad_fixed[1]**2 + diff**2 + 1e-8
            
            update_x = -diff * grad_fixed[0] / denom
            update_y = -diff * grad_fixed[1] / denom
            
            # Smooth update field
            update_x = ndimage.gaussian_filter(update_x, self.sigma)
            update_y = ndimage.gaussian_filter(update_y, self.sigma)
            
            # Compose fields
            displacement[..., 0] += update_x
            displacement[..., 1] += update_y
            
            # Apply transformation
            moving = self.warp_image(moving, displacement)
        
        return displacement, moving
    
    def warp_image(self, image, displacement):
        """Apply displacement field"""
        from scipy.ndimage import map_coordinates
        
        coords = np.meshgrid(*[np.arange(s) for s in image.shape], indexing='ij')
        
        for i in range(len(image.shape)):
            coords[i] = coords[i] + displacement[..., i]
        
        return map_coordinates(image, coords, order=1)
```

## VoxelMorph (Learning-Based)

```python
import torch
import torch.nn as nn

class VoxelMorph(nn.Module):
    """Learning-based deformable registration"""
    
    def __init__(self, in_channels=2):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv2d(in_channels, 16, 3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(16, 32, 3, stride=2, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(32, 32, 3, padding=1),
            nn.LeakyReLU(0.2),
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Conv2d(32, 32, 3, padding=1),
            nn.LeakyReLU(0.2),
            nn.ConvTranspose2d(32, 16, 3, stride=2, padding=1, output_padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv2d(16, 2, 3, padding=1),  # 2D displacement field
        )
    
    def forward(self, fixed, moving):
        """Predict displacement field"""
        # Concatenate inputs
        x = torch.cat([fixed, moving], dim=1)
        
        # Encode
        features = self.encoder(x)
        
        # Decode displacement field
        displacement = self.decoder(features)
        
        # Warp moving image
        warped = self.spatial_transform(moving, displacement)
        
        return warped, displacement
    
    def spatial_transform(self, image, flow):
        """Apply flow field to warp image"""
        # Use grid_sample for differentiable warping
        grid = self.flow_to_grid(flow)
        return torch.nn.functional.grid_sample(image, grid, align_corners=True)
```

## Multi-Modal Fusion

```python
class ImageFusion:
    def __init__(self):
        pass
    
    def wavelet_fusion(self, img1, img2, wavelet='db4', levels=4):
        """
        Wavelet-based image fusion
        
        1. Decompose both images
        2. Fuse coefficients (max rule)
        3. Reconstruct
        """
        import pywt
        
        # Wavelet decomposition
        coeffs1 = pywt.wavedec2(img1, wavelet, level=levels)
        coeffs2 = pywt.wavedec2(img2, wavelet, level=levels)
        
        # Fuse coefficients
        fused_coeffs = []
        for c1, c2 in zip(coeffs1, coeffs2):
            if isinstance(c1, tuple):
                # Detail coefficients - take maximum
                fused = tuple(np.maximum(a, b) for a, b in zip(c1, c2))
            else:
                # Approximation coefficients - average
                fused = (c1 + c2) / 2
            fused_coeffs.append(fused)
        
        # Reconstruct
        fused = pywt.waverec2(fused_coeffs, wavelet)
        
        return fused
    
    def laplacian_pyramid_fusion(self, img1, img2, levels=4):
        """
        Laplacian pyramid fusion
        """
        # Build pyramids
        pyr1 = self.laplacian_pyramid(img1, levels)
        pyr2 = self.laplacian_pyramid(img2, levels)
        
        # Fuse each level
        fused_pyr = []
        for p1, p2 in zip(pyr1, pyr2):
            # Choose based on local energy
            mask = np.abs(p1) > np.abs(p2)
            fused = p1 * mask + p2 * (~mask)
            fused_pyr.append(fused)
        
        # Reconstruct
        return self.reconstruct_pyramid(fused_pyr)
    
    def learned_fusion(self, img1, img2, model):
        """
        Deep learning-based fusion
        """
        # Stack images
        input_tensor = torch.stack([
            torch.from_numpy(img1).float(),
            torch.from_numpy(img2).float()
        ]).unsqueeze(0)
        
        with torch.no_grad():
            fused = model(input_tensor)
        
        return fused.squeeze().numpy()
```

## Evaluation Metrics

```python
class RegistrationMetrics:
    def __init__(self):
        pass
    
    def target_registration_error(self, landmarks_fixed, landmarks_moving):
        """
        TRE = mean distance between corresponding landmarks
        """
        distances = np.sqrt(np.sum((landmarks_fixed - landmarks_moving)**2, axis=1))
        return np.mean(distances), np.std(distances)
    
    def dice_coefficient(self, seg1, seg2):
        """
        Dice = 2 * |A ∩ B| / (|A| + |B|)
        """
        intersection = np.sum(seg1 & seg2)
        return 2 * intersection / (np.sum(seg1) + np.sum(seg2))
    
    def hausdorff_distance(self, surface1, surface2):
        """
        Maximum surface distance
        """
        from scipy.spatial.distance import cdist
        
        distances = cdist(surface1, surface2)
        
        h1 = np.max(np.min(distances, axis=1))
        h2 = np.max(np.min(distances, axis=0))
        
        return max(h1, h2)
```

## Deliverables

1. **Registration Pipeline**: Rigid + deformable
2. **Fusion Algorithm**: Implementation
3. **Results**: On 10 patient cases
4. **Evaluation Metrics**: TRE, Dice, visual
5. **Visualizations**: Registered/fused images

## Project Structure

```
AIDS-3_OmniVision/
├── README.md
├── registration/
│   ├── rigid.py
│   ├── deformable.py
│   └── voxelmorph.py
├── fusion/
│   ├── wavelet.py
│   ├── pyramid.py
│   └── learned.py
├── evaluation/
│   └── metrics.py
├── data/
│   └── patients/
├── run_registration.py
└── solution_template.py
```

## Tips

1. Mutual information works well for multi-modal registration
2. Start with rigid, then refine with deformable
3. Topology preservation is critical for medical images
4. Wavelet fusion preserves details from both modalities
5. Evaluate with both quantitative metrics and visual inspection
