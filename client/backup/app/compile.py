import subprocess
import tempfile
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image

from app.config import Config

# 定義不顯示視窗的 flag
CREATE_NO_WINDOW = 0x08000000

def latex_symbol_to_png(
    tex_code: str,
    compiler: str = "xelatex",
    out_path: str = "symbol.png", 
    background: None | str = None, 
    gray_level: bool = True
):
    """
    Convert LaTeX code into a PNG image
    using xelatex or lualatex.
    Returns: (png_path, width_px, height_px)
    """

    assert compiler in ("xelatex", "lualatex"), "compiler must be xelatex or lualatex"

    with tempfile.TemporaryDirectory(dir=Config.TMP_SAVING_PATH) as tmpdir:
        tmpdir = Path(tmpdir)
        tex_path = tmpdir / "symbol.tex"
        pdf_path = tmpdir / "symbol.pdf"

        # --- Step 1: Write the latex file ---
        tex_content = rf"""
\documentclass[a4paper, 12pt]{{article}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{xeCJK}}
\setCJKmainfont{{標楷體}}
\pagestyle{{empty}}
\begin{{document}}
\noindent
{tex_code}

\end{{document}}
"""
        tex_path.write_text(tex_content, encoding="utf-8")

        # --- Step 2: Compile to PDF ---
        subprocess.run(
            [
                compiler,
                "-interaction=nonstopmode",
                str(tex_path)
            ],
            cwd=tmpdir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, 
            creationflags=CREATE_NO_WINDOW
        )

        # --- Step 4: convert PDF to PNG with white background ---
        with fitz.open(pdf_path) as pdf:
            page = pdf[0]

            mat = fitz.Matrix(2.5, 2.5)
            pix = page.get_pixmap(matrix=mat, alpha=True)

            # Convert pixmap → PIL image
            img = Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
            # Crop to content and add 20px padding
            img = img.crop(img.getbbox())
            border_size = 20
            final_img = Image.new("RGBA", 
                                 (img.width + 2*border_size, img.height + 2*border_size),
                                 (255, 255, 255, 0))
            final_img.paste(img, (border_size, border_size), img)
            img = final_img

            if background is None:
                if gray_level:
                    # Convert pixmap to grayscale while keeping alpha
                    # pix.samples: RGBA; shape: (h*w*4)

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
                if gray_level:
                    img = img.convert("LA")
                bg = Image.new("RGB", img.size, background)
                bg.paste(img, mask=img.split()[-1])  # use alpha channel as mask
                bg.save(out_path, format="PNG")

def compile_tex(tex_code: str) -> str:
    out_path = f"{Config.TMP_SAVING_PATH}/result.png"
    latex_symbol_to_png(tex_code, out_path=out_path, background="#ffffff")
    return out_path
