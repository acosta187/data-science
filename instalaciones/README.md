# 🐍 Guía de instalación — Entorno `data_science` con Anaconda

## Requisitos previos

- [Anaconda](https://www.anaconda.com/download) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html) instalado
- Terminal (Linux/Mac) o Anaconda Prompt (Windows)

---

## ⚡ Instalación en un solo comando

```bash
conda env create -f environment.yml && conda activate data_science && python verify.py
```

Esto hace las tres cosas de una vez:
1. Crea el entorno con todas las librerías
2. Lo activa
3. Verifica que todo esté correctamente instalado

---

## 📋 Paso a paso (si prefieres más control)

### 1. Crear el entorno

```bash
conda env create -f environment.yml
```

### 2. Activar el entorno

```bash
conda activate data_science
```

### 3. Verificar la instalación

```bash
python verify.py
```

Deberías ver algo como:

```
✅ Ambiente data_science listo y cargado
   pandas     2.2.x
   numpy      1.26.x
   sklearn    1.4.x
   pyarrow    15.x.x
   matplotlib 3.8.x
   seaborn    0.13.x
```

---

## 🔧 Gestión del entorno

| Acción | Comando |
|--------|---------|
| Activar | `conda activate data_science` |
| Desactivar | `conda deactivate` |
| Listar entornos | `conda env list` |
| Actualizar desde `environment.yml` | `conda env update -f environment.yml --prune` |
| Eliminar el entorno | `conda env remove -n data_science` |
| Exportar el entorno actual | `conda env export > environment.yml` |

---

## ➕ Agregar paquetes nuevos

**Con conda (preferido):**
```bash
conda install -n data_science nombre-paquete
```

**Con pip (si no está en conda):**
```bash
conda activate data_science
pip install nombre-paquete
```

Para hacer el cambio permanente, agrégalo al `environment.yml` y ejecuta:
```bash
conda env update -f environment.yml --prune
```

---

## 🗂️ Archivos incluidos

```
.
├── environment.yml   # Definición del entorno conda
├── verify.py         # Script de verificación de librerías
└── README.md         # Esta guía
```

---

## ❓ Solución de problemas

**El comando `conda activate` no funciona en Linux/Mac:**
```bash
source ~/anaconda3/etc/profile.d/conda.sh
conda activate data_science
```

**El entorno ya existe y quiero recrearlo:**
```bash
conda env remove -n data_science
conda env create -f environment.yml
```

**Quiero usar Mamba para instalaciones más rápidas:**
```bash
conda install -n base -c conda-forge mamba
mamba env create -f environment.yml
```
