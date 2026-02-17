# 🛠️ Guía Completa: Instalación Limpia de VS Code + Python en Linux

> **Compatible con:** Ubuntu 20.04 / 22.04 / 24.04 · Debian 11/12 · Linux Mint · Pop!_OS  
> **Última revisión:** 2025  
> **Requisito previo:** Acceso a `sudo` y conexión a internet

---

## 📋 Tabla de contenidos

1. [Antes de empezar](#antes-de-empezar)
2. [Paso 1 — Cerrar VS Code](#paso-1--cerrar-vs-code)
3. [Paso 2 — Desinstalar VS Code por completo](#paso-2--desinstalar-vs-code-por-completo)
4. [Paso 3 — Limpiar repositorios y claves antiguas](#paso-3--limpiar-repositorios-y-claves-antiguas)
5. [Paso 4 — Instalar VS Code (método oficial)](#paso-4--instalar-vs-code-método-oficial)
6. [Paso 5 — Python en Ubuntu: qué tocar y qué NO tocar](#paso-5--python-en-ubuntu-qué-tocar-y-qué-no-tocar)
7. [Paso 6 — Instalar Miniconda (gestor de entornos recomendado)](#paso-6--instalar-miniconda-gestor-de-entornos-recomendado)
8. [Paso 7 — Crear y gestionar entornos con Conda](#paso-7--crear-y-gestionar-entornos-con-conda)
9. [Paso 8 — Instalar librerías esenciales](#paso-8--instalar-librerías-esenciales)
10. [Paso 9 — Instalar extensión de Python en VS Code](#paso-9--instalar-extensión-de-python-en-vs-code)
11. [Paso 10 — Configuración recomendada de VS Code](#paso-10--configuración-recomendada-de-vs-code)
12. [Paso 11 — Verificación final](#paso-11--verificación-final)
13. [Solución de problemas frecuentes](#solución-de-problemas-frecuentes)
14. [Desinstalar todo (si lo necesitas en el futuro)](#desinstalar-todo-si-lo-necesitas-en-el-futuro)

---

## Antes de empezar

### ¿Por qué hacer una instalación limpia?

VS Code instalado desde fuentes no oficiales (Snap, paquetes .deb de terceros, PPAs externos) puede generar conflictos con actualizaciones, firmas GPG corruptas o repositorios desactualizados. Esta guía utiliza el **repositorio oficial de Microsoft**, que es el método más estable y seguro.

### Verificar si ya tienes VS Code instalado

```bash
which code
dpkg -l | grep code
snap list | grep code
```

> ⚠️ Si VS Code fue instalado mediante **Snap**, los pasos de desinstalación son diferentes. Ver sección de [Solución de problemas](#solución-de-problemas-frecuentes).

### Hacer una copia de seguridad de tus extensiones (opcional pero recomendado)

Si tienes extensiones que deseas conservar, expórtalas antes de borrar todo:

```bash
code --list-extensions > ~/mis-extensiones-vscode.txt
```

Podrás reinstalarlas más adelante con:

```bash
cat ~/mis-extensiones-vscode.txt | xargs -L 1 code --install-extension
```

---

## Paso 1 — Cerrar VS Code

Antes de modificar cualquier archivo, asegúrate de que VS Code **no esté en ejecución**:

```bash
pkill code
```

Verificar que ya no hay procesos activos:

```bash
pgrep -l code
```

> Si el comando no devuelve nada, el proceso está cerrado correctamente.

---

## Paso 2 — Desinstalar VS Code por completo

### Si fue instalado con `apt`

```bash
# Elimina el paquete
sudo apt remove code -y

# Purga también los archivos de configuración del sistema
sudo apt purge code -y
```

> **Diferencia entre `remove` y `purge`:**  
> - `remove` → elimina el programa pero conserva archivos de configuración en `/etc`  
> - `purge` → elimina todo, incluyendo configuraciones del sistema

### Eliminar configuraciones y datos del usuario

```bash
# Configuración del editor (temas, keybindings, settings.json, etc.)
rm -rf ~/.config/Code

# Extensiones instaladas localmente
rm -rf ~/.vscode
```

> ⚠️ **Advertencia:** Estos comandos son irreversibles. Si no hiciste una copia de las extensiones en el Paso 0, se perderán.

### Si fue instalado con Snap (caso alternativo)

```bash
sudo snap remove code
rm -rf ~/snap/code
```

### Si fue instalado manualmente con un paquete `.deb`

```bash
sudo dpkg -r code
sudo dpkg --purge code
```

---

## Paso 3 — Limpiar repositorios y claves antiguas

Los repositorios y firmas GPG de instalaciones anteriores pueden causar errores al actualizar. Elimínalos antes de agregar los nuevos:

```bash
# Elimina la lista de repositorios de VS Code
sudo rm -f /etc/apt/sources.list.d/vscode.list

# Elimina la clave GPG antigua de Microsoft
sudo rm -f /usr/share/keyrings/packages.microsoft.gpg

# También elimina claves alternativas que pudieran existir
sudo rm -f /etc/apt/trusted.gpg.d/microsoft.gpg

# Actualiza la lista de paquetes para confirmar que no hay errores
sudo apt update
```

> Si `apt update` muestra advertencias sobre repositorios faltantes, es normal en este punto. Se resolverán en el siguiente paso.

---

## Paso 4 — Instalar VS Code (método oficial)

### 1️⃣ Instalar dependencias necesarias

```bash
sudo apt install wget gpg apt-transport-https ca-certificates -y
```

| Paquete | Propósito |
|---|---|
| `wget` | Descargar la clave GPG de Microsoft |
| `gpg` | Verificar la autenticidad de los paquetes |
| `apt-transport-https` | Permite que `apt` use repositorios HTTPS |
| `ca-certificates` | Certificados de autoridades de certificación (HTTPS) |

### 2️⃣ Agregar la clave GPG oficial de Microsoft

```bash
wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null
```

**¿Qué hace cada parte?**

- `wget -qO-` → descarga la clave en modo silencioso y la envía a stdout
- `gpg --dearmor` → convierte la clave de formato ASCII armored a binario (`.gpg`)
- `sudo tee ... > /dev/null` → guarda el resultado con permisos root, suprimiendo la salida en pantalla

Verificar que la clave se guardó correctamente:

```bash
ls -lh /usr/share/keyrings/packages.microsoft.gpg
```

### 3️⃣ Agregar el repositorio oficial de Microsoft

```bash
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] \
https://packages.microsoft.com/repos/code stable main" \
  | sudo tee /etc/apt/sources.list.d/vscode.list
```

> **Nota para arquitecturas ARM (Raspberry Pi, Mac M1/M2 con Linux):**  
> Reemplaza `arch=amd64` por `arch=arm64` o `arch=armhf` según corresponda.  
> Verifica tu arquitectura con: `dpkg --print-architecture`

### 4️⃣ Actualizar la lista de paquetes e instalar VS Code

```bash
sudo apt update
sudo apt install code -y
```

### 5️⃣ Verificar la instalación

```bash
code --version
```

La salida debería verse similar a:

```
1.89.1
b58957e67ee1e712cebf466b995adf4c5307b2bd
x64
```

> Los tres valores corresponden a: versión del editor, hash del commit y arquitectura.

---

## Paso 5 — Python en Ubuntu: qué tocar y qué NO tocar

### ⚠️ El Python del sistema es intocable

Ubuntu y Debian dependen de Python internamente. El intérprete que viene instalado en `/usr/bin/python3` es utilizado por herramientas críticas del sistema operativo como `apt`, `NetworkManager`, `gnome-shell`, actualizadores de software y scripts de administración.

**Nunca debes:**

- Desinstalar o reemplazar el `python3` del sistema
- Actualizar paquetes del sistema con `pip install --upgrade` a nivel global (riesgo de romper dependencias del SO)
- Ejecutar `sudo pip install` para instalar librerías de trabajo

Intentar modificar este Python puede resultar en un sistema inestable o incluso inutilizable que requiere reinstalación completa del SO.

### Verificar cuál es el Python del sistema (solo lectura)

```bash
# Ver la versión
python3 --version

# Ver dónde vive (NO es el que usarás para programar)
which python3
# → /usr/bin/python3

# Ver qué paquetes tiene instalados (no los toques)
pip3 list
```

### ¿Puedo actualizar pip del sistema?

Con precaución. Ubuntu a veces bloquea esto con el error `externally-managed-environment` a partir de Ubuntu 23.04+. Lo más seguro es **no actualizar pip a nivel global** y hacerlo únicamente dentro de entornos de Conda o venv (lo veremos en los pasos siguientes).

Si necesitas actualizar pip del sistema (no recomendado para uso general), el único método seguro en Ubuntu moderno es:

```bash
# Ubuntu 22.04 o anterior
pip3 install --upgrade pip --user

# Ubuntu 23.04+ (con entornos gestionados externamente)
# Mejor no hacerlo — usa Miniconda en su lugar
```

> 💡 **La solución correcta** para trabajar con Python en Ubuntu **no es tocar el Python del sistema**, sino instalar un gestor de entornos independiente. La herramienta más robusta y recomendada para esto es **Miniconda**.

---

## Paso 6 — Instalar Miniconda (gestor de entornos recomendado)

### ¿Qué es Miniconda y por qué usarlo?

**Miniconda** es una distribución mínima de [Conda](https://docs.conda.io/), el gestor de paquetes y entornos de la familia Anaconda. A diferencia de instalar Python directamente en el sistema, Miniconda:

- Instala su **propio Python completamente separado** del sistema (`~/miniconda3/`)
- Permite crear múltiples **entornos aislados**, cada uno con su propia versión de Python y librerías
- Gestiona dependencias de forma mucho más robusta que `pip` para librerías científicas (NumPy, TensorFlow, etc.)
- **Nunca toca el Python del sistema operativo**
- Funciona sin `sudo` para la mayoría de las operaciones

### Comparativa: venv vs Conda

| Característica | `venv` + `pip` | Miniconda |
|---|---|---|
| Aislamiento del sistema | ✅ Sí | ✅ Sí |
| Múltiples versiones de Python | ❌ No (usa la del sistema) | ✅ Sí |
| Librerías científicas/binarias | ⚠️ A veces problemas | ✅ Excelente |
| Requiere `sudo` | ❌ No | ❌ No |
| Tamaño inicial | ~5 MB | ~60 MB |
| Recomendado para ciencia de datos | ⚠️ Básico | ✅ Sí |

### 1️⃣ Descargar el instalador

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
```

> Para sistemas **ARM64** (Raspberry Pi 4+, algunas laptops):
> ```bash
> wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh -O ~/miniconda.sh
> ```

### 2️⃣ Verificar la integridad del archivo (recomendado)

```bash
sha256sum ~/miniconda.sh
```

Compara el hash resultante con el que aparece en la [página oficial de Miniconda](https://docs.anaconda.com/miniconda/). Si coinciden, el archivo es auténtico.

### 3️⃣ Ejecutar el instalador

```bash
bash ~/miniconda.sh
```

Durante la instalación:
- Acepta la licencia escribiendo `yes`
- Confirma la ruta de instalación (por defecto `~/miniconda3` — recomendada, no requiere `sudo`)
- Cuando pregunte si deseas inicializar Conda: responde **`yes`** (esto agrega Conda al PATH en tu `~/.bashrc`)

### 4️⃣ Aplicar los cambios al shell actual

```bash
source ~/.bashrc
```

### 5️⃣ Verificar la instalación

```bash
conda --version
# conda 24.x.x

which python
# ~/miniconda3/bin/python  ← Conda ya tiene su propio Python, separado del sistema

python --version
# Python 3.12.x
```

> Nota: el Python del sistema sigue intacto en `/usr/bin/python3`. Conda usa el suyo propio en `~/miniconda3/`.

### 6️⃣ Limpiar el instalador

```bash
rm ~/miniconda.sh
```

### Actualizar Conda a la última versión

```bash
conda update -n base -c defaults conda -y
```

### Desactivar la activación automática del entorno base (opcional)

Por defecto Conda activa el entorno `base` al abrir cada terminal. Si prefieres que no lo haga automáticamente:

```bash
conda config --set auto_activate_base false
```

Para activarlo manualmente cuando lo necesites:

```bash
conda activate base
```

---

## Paso 7 — Crear y gestionar entornos con Conda

### ¿Por qué crear entornos separados?

Cada proyecto puede requerir versiones distintas de Python o librerías incompatibles entre sí. Los entornos de Conda resuelven esto creando espacios completamente aislados, sin afectar ni el sistema ni otros proyectos.

### Crear un entorno nuevo

```bash
# Sintaxis básica: nombre del entorno + versión de Python
conda create -n mi-proyecto python=3.11 -y
```

```bash
# Puedes usar cualquier versión de Python disponible
conda create -n data-science python=3.12 -y
conda create -n legacy-app python=3.9 -y
```

> El entorno se guarda en `~/miniconda3/envs/mi-proyecto/` y es completamente independiente.

### Activar un entorno

```bash
conda activate mi-proyecto
```

El prompt de la terminal cambiará para indicar el entorno activo:

```
(mi-proyecto) usuario@pc:~$
```

### Verificar que estás en el entorno correcto

```bash
which python
# ~/miniconda3/envs/mi-proyecto/bin/python

python --version
# Python 3.11.x

pip --version
# pip 24.x from ~/miniconda3/envs/mi-proyecto/...
```

### Actualizar pip dentro del entorno (seguro aquí)

```bash
# Solo ejecuta esto DENTRO del entorno activado
pip install --upgrade pip
```

### Desactivar el entorno

```bash
conda deactivate
```

### Ver todos tus entornos

```bash
conda env list
# o equivalentemente:
conda info --envs
```

Salida esperada:

```
# conda environments:
#
base                     ~/miniconda3
mi-proyecto           *  ~/miniconda3/envs/mi-proyecto
data-science             ~/miniconda3/envs/data-science
```

El `*` indica el entorno activo actualmente.

### Eliminar un entorno (cuando ya no lo necesites)

```bash
conda env remove -n mi-proyecto
```

---

## Paso 8 — Instalar librerías esenciales

Siempre activa primero el entorno donde quieres instalar:

```bash
conda activate mi-proyecto
```

### Instalar con Conda (preferido para librerías científicas)

Conda resuelve dependencias binarias mejor que pip, especialmente para librerías con componentes en C/C++:

```bash
# Ciencia de datos y análisis
conda install numpy pandas matplotlib seaborn -y

# Machine Learning
conda install scikit-learn -y

# Notebooks interactivos
conda install jupyter notebook -y
```

### Instalar con pip (cuando el paquete no está en Conda)

```bash
# pip funciona perfectamente dentro de un entorno Conda
pip install requests httpx beautifulsoup4

# Librerías de IA / LLMs
pip install openai anthropic langchain

# Herramientas de desarrollo
pip install black ruff pytest
```

> **Regla de oro:** Instala primero con `conda install`. Si el paquete no está disponible, usa `pip install`. Mezclar ambos es seguro **siempre que actives el entorno primero**.

### Tabla de librerías por categoría

| Categoría | Librería | Instalación |
|---|---|---|
| Arrays y matrices | `numpy` | `conda install numpy` |
| Datos tabulares | `pandas` | `conda install pandas` |
| Gráficas básicas | `matplotlib` | `conda install matplotlib` |
| Gráficas estadísticas | `seaborn` | `conda install seaborn` |
| Machine Learning | `scikit-learn` | `conda install scikit-learn` |
| Deep Learning (CPU) | `tensorflow` | `pip install tensorflow` |
| Deep Learning (GPU) | `pytorch` | Ver [pytorch.org](https://pytorch.org/get-started/locally/) |
| Notebooks | `jupyter` | `conda install jupyter` |
| HTTP / APIs | `requests` | `pip install requests` |
| Web scraping | `beautifulsoup4` | `pip install beautifulsoup4` |
| Variables de entorno | `python-dotenv` | `pip install python-dotenv` |
| Formateo de código | `black` | `pip install black` |
| Linting | `ruff` | `pip install ruff` |
| Tests | `pytest` | `pip install pytest` |

### Guardar y reproducir un entorno (para compartir proyectos)

```bash
# Exportar todas las dependencias del entorno activo
conda env export > environment.yml

# Recrear el entorno en otra máquina desde el archivo
conda env create -f environment.yml
```

```bash
# Alternativa solo con pip (estilo clásico)
pip freeze > requirements.txt
pip install -r requirements.txt
```

---

## Paso 9 — Instalar extensión de Python en VS Code

### Método por terminal (recomendado para automatización)

```bash
code --install-extension ms-python.python
```

### Extensiones adicionales recomendadas para Python

```bash
# Análisis estático avanzado (autocomplete potente)
code --install-extension ms-python.pylance

# Jupyter Notebooks dentro de VS Code
code --install-extension ms-toolsai.jupyter

# Formateador de código Black
code --install-extension ms-python.black-formatter

# Linter moderno y ultra rápido
code --install-extension charliermarsh.ruff
```

### Verificar extensiones instaladas

```bash
code --list-extensions
```

### Seleccionar el intérprete de Conda en VS Code

VS Code puede detectar los entornos de Conda automáticamente:

1. Abre cualquier archivo `.py`
2. Presiona `Ctrl + Shift + P`
3. Escribe: *"Python: Select Interpreter"*
4. Verás una lista que incluye tus entornos de Conda, por ejemplo:
   ```
   Python 3.11.x ('mi-proyecto': conda)  ~/miniconda3/envs/mi-proyecto/bin/python
   Python 3.12.x ('data-science': conda) ~/miniconda3/envs/data-science/bin/python
   Python 3.12.x ('base': conda)         ~/miniconda3/bin/python
   ```
5. Selecciona el entorno del proyecto en el que estás trabajando

> VS Code recordará el intérprete seleccionado por cada carpeta de proyecto (workspace).

---

## Paso 10 — Configuración recomendada de VS Code

### Abrir el archivo de configuración

```bash
# Desde terminal
code ~/.config/Code/User/settings.json
```

O dentro de VS Code: `Ctrl + Shift + P` → *"Open User Settings (JSON)"*

### Configuración sugerida para Python con Conda

```json
{
  "editor.fontSize": 14,
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "editor.formatOnSave": true,
  "editor.rulers": [79, 120],
  "files.autoSave": "onFocusChange",
  "terminal.integrated.defaultProfile.linux": "bash",

  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  },

  "python.condaPath": "~/miniconda3/bin/conda",
  "python.terminal.activateEnvironment": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

> **Nota:** No pongas una ruta fija en `python.defaultInterpreterPath` si usas múltiples entornos. Deja que VS Code gestione el intérprete por workspace mediante *"Select Interpreter"*.

---

## Paso 11 — Verificación final

Ejecuta todos los siguientes comandos y confirma que no hay errores:

```bash
# VS Code
code --version

# Python del SISTEMA (no lo toques, solo confirma que sigue intacto)
/usr/bin/python3 --version

# Conda
conda --version

# Activar entorno y verificar Python de Conda
conda activate mi-proyecto
which python        # debe apuntar a ~/miniconda3/envs/...
python --version
pip --version

# Extensiones de Python instaladas en VS Code
code --list-extensions | grep ms-python
```

### Prueba rápida de funcionamiento

```bash
# Con el entorno activado
conda activate mi-proyecto

# Crear un archivo de prueba
cat > /tmp/test_env.py << 'EOF'
import sys
import numpy as np
import pandas as pd

print(f"Python: {sys.version}")
print(f"Ejecutable: {sys.executable}")
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
print("✅ Todo funciona correctamente")
EOF

python /tmp/test_env.py

# Abrirlo en VS Code
code /tmp/test_env.py
```

---

## Solución de problemas frecuentes

### ❌ Error: `NO_PUBKEY` al ejecutar `apt update`

```
W: GPG error: https://packages.microsoft.com/repos/code stable InRelease:
   The following signatures couldn't be verified because the public key
   is not available: NO_PUBKEY EB3E94ADBE1229CF
```

**Solución:**

```bash
sudo rm -f /usr/share/keyrings/packages.microsoft.gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc \
  | gpg --dearmor \
  | sudo tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null
sudo apt update
```

---

### ❌ Error: `code: command not found` tras la instalación

VS Code no está en el PATH. Verifica dónde fue instalado:

```bash
which code || find /usr -name "code" 2>/dev/null
```

Si no aparece, prueba reinstalar:

```bash
sudo apt install --reinstall code
```

---

### ❌ VS Code instalado con Snap en conflicto con la versión apt

```bash
# Eliminar la versión Snap primero
sudo snap remove code

# Luego continuar desde el Paso 3
```

---

### ❌ Error: `externally-managed-environment` al usar pip

En Ubuntu 23.04+ aparece este error al intentar `pip install` fuera de un entorno:

```
error: externally-managed-environment
× This environment is externally managed
```

**Causa:** Ubuntu protege su Python del sistema para evitar conflictos.  
**Solución correcta:** Nunca instales paquetes en el Python del sistema. Usa siempre un entorno de Conda:

```bash
conda activate mi-proyecto
pip install nombre-paquete
```

---

### ❌ `conda: command not found` después de instalar Miniconda

El shell no cargó los cambios del instalador:

```bash
source ~/.bashrc
# o si usas zsh:
source ~/.zshrc
```

Si persiste, agrega manualmente al final de `~/.bashrc`:

```bash
echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

### ❌ VS Code no detecta los entornos de Conda

```bash
# Asegúrate de que conda está en el PATH
which conda

# Configura la ruta en VS Code settings.json
```

```json
"python.condaPath": "/home/TU_USUARIO/miniconda3/bin/conda"
```

Luego recarga VS Code: `Ctrl + Shift + P` → *"Developer: Reload Window"*

---

## Desinstalar todo (si lo necesitas en el futuro)

```bash
# 1. Cerrar VS Code
pkill code

# 2. Desinstalar VS Code
sudo apt remove code -y
sudo apt purge code -y

# 3. Eliminar configuraciones del usuario de VS Code
rm -rf ~/.config/Code
rm -rf ~/.vscode

# 4. Limpiar repositorios y claves de Microsoft
sudo rm -f /etc/apt/sources.list.d/vscode.list
sudo rm -f /usr/share/keyrings/packages.microsoft.gpg

# 5. Actualizar lista de paquetes
sudo apt update

# 6. Eliminar Miniconda completamente
rm -rf ~/miniconda3
rm -rf ~/.conda

# 7. Limpiar las líneas que Conda agregó a .bashrc
# Abre ~/.bashrc y elimina el bloque entre:
# >>> conda initialize >>> ... <<< conda initialize <<<
```

> ⚠️ El Python del sistema (`/usr/bin/python3`) **no debe desinstalarse**. El sistema operativo lo necesita.

---

## 📌 Resumen de comandos (referencia rápida)

```bash
# ─── LIMPIEZA VS CODE ────────────────────────────────────
pkill code
sudo apt remove code -y && sudo apt purge code -y
rm -rf ~/.config/Code ~/.vscode
sudo rm -f /etc/apt/sources.list.d/vscode.list /usr/share/keyrings/packages.microsoft.gpg
sudo apt update

# ─── INSTALACIÓN VS CODE ─────────────────────────────────
sudo apt install wget gpg apt-transport-https ca-certificates -y
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" | sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update && sudo apt install code -y
code --version

# ─── MINICONDA ───────────────────────────────────────────
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh        # responde "yes" a todo
source ~/.bashrc
rm ~/miniconda.sh
conda update -n base -c defaults conda -y
conda --version

# ─── CREAR Y USAR ENTORNO ────────────────────────────────
conda create -n mi-proyecto python=3.11 -y
conda activate mi-proyecto
pip install --upgrade pip

# ─── LIBRERÍAS ESENCIALES ────────────────────────────────
conda install numpy pandas matplotlib seaborn scikit-learn jupyter -y
pip install requests python-dotenv black ruff pytest

# ─── EXTENSIONES VS CODE ─────────────────────────────────
code --install-extension ms-python.python
code --install-extension ms-python.pylance
code --install-extension ms-toolsai.jupyter
code --install-extension ms-python.black-formatter
code --install-extension charliermarsh.ruff
```

---

> 💡 **Tips finales:**
> - VS Code se actualiza automáticamente con `sudo apt upgrade` gracias al repositorio de Microsoft.
> - Siempre activa tu entorno Conda antes de trabajar: `conda activate mi-proyecto`.
> - Nunca uses `sudo pip install` ni modifiques el Python de `/usr/bin/`.
> - Para cada proyecto nuevo, crea un entorno nuevo: `conda create -n nuevo-proyecto python=3.11`.
