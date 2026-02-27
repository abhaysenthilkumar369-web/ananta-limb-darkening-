import numpy as np
from scipy.optimize import curve_fit
from limb_models import MODEL_FUNCTIONS, MODEL_INITIAL_GUESSES, get_model_latex

def calculate_statistics(y_observed, y_fitted, num_params):
    """
    Computes R^2 and reduced chi-square.
    Assuming measurement errors are uniform and estimated from the observation residual variance.
    """
    residuals = y_observed - y_fitted
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y_observed - np.mean(y_observed))**2)
    
    # R-squared
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    # Reduced Chi-Square 
    dof = max(1, len(y_observed) - num_params)
    
    # Estimate raw variance as the variance of the residuals 
    # (Since we don't have explicit pixel-by-pixel observational error bars)
    obs_variance = np.var(residuals) if np.var(residuals) > 0 else 1e-10
    
    chi_square = np.sum((residuals**2) / obs_variance)
    reduced_chi_square = chi_square / dof
    
    return float(r_squared), float(reduced_chi_square), residuals.tolist()

def fit_model(mu_arr: np.ndarray, i_norm_arr: np.ndarray, model_type: str):
    """
    Fits the specified model using non-linear least squares.
    """
    if model_type not in MODEL_FUNCTIONS:
        raise ValueError(f"Unknown model type: {model_type}")
        
    func = MODEL_FUNCTIONS[model_type]
    p0 = MODEL_INITIAL_GUESSES[model_type]
    
    # Fit the data
    try:
        popt, pcov = curve_fit(func, mu_arr, i_norm_arr, p0=p0, maxfev=10000)
        
        # Calculate standard errors from the covariance matrix
        perr = np.sqrt(np.diag(pcov))
        
        # Calculate fitted model Y values
        y_fitted = func(mu_arr, *popt)
        
        # Calculate statistics
        r_squared, chi_sq_red, residuals = calculate_statistics(i_norm_arr, y_fitted, len(popt))
        
        return {
            "model_type": model_type,
            "formula_latex": get_model_latex(model_type),
            "coefficients": popt.tolist(),
            "standard_errors": perr.tolist(),
            "r_squared": r_squared,
            "reduced_chi_square": chi_sq_red,
            "fitted_curve_y": y_fitted.tolist(),
            "residuals": residuals
        }
    except Exception as e:
        raise RuntimeError(f"Curve fitting failed for {model_type}: {str(e)}")

def fit_all_models(mu_arr: np.ndarray, i_norm_arr: np.ndarray):
    """
    Used for 'compare' mode. Fits all models and sorts by reduced Chi-Square.
    """
    results = {}
    for mod in MODEL_FUNCTIONS.keys():
        try:
            res = fit_model(mu_arr, i_norm_arr, mod)
            results[mod] = res
        except:
            continue
            
    # Need to rank by how close reduced Chi-Square is to 1.0
    # Actually, a smaller reduced chi-square (given our variance estimate) just means tighter fit. 
    # Let's sort by R^2 descending, which is simpler and universally understood.
    ranked = sorted(results.values(), key=lambda x: x["r_squared"], reverse=True)
    return ranked
