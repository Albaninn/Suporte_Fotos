# 📸 PhotoFlow Organizer

> **Automação de fluxo de trabalho para fotógrafos de eventos.**
> Organização inteligente baseada em metadados EXIF, unificação de múltiplas fontes e renomeação sequencial.

![Badge Concluído](http://img.shields.io/static/v1?label=STATUS&message=EM%20DESENVOLVIMENTO&color=GREEN&style=for-the-badge)
![Badge Python](http://img.shields.io/static/v1?label=PYTHON&message=3.10+&color=blue&style=for-the-badge)

## 📌 O Problema
Fotógrafos que cobrem eventos dinâmicos (como campeonatos de Judô ou casamentos) frequentemente utilizam **múltiplos corpos de câmera** (ex: uma Nikon com teleobjetiva e uma Canon com grande angular).

Ao descarregar os cartões, a ordenação alfabética padrão do sistema operacional (`DSC_001.jpg`, `IMG_001.jpg`) quebra a cronologia do evento, misturando momentos distintos e dificultando a edição e a narrativa visual.

## 🚀 A Solução
O **PhotoFlow Organizer** é uma aplicação Desktop que ingere arquivos de múltiplas fontes, lê os metadados brutos (EXIF) para capturar o *timestamp* exato do clique e reorganiza todo o set de imagens em uma linha do tempo única e coerente.

### Funcionalidades Principais
* **Ingestão Multi-Origem:** Suporte para importação simultânea de múltiplos cartões de memória/pastas.
* **Smart Sorting (Ordenação Inteligente):** Utiliza a tag EXIF `DateTimeOriginal` para ordenar fotos independente do nome do arquivo ou da marca da câmera.
* **Renomeação em Lote:** Padroniza os arquivos (ex: `Evento_Judo_0001.jpg`) mantendo a ordem cronológica real.
* **Preservação de Dados:** Utiliza cópia segura (`shutil`) para manter metadados originais intactos.
* **Interface Moderna:** GUI desenvolvida com `CustomTkinter` com suporte a Dark Mode.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3
* **GUI:** CustomTkinter (Wrapper moderno para Tcl/Tk)
* **Manipulação de Imagem:** Pillow (PIL)
* **Sistema de Arquivos:** OS, Shutil, Pathlib
* **Build:** PyInstaller / Auto-Py-To-Exe

## ⚙️ Como executar o projeto

### Pré-requisitos
Certifique-se de ter o [Python 3.10+](https://www.python.org/) instalado.

### Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/Albaninn/Suporte_Fotos.git
   ```

2. Crie um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   python src/main.py
   ```

## 📂 Estrutura do Projeto
```text
PhotoFlow_Organizer/
├── src/
│   ├── backend.py       # Lógica de negócio (Leitura EXIF, Ordenação)
│   ├── interface.py     # Camada de Apresentação (GUI)
│   └── main.py          # Entry point
├── requirements.txt     # Dependências
└── README.md            # Documentação
```

## 🤝 Contribuição
Sugestões e pull requests são bem-vindos. Este projeto foi desenvolvido para resolver dores reais no fluxo de fotografia esportiva e social.

---
Desenvolvido por Luckas Serenato