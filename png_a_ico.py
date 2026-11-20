from PIL import Image

def generar_ico():
    try:
        img = Image.open("frontend/assets/colibri_temp.png")
        img.save("frontend/assets/colibri.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        print("✅ ¡Icono .ico generado con éxito en frontend/assets/colibri.ico!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generar_ico()
