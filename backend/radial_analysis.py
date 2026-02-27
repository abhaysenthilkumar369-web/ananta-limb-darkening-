import numpy as np

def extract_radial_profile(img_np: np.ndarray, cx: int, cy: int, radius: int):
    """
    Extracts intensity as a function of radial distance from the center.
    Converts r to mu = sqrt(1 - (r/R)^2).
    Applies sigma clipping and returns normalized intensity values.
    """
    Y, X = np.indices(img_np.shape)
    
    # Calculate distance from center for every pixel
    R = np.sqrt((X - cx)**2 + (Y - cy)**2)
    
    # Mask pixels outside the disk and invalid centers
    mask = R <= radius
    r_valid = R[mask]
    i_valid = img_np[mask].astype(float)
    
    # We want to perform radial binning to smooth out the noise
    # We bin distances into integer pixel groupings
    r_int = r_valid.astype(int)
    
    # Calculate mean intensity per radial bin
    max_r = int(np.max(r_int))
    r_binned = np.arange(max_r + 1)
    i_binned = np.zeros(max_r + 1)
    
    for r_val in r_binned:
        pixels_in_bin = i_valid[r_int == r_val]
        if len(pixels_in_bin) > 0:
            # Sigma clipping to remove spikes (ex. from cosmic rays or dead pixels)
            mean, std = np.mean(pixels_in_bin), np.std(pixels_in_bin)
            clip_mask = np.abs(pixels_in_bin - mean) < (3 * std)
            valid_pixels = pixels_in_bin[clip_mask]
            
            i_binned[r_val] = np.mean(valid_pixels) if len(valid_pixels) > 0 else np.nan
        else:
            i_binned[r_val] = np.nan
            
    # Remove NaN values
    valid_mask = ~np.isnan(i_binned)
    r_binned = r_binned[valid_mask]
    i_binned = i_binned[valid_mask]
    
    # Normalize radius
    r_norm = r_binned / radius
    r_norm = np.clip(r_norm, 0, 1)
    
    # Convert to mu
    mu_arr = np.sqrt(1 - r_norm**2)
    
    # Normalize intensity
    center_idx = min(10, len(i_binned)-1)
    i_max = np.max(i_binned[:center_idx+1]) if len(i_binned) > 0 else 1
    if i_max == 0: i_max = 1 
    
    i_norm_arr = i_binned / i_max
    
    # Scipy needs arrays sorted nicely by the x-variable (mu)
    sort_idx = np.argsort(mu_arr)
    return mu_arr[sort_idx], i_norm_arr[sort_idx]
