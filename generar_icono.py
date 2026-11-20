from PIL import Image, ImageDraw

def crear_icono_colibri():
    # Tamaño base (los iconos .ico usan 256x256 como estándar moderno)
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colores exactos de la paleta
    mint = (61, 186, 137, 255)      # #3DBA89
    blue = (74, 144, 226, 255)      # #4A90E2
    purple = (155, 89, 182, 255)    # #9B59B6
    bg = (15, 22, 38, 255)          # #0F1626 (fondo oscuro)

    # 1. Dibujar fondo circular (como un logo moderno)
    draw.ellipse([(10, 10), (size-10, size-10)], fill=bg)

    # 2. Ala superior (Azul) - un triángulo estilizado
    wing_top = [(120, 100), (220, 40), (200, 120), (130, 140)]
    draw.polygon(wing_top, fill=blue)

    # 3. Ala inferior (Morado) - otro triángulo
    wing_bottom = [(120, 140), (190, 210), (140, 190), (100, 160)]
    draw.polygon(wing_bottom, fill=purple)

    # 4. Cuerpo (Verde Menta) - una forma de gota
    body = [(110, 130), (140, 110), (150, 170), (120, 210), (90, 180)]
    draw.polygon(body, fill=mint)

    # 5. Pico (Azul) - una línea fina
    beak = [(110, 130), (40, 140), (110, 135)]
    draw.polygon(beak, fill=blue)

    # 6. Ojo (Blanco)
    draw.ellipse([(115, 120), (125, 130)], fill=(255, 255, 255, 255))

    # 7. Suavizar bordes
    img = img.resize((256, 256), Image.Resampling.LANCZOS)

    # Guardar como .ico con múltiples resoluciones (Windows usa varias)
    img.save("frontend/assets/colibri.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("✅ Icono colibri.ico generado en frontend/assets/")

if __name__ == "__main__":
    crear_icono_colibri()