import os
import shutil
import cv2  # OpenCV para detecção de borrão
import piexif # Para editar metadados
from datetime import datetime
from PIL import Image, ImageEnhance

class PhotoManager:
    def __init__(self):
        self.extensoes_validas = ('.jpg', '.jpeg', '.png', '.cr2', '.nef', '.arw')

    def escanear_hierarquia(self, pasta_raiz):
        """Busca recursiva de pastas com fotos."""
        pastas_com_fotos = []
        for root, dirs, files in os.walk(pasta_raiz):
            tem_foto = any(arquivo.lower().endswith(self.extensoes_validas) for arquivo in files)
            if tem_foto:
                pastas_com_fotos.append(root)
        return pastas_com_fotos

    def _obter_data_exif(self, caminho_arquivo):
        """Tenta extrair Data Original ou usa Data de Modificação."""
        try:
            image = Image.open(caminho_arquivo)
            exif_data = image._getexif()
            if exif_data:
                data_str = exif_data.get(36867) # DateTimeOriginal
                if data_str:
                    return datetime.strptime(data_str, '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass
        return datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))

    def _detectar_borrao(self, caminho_imagem, limiar):
        """
        Retorna (True, valor_variancia) se estiver borrada, ou (False, valor_variancia).
        Quanto MENOR a variância, mais borrada.
        """
        try:
            # Lê em escala de cinza para performance
            imagem = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
            if imagem is None: 
                return False, 0
            
            # Calcula a variância do Laplaciano
            variancia = cv2.Laplacian(imagem, cv2.CV_64F).var()
            
            return variancia < limiar, variancia
        except Exception as e:
            print(f"Erro ao analisar borrão em {caminho_imagem}: {e}")
            return False, 0

    def _aplicar_processamento_visual(self, img_pil, config):
        """Aplica Resize e Marca d'água na imagem carregada."""
        
        # 1. Redimensionamento
        if config.get('resize_ativo') and config.get('resize_largura'):
            largura_max = int(config['resize_largura'])
            w, h = img_pil.size
            if w > largura_max:
                ratio = largura_max / float(w)
                nova_altura = int(h * ratio)
                # LANCZOS é o melhor filtro para redução de qualidade
                img_pil = img_pil.resize((largura_max, nova_altura), Image.Resampling.LANCZOS)

        # 2. Marca D'água
        if config.get('watermark_ativo') and config.get('watermark_path'):
            path_logo = config['watermark_path']
            if os.path.exists(path_logo):
                logo = Image.open(path_logo).convert("RGBA")
                
                # Redimensiona o logo proporcionalmente (ex: 15% da largura da foto)
                w_img, h_img = img_pil.size
                fator_escala = 0.15 
                w_logo_novo = int(w_img * fator_escala)
                ratio_logo = w_logo_novo / float(logo.size[0])
                h_logo_novo = int(logo.size[1] * ratio_logo)
                
                logo = logo.resize((w_logo_novo, h_logo_novo), Image.Resampling.LANCZOS)
                
                # Cria uma tela transparente do tamanho da foto
                layer_transparente = Image.new('RGBA', img_pil.size, (0,0,0,0))
                
                # Define posição (Padrão: Canto Inferior Direito com margem)
                margem = int(w_img * 0.02)
                posicao_x = w_img - w_logo_novo - margem
                posicao_y = h_img - h_logo_novo - margem
                
                layer_transparente.paste(logo, (posicao_x, posicao_y))
                
                # Converte a imagem original para RGBA para compor
                img_pil = img_pil.convert("RGBA")
                img_pil = Image.alpha_composite(img_pil, layer_transparente)
                
                # Volta para RGB para salvar em JPG
                img_pil = img_pil.convert("RGB")

        return img_pil

    def _injetar_metadados(self, caminho_arquivo, artista, copyright_text):
        """Insere tags IPTC/EXIF de autoria."""
        try:
            exif_dict = piexif.load(caminho_arquivo)
            
            # 0x013B é 'Artist', 0x8298 é 'Copyright'
            exif_dict["0th"][piexif.ImageIFD.Artist] = artista.encode('utf-8')
            exif_dict["0th"][piexif.ImageIFD.Copyright] = copyright_text.encode('utf-8')
            
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, caminho_arquivo)
        except Exception as e:
            print(f"Aviso: Não foi possível injetar metadados em {caminho_arquivo}: {e}")

    def processar_arquivos(self, lista_pastas, pasta_destino, prefixo, config, callback_progresso=None):
        """
        Main Pipeline.
        config: Dicionário com todas as flags (blur, watermark, copyright, etc)
        """
        arquivos_encontrados = []
        relatorio_borradas = [] # Lista de tuplas (nome_arquivo, score)

        # --- ETAPA 1: COLETA ---
        print("--- Iniciando Coleta ---")
        for pasta in lista_pastas:
            if not os.path.exists(pasta): continue
            for nome in os.listdir(pasta):
                if nome.lower().endswith(self.extensoes_validas):
                    arquivos_encontrados.append(os.path.join(pasta, nome))

        total = len(arquivos_encontrados)
        if total == 0: return {"status": "erro", "msg": "Nenhum arquivo encontrado."}

        # --- ETAPA 2: ORDENAÇÃO ---
        lista_ordenada = []
        for idx, caminho in enumerate(arquivos_encontrados):
            data = self._obter_data_exif(caminho)
            lista_ordenada.append((data, caminho))
            if callback_progresso:
                callback_progresso("Lendo metadados...", (idx / total) * 30)

        lista_ordenada.sort(key=lambda x: x[0])

        # --- ETAPA 3: PROCESSAMENTO ---
        if not os.path.exists(pasta_destino): os.makedirs(pasta_destino)
        padding = len(str(total))

        for i, (data, caminho_origem) in enumerate(lista_ordenada):
            nome_arquivo_original = os.path.basename(caminho_origem)
            extensao = os.path.splitext(caminho_origem)[1].lower()
            
            # Novo nome
            contador = str(i + 1).zfill(padding)
            novo_nome = f"{prefixo}_{contador}{extensao}"
            caminho_final = os.path.join(pasta_destino, novo_nome)

            # A. Detecção de Borrão (Opcional)
            if config.get('blur_ativo'):
                e_borrada, score = self._detectar_borrao(caminho_origem, config.get('blur_limiar', 100))
                if e_borrada:
                    relatorio_borradas.append((novo_nome, int(score)))

            # B. Manipulação de Imagem (Resize / Watermark)
            processamento_pesado = config.get('resize_ativo') or config.get('watermark_ativo')
            
            try:
                if processamento_pesado and extensao in ['.jpg', '.jpeg', '.png']:
                    # Abre, Edita, Salva
                    with Image.open(caminho_origem) as img:
                        img_processada = self._aplicar_processamento_visual(img, config)
                        # Salva com qualidade alta
                        img_processada.save(caminho_final, quality=95, exif=img.info.get('exif'))
                else:
                    # Cópia Direta (Mais rápido e preserva tudo se for RAW)
                    shutil.copy2(caminho_origem, caminho_final)
                
                # C. Injeção de Copyright (Opcional)
                if config.get('copyright_ativo') and extensao in ['.jpg', '.jpeg']:
                    self._injetar_metadados(
                        caminho_final, 
                        config.get('copyright_artista', ''), 
                        config.get('copyright_texto', '')
                    )

            except Exception as e:
                print(f"Erro ao processar {nome_arquivo_original}: {e}")

            if callback_progresso:
                progresso = 30 + ((i + 1) / total) * 70
                callback_progresso(f"Processando {novo_nome}...", progresso)

        return {
            "status": "sucesso", 
            "msg": f"Processados {total} arquivos.",
            "total": total,
            "borradas": relatorio_borradas
        }