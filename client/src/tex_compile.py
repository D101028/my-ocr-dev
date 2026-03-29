import os
import subprocess
from pathlib import Path

from PIL import Image, ImageEnhance, ImageChops

from config import Config

try:
    import fitz  # PyMuPDF
except:
    pass 

def latex_symbol_to_png(
    macro,
    compiler="xelatex",
    dpi=300,
    out_path="symbol.png", 
    background=None, 
    gray_level=True
):
    """
    Convert a LaTeX math symbol macro like '\\alpha' into a PNG image
    using xelatex or lualatex.
    Returns: (png_path, width_px, height_px)
    """
    assert compiler in ("xelatex", "lualatex"), "compiler must be xelatex or lualatex"

    tmpdir = Path(Config.WORKING_DIR)
    tex_name = "symbol.tex"
    pdf_name = "symbol.pdf"
    cropped_pdf_name = "symbol-crop.pdf"
    tex_path = tmpdir / tex_name
    cropped_pdf_path = tmpdir / cropped_pdf_name

    # --- Step 1: Write the latex file ---
    tex_content = rf"""
\documentclass[preview,border=2pt]{{standalone}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\begin{{document}}

{macro}

\end{{document}}
"""
    tex_path.write_text(tex_content)

    # --- Step 2: Compile to PDF ---
    p = subprocess.run(
        [
            compiler,
            "-interaction=nonstopmode",
            tex_name
        ],
        cwd=tmpdir,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    if p.returncode:
        print("-"*10, f"stdout: {p.stdout}", "-"*10, f"stderr: {p.stderr}", "-"*10, sep='\n')
        raise Exception("\n".join(("-"*10, f"stdout: {p.stdout}", "-"*10, f"stderr: {p.stderr}", "-"*10)))

    # --- Step 3: Crop PDF to bounding box ---
    p = subprocess.run(
        ["pdfcrop", pdf_name, cropped_pdf_name],
        cwd=tmpdir,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    if p.returncode:
        print("-"*10, f"stdout: {p.stdout}", "-"*10, f"stderr: {p.stderr}", "-"*10, sep='\n')
        raise Exception("\n".join(("-"*10, f"stdout: {p.stdout}", "-"*10, f"stderr: {p.stderr}", "-"*10)))

    # --- Step 4: convert PDF → PNG with white background ---
    with fitz.open(cropped_pdf_path) as pdf:
        page = pdf[0]

        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=True)

        if background is None:
            if gray_level:
                # Convert pixmap to grayscale while keeping alpha
                # pix.samples: RGBA; shape: (h*w*4)

                # Convert pixmap → PIL image
                img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)

                # Split channels
                r, g, b, a = img.split()

                # Convert RGB → grayscale (luminosity)
                gray = Image.merge("RGB", (r, g, b)).convert("L")

                # Recombine gray + original alpha
                final_img = Image.merge("LA", (gray, a))
                final_img.save(out_path)
            else:
                pix.save(out_path)
        else:
            img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
            if gray_level:
                img = img.convert("LA")
            bg = Image.new("RGB", img.size, background)
            bg.paste(img, mask=img.split()[-1])  # use alpha channel as mask
            bg.save(out_path, format="PNG")

    return pix.width, pix.height

def crop_img_obj(img: Image.Image, bg_color: tuple[int, int, int] | None = (255, 255, 255)):
    # Use alpha if requested/available
    if bg_color is None and (img.mode in ("RGBA", "LA") or ("transparency" in img.info)):
        if img.mode not in ("RGBA", "LA"):
            img = img.convert("RGBA")
        alpha = img.getchannel("A")
        bbox = alpha.getbbox()
        return img.crop(bbox) if bbox else img
    else:
        rgb = img.convert("RGB")
        use_bg = bg_color if bg_color is not None else rgb.getpixel((0, 0))
        bg_img = Image.new("RGB", rgb.size, use_bg)
        diff = ImageChops.difference(rgb, bg_img)
        diff = ImageChops.add(diff, diff, 2.0, -10)
        bbox = diff.getbbox()
        return img.crop(bbox) if bbox else img

def create_img(macro: str, save_dir: str) -> str:
    name = os.urandom(8).hex() + ".png"
    fp = f"{save_dir}/{name}"
    latex_symbol_to_png(
        macro, 
        out_path = fp, 
        background = (255,255,255)
    )
    img = ImageEnhance.Contrast(Image.open(fp).convert("L")).enhance(4.0)
    img = crop_img_obj(img, (255,255,255)).convert("L")
    # Add 5px margin
    bg = Image.new("L", (img.width + 10, img.height + 10), 255)
    bg.paste(img, (5, 5))
    img = bg
    
    # Resize if width >= 600
    if img.width >= 600:
        ratio = 600 / img.width
        new_size = (600, int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    img.save(fp)
    return fp

def compile_to_png(raw_tex_code: str) -> str:
    fp = create_img(raw_tex_code, Config.WORKING_DIR)
    return fp

