from PIL import Image, ImageOps
import numpy as np
import os

def aplicar_paleta_colibri():
    ruta_entrada = "frontend/assets/logo_base.png"
    ruta_salida = "frontend/assets/logo_colibri.png"

    if not os.path.exists(ruta_entrada):
        print("❌ Error: No se encontró logo_base.png")
        return

    # 1. Cargar imagen y convertir a RGBA
    img = Image.open(ruta_entrada).convert("RGBA")
    
    # 2. Hacerla más grande para que se vea nítida
    img = img.resize((512, 512), Image.Resampling.LANCZOS)
    
    # 3. Convertir a array de numpy para manipular colores
    data = np.array(img)
    
    # 4. Crear una máscara de transparencia basada en qué tan oscuro es el píxel
    # (Asumimos que el logo original es oscuro sobre fondo blanco)
    gray = np.mean(data[:, :, :3], axis=2)
    alpha = 255 - gray # Los píxeles oscuros se vuelven opacos, los blancos transparentes
    
    # 5. Aplicar degradado de colores (Verde Menta -> Azul -> Morado)
    # Degradado vertical
    height, width = alpha.shape
    
    # Definir colores
    mint = np.array([61, 186, 137])
    blue = np.array([74, 144, 226])
    purple = np.array([155, 89, 182])
    
    # Crear gradiente
    gradiente = np.zeros((height, width, 3))
    for y in range(height):
        ratio = y / height
        if ratio < 0.5:
            # De menta a azul
            t = ratio * 2
            gradiente[y, :] = mint * (1 - t) + blue * t
        else:
            # De azul a morado
            t = (ratio - 0.5) * 2
            gradiente[y, :] = blue * (1 - t) + purple * t

    # 6. Combinar todo
    final_data = np.zeros((height, width, 4), dtype=np.uint8)
    final_data[:, :, :3] = gradiente
    final_data[:, :, 3] = alpha.astype(np.uint8)
    
    # 7. Guardar
    final_img = Image.fromarray(final_data)
    final_img.save(ruta_salida)
    print(f"✅ ¡Logo generado con éxito en {ruta_salida}!")

if __name__ == "__main__":
    try:
        import numpy
    except ImportError:
        print("Instalando numpy...")
        os.system("pip install numpy")
        
    aplicar_paleta_colibri()