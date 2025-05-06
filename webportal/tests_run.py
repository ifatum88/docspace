import subprocess
import os
import glob
import tempfile

def render_plantuml(source_text: str, output_dir: str = ".", jar_path='webportal/tools/plantuml-mit-1.2025.2.jar'):
    os.makedirs(output_dir, exist_ok=True)

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.uml', dir=output_dir, delete=False) as uml_file:
        uml_file.write(source_text)
        uml_file.flush()
        uml_filename = os.path.basename(uml_file.name)

    try:
        subprocess.run([
            "java", "-jar", jar_path, "-tsvg", uml_filename, "-o", "."
        ], cwd=output_dir, check=True)

        expected_svg = os.path.join(output_dir, uml_filename.replace(".uml", ".svg"))
        if os.path.exists(expected_svg):
            print(f"✅ SVG файл сгенерирован: {expected_svg}")
        else:
            print("❌ SVG файл не найден. Возможно, возникла ошибка при генерации.")
    except subprocess.CalledProcessError as e:
        print(f"🚨 Ошибка выполнения PlantUML: {e}")

# Пример
pumlstr = "@startuml\nBob -> Alice : hello\n@enduml"
render_plantuml(pumlstr)