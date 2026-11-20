import cairosvg
from PIL import Image
import io

def crear_ico_desde_svg():
    # Ruta del SVG que generó Gemini (asegúrate de guardarlo como 'icono_colibri.svg' en la raíz)
    svg_path = "icono_colibri.svg"
    ico_path = "frontend/assets/colibri.ico"
    png_temp = "frontend/assets/colibri_temp.png"

    try:
        # 1. Convertir SVG a PNG (512x512 para buena calidad)
        cairosvg.svg2png(url=svg_path, write_to=png_temp, output_width=512, output_height=512)
        
        # 2. Cargar el PNG y guardarlo como .ICO multi-resolución
        img = Image.open(png_temp)
        img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        
        print(f"✅ ¡Icono .ico generado con éxito en {ico_path}!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Asegúrate de tener instalado 'cairosvg' y 'pillow' (pip install cairosvg pillow)")

if __name__ == "__main__":
    crear_ico_desde_svg()