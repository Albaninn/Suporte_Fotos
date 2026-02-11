# 📸 PhotoFlow Pro

> **Suíte de ingestão, organização e tratamento em lote para fotógrafos.**
> Unifica múltiplas câmeras, detecta fotos borradas via Visão Computacional e aplica branding inteligente.

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)

![Badge Python](https://img.shields.io/static/v1?label=PYTHON&message=3.10+&color=blue&style=for-the-badge)
![Badge CV](https://img.shields.io/static/v1?label=OPENCV&message=VISÃO%20COMPUTACIONAL&color=green&style=for-the-badge)
![Badge Status](https://img.shields.io/static/v1?label=STATUS&message=V1.0%20STABLE&color=success&style=for-the-badge)

## 📌 O Problema
No fluxo profissional de fotografia (eventos esportivos, casamentos), três dores são constantes:
1.  **Dessincronia:** Fotos de múltiplas câmeras (Nikon, Canon) ficam fora de ordem ao serem renomeadas.
2.  **Triagem Lenta:** Encontrar fotos tremidas/borradas em um lote de 2.000 imagens leva horas.
3.  **Exportação Manual:** Abrir o Lightroom apenas para colocar uma marca d'água simples e redimensionar para o cliente.

## 🚀 A Solução
O **PhotoFlow Pro** é uma aplicação Desktop que automatiza a ingestão. Ele lê os metadados brutos (EXIF) para ordenação cronológica perfeita, usa algoritmos matemáticos para detectar nitidez e aplica branding (logo) respeitando a orientação da foto.

### Funcionalidades Chave

#### 1. 🧠 Organização Inteligente (Backend Recursivo)
* **Varredura Profunda:** Detecta fotos em subpastas de cartões de memória automaticamente.
* **Cronologia Real:** Ordena arquivos baseados na tag EXIF `DateTimeOriginal`, ignorando nomes de arquivo arbitrários (`DSC_001`, `IMG_999`).

#### 2. 👁️ Detecção de Borrão (Computer Vision)
* Utiliza **OpenCV** e o operador **Laplaciano** para calcular a variância de bordas da imagem.
* Gera um relatório automático apontando quais arquivos estão abaixo do limiar de nitidez definido pelo usuário.

#### 3. 💧 Smart Watermark (Marca D'água Dinâmica)
* **Lógica de Proporção:** O logo ocupa sempre X% da largura da imagem, independente se a foto é **Retrato (Vertical)** ou **Paisagem (Horizontal)**.
* **Controle de Opacidade:** Slider de 0-100% para marcas d'água sutis.
* **Correção de Rotação:** Aplica a orientação EXIF antes do processamento para garantir que o logo fique no canto correto.

#### 4. 🛡️ Metadados e Persistência
* **Injeção IPTC:** Grava *Copyright* e *Artist Name* diretamente nos metadados do arquivo final.
* **Configurações Salvas:** O app lembra suas preferências (pastas, sensibilidade, textos) em um arquivo JSON local.

## 🛠️ Stack Tecnológico

* **Linguagem:** Python 3.10+
* **Interface (GUI):** CustomTkinter (Modern UI / Dark Mode)
* **Processamento de Imagem:** Pillow (PIL) + ImageOps
* **Visão Computacional:** OpenCV (`cv2`)
* **Metadados:** PieExif
* **Build:** Auto-Py-To-Exe (PyInstaller)

## ⚙️ Instalação e Execução

### Rodando o código fonte
1.  Clone o repositório:
    ```bash
    git clone https://github.com/Albaninn/Suporte_Fotos.git
    ```
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3.  Execute:
    ```bash
    python src/main.py
    ```

### Gerando o Executável (.exe)
Este projeto está configurado para ser compilado em um arquivo único portátil.
1.  Instale o construtor: `pip install auto-py-to-exe`
2.  Execute `auto-py-to-exe` e selecione o script `src/main.py`.
3.  Certifique-se de incluir o ícone `camera.ico` como recurso adicional.

### Caminho do Executável(.exe)
Suporte_Fotos\output\PhotoFlow.exe

## 📂 Estrutura do Projeto

```text
PhotoFlow_Pro/
├── output/
│   ├── PhotoFlow.exe 
├── src/
│   ├── backend.py       # Lógica (OpenCV, Pillow, EXIF Sorting)
│   ├── interface.py     # GUI (CustomTkinter, Tabs, Events)
│   └── main.py          # Entry Point
├── camera.ico           # Ícone do App
├── user_config.json     # (Gerado automaticamente)
├── requirements.txt     # Dependências
└── README.md            # Documentação
```

## 🤝 Contribuição
Sugestões e pull requests são bem-vindos. Este projeto foi desenvolvido para resolver dores reais no fluxo de fotografia esportiva e social.

---
Desenvolvido por Luckas Serenato