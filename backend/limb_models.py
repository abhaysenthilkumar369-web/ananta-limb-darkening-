import numpy as np

def linear_law(mu, u):
    """ I(mu)/I(1) = 1 - u(1 - mu) """
    return 1 - u * (1 - mu)

def quadratic_law(mu, a, b):
    """ I(mu)/I(1) = 1 - a(1 - mu) - b(1 - mu)^2 """
    return 1 - a * (1 - mu) - b * (1 - mu)**2

def square_root_law(mu, c, d):
    """ I(mu)/I(1) = 1 - c(1 - mu) - d(1 - sqrt(mu)) """
    return 1 - c * (1 - mu) - d * (1 - np.sqrt(mu))

def logarithmic_law(mu, e, f):
    """ I(mu)/I(1) = 1 - e(1 - mu) - f*mu*ln(mu) """
    # mu can be 0 at the extreme limb, np.log(0) is -inf
    # Add a tiny epsilon to prevent math errors
    mu_safe = np.clip(mu, 1e-10, 1.0)
    return 1 - e * (1 - mu_safe) - f * mu_safe * np.log(mu_safe)

def claret_4_param_law(mu, a1, a2, a3, a4):
    """ I(mu)/I(1) = 1 - sum(a_k * (1 - mu^(k/2))) for k=1..4 """
    return 1 - a1*(1 - mu**0.5) - a2*(1 - mu**1.0) - a3*(1 - mu**1.5) - a4*(1 - mu**2.0)

# Dictionary to map string names to their python functions
MODEL_FUNCTIONS = {
    "linear": linear_law,
    "quadratic": quadratic_law,
    "square-root": square_root_law,
    "logarithmic": logarithmic_law,
    "claret": claret_4_param_law
}

MODEL_INITIAL_GUESSES = {
    "linear": [0.5],
    "quadratic": [0.4, 0.2],
    "square-root": [0.4, 0.2],
    "logarithmic": [0.5, 0.1],
    "claret": [0.5, -0.1, 0.4, -0.2]
}

def get_model_latex(model_type: str) -> str:
    latex_strings = {
        "linear": r"\frac{I(\mu)}{I(1)} = 1 - u(1 - \mu)",
        "quadratic": r"\frac{I(\mu)}{I(1)} = 1 - a(1 - \mu) - b(1 - \mu)^2",
        "square-root": r"\frac{I(\mu)}{I(1)} = 1 - c(1 - \mu) - d(1 - \sqrt{\mu})",
        "logarithmic": r"\frac{I(\mu)}{I(1)} = 1 - e(1 - \mu) - f \mu \ln(\mu)",
        "claret": r"\frac{I(\mu)}{I(1)} = 1 - \sum_{k=1}^{4} a_k (1 - \mu^{k/2})"
    }
    return latex_strings.get(model_type, "")
