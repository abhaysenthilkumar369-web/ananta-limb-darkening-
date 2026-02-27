import io
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_plot(mu_arr, i_norm_arr, results):
    """
    Creates the matplotlib plots required for the report and saves them to bytes buffers.
    """
    # Plot 1: Distance vs Gray Value (Drift Scan equivalent, symmetric dome)
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    
    # To simulate a drift scan, we mirror the radial profile
    # Drift scans sweep from -R to +R
    # Since r_norm goes from 0 to 1, we map to actual pixels using an arbitrary radius, or just map -1 to 1 normalized.
    radius = len(mu_arr) # Approx pixels
    r_norm = np.sqrt(1 - np.array(mu_arr)**2)
    
    r_full = np.concatenate((-r_norm[::-1], r_norm))
    i_full = np.concatenate((i_norm_arr[::-1], i_norm_arr))
    
    ax1.plot(r_full, i_full, 'k.', markersize=2, label="Observed Profile")
    
    # Optional smooth curve for the dome
    from scipy.signal import savgol_filter
    if len(i_full) > 5:
        window = min(len(i_full)//10 * 2 + 1, 51)
        if window > 2:
            smooth_i = savgol_filter(i_full, window, 3)
            ax1.plot(r_full, smooth_i, 'crimson', alpha=0.5, label="Smoothed Trend")
            
    ax1.set_title("Distance vs Gray Value", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Normalized Distance (r/R)", fontsize=12)
    ax1.set_ylabel("Normalized Intensity (I / I_max)", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right")
    ax1.text(-0.9, np.min(i_full), "Preceding Limb", fontsize=10, style='italic')
    ax1.text(0.6, np.min(i_full), "Following Limb", fontsize=10, style='italic')

    buf1 = io.BytesIO()
    fig1.savefig(buf1, format='png', dpi=300, bbox_inches='tight')
    buf1.seek(0)
    plt.close(fig1)

    # Plot 2: Solar Limb Darkening (I/I0 vs mu) + Residuals
    fig2 = plt.figure(figsize=(8, 8))
    gs = fig2.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.1)
    
    ax_main = fig2.add_subplot(gs[0])
    ax_res = fig2.add_subplot(gs[1], sharex=ax_main)
    
    # Main Plot
    ax_main.plot(mu_arr, i_norm_arr, 'k.', label="Observational Data")
    
    # Overlay all fitted models
    for res in results:
        ax_main.plot(mu_arr, res['fitted_curve_y'], lw=2, label=f"Fit: {res['model_type'].capitalize()}")
        if len(results) == 1:
            ax_res.plot(mu_arr, res['residuals'], 'k.', alpha=0.5)
            ax_res.axhline(0, color='r', linestyle='--')
            
    ax_main.set_title("Solar Limb Darkening", fontsize=14, fontweight='bold')
    ax_main.set_ylabel("I(μ) / I(1)", fontsize=12)
    ax_main.legend(loc="upper left")
    ax_main.grid(True, alpha=0.3)
    
    # Residual Plot
    ax_res.set_xlabel("μ = cos(θ)", fontsize=12)
    ax_res.set_ylabel("Residuals", fontsize=12)
    ax_res.grid(True, alpha=0.3)
    if len(results) > 1:
        ax_res.text(0.5, 0.5, "Residuals plotted below for single models only", ha='center')
        
    buf2 = io.BytesIO()
    fig2.savefig(buf2, format='png', dpi=300, bbox_inches='tight')
    buf2.seek(0)
    plt.close(fig2)

    return buf1, buf2

def build_pdf_report(mu_arr, i_norm_arr, results):
    """
    Generates a 3-page scientific PDF utilizing ReportLab.
    Returns bytes object of the PDF.
    """
    buf1, buf2 = create_plot(mu_arr, i_norm_arr, results)
    
    out_buf = io.BytesIO()
    doc = SimpleDocTemplate(out_buf, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4))
    
    Story = []
    
    # ========================== PAGE 1 ==========================
    Story.append(Paragraph("ANANTA Limb Darkening Analyser", styles['Title']))
    Story.append(Paragraph("Computational Astrophysical Interpretation Report", styles['Heading2']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("1. Observational Analysis & Drift Scan", styles['Heading3']))
    Story.append(Spacer(1, 12))
    
    txt = ("The stellar disk was automatically detected, and a radial intensity profile was extracted. "
           "The plot below reconstructs a classical solar drift scan by mirroring the extracted radial points, "
           "visualizing the symmetric dome-like structure indicative of photospheric thermal gradients.")
    Story.append(Paragraph(txt, styles['Normal']))
    Story.append(Spacer(1, 12))
    
    img1 = Image(buf1, width=450, height=337)
    Story.append(img1)
    
    Story.append(PageBreak())
    
    # ========================== PAGE 2 ==========================
    Story.append(Paragraph("2. Model Fitting Analysis", styles['Heading3']))
    Story.append(Spacer(1, 12))
    
    img2 = Image(buf2, width=450, height=450)
    Story.append(img2)
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("Statistical Framework & Regression Outcomes", styles['Heading4']))
    
    for res in results:
        Story.append(Spacer(1, 6))
        Story.append(Paragraph(f"Model Law: {res['model_type'].capitalize()}", styles['Bullet']))
        coeff_str = ", ".join([f"{c:.4f}" for c in res['coefficients']])
        err_str = ", ".join([f"{e:.4f}" for e in res['standard_errors']])
        Story.append(Paragraph(f"Coefficients: {coeff_str}", styles['Normal']))
        Story.append(Paragraph(f"Estimated Standard Errors (1σ): {err_str}", styles['Normal']))
        Story.append(Paragraph(f"Coefficient of Determination (R²): {res['r_squared']:.5f}", styles['Normal']))
        Story.append(Paragraph(f"Reduced \u03C7²: {res['reduced_chi_square']:.5f}", styles['Normal']))
    
    Story.append(PageBreak())

    # ========================== PAGE 3 ==========================
    Story.append(Paragraph("3. Computational Astrophysical Interpretation", styles['Heading3']))
    Story.append(Spacer(1, 12))
    
    interp_text = (
        "Limb darkening arises because our line of sight penetrates into different physical depths "
        "depending on the viewing angle (parameterized by \u03BC = cos(\u03B8)). At the disk center (\u03BC=1), "
        "we observe deeper, hotter radiative layers of the photosphere. Near the limb (\u03BC \u2192 0), optical depth "
        "forces us to observe higher, cooler atmospheric layers, leading to the observed intensity dropoff."
    )
    Story.append(Paragraph(interp_text, styles['Normal']))
    Story.append(Spacer(1, 12))
    
    stat_text = (
        "By applying non-linear least squares contour fitting on the unbinned or sigma-clipped "\u03BC" array, "
        "we successfully derive the empirical law coefficients rather than estimating them via theoretic atmospheric models. "
        "The reduced chi-square (\u03C7²_red) and R² coefficient validate the mathematical robustness of the selected law against "
        "the observed intensity profile curvature."
    )
    Story.append(Paragraph(stat_text, styles['Normal']))
    
    doc.build(Story)
    
    out_buf.seek(0)
    return out_buf
