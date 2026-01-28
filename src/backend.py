import os
import shutil
import cv2
import piexif
from datetime import datetime
from PIL import Image, ImageEnhance, ImageOps # <--- Adicionado ImageOps

class PhotoManager:
    def __init__(self):
        self.extensoes_validas = ('.jpg', '.jpeg', '.png', '.cr2', '.nef', '.arw')

    def escanear_hierarquia(self, pasta_raiz):
        pastas_com_fotos = []
        for root, dirs, files in os.walk(pasta_raiz):
            tem_foto = any(arquivo.lower().endswith(self.extensoes_validas) for arquivo in files)
            if tem_foto:
                pastas_com_fotos.append(root)
        return pastas_com_fotos

    def _obter_data_exif(self, caminho_arquivo):
        try:
            image = Image.open(caminho_arquivo)
            exif_data = image._getexif()
            if exif_data:
                data_str = exif_data.get(36867)
                if data_str:
                    return datetime.strptime(data_str, '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass
        return datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))

    def _detectar_borrao(self, caminho_imagem, limiar):
        try:
            imagem = cv2.imread(caminho_imagem, cv2.IMREAD_GRAYSCALE)
            if imagem is None: return False, 0
            variancia = cv2.Laplacian(imagem, cv2.CV_64F).var()
            return variancia < limiar, variancia
        except Exception as e:
            print(f"Erro borrão: {e}")
            return False, 0

    def _aplicar_processamento_visual(self, img_pil, config):
        # --- CORREÇÃO CRÍTICA DE ROTAÇÃO ---
        # Aplica a rotação do EXIF fisicamente na imagem antes de editar.
        # Isso garante que fotos verticais fiquem realmente verticais na memória.
        img_pil = ImageOps.exif_transpose(img_pil) 
        # -----------------------------------

        # 1. Redimensionamento
        if config.get('resize_ativo') and config.get('resize_largura'):
            largura_max = int(config['resize_largura'])
            w, h = img_pil.size
            
            if w > largura_max or h > largura_max:
                if w > h: # Paisagem
                    ratio = largura_max / float(w)
                    nova_h = int(h * ratio)
                    novo_w = largura_max
                else: # Retrato
                    # Mantém a proporção correta baseada na largura ou altura?
                    # Para "fit", limitamos o maior lado.
                    # Mas se quiser largura fixa, usa a lógica abaixo.
                    # Vamos limitar pelo MAIOR lado para garantir consistência.
                    if h > largura_max:
                        ratio = largura_max / float(h)
                        novo_w = int(w * ratio)
                        nova_h = largura_max
                    else:
                        novo_w = w
                        nova_h = h
                    
                img_pil = img_pil.resize((novo_w, nova_h), Image.Resampling.LANCZOS)

        # 2. Marca D'água
        if config.get('watermark_ativo') and config.get('watermark_path'):
            path_logo = config['watermark_path']
            if os.path.exists(path_logo):
                logo = Image.open(path_logo).convert("RGBA")
                w_img, h_img = img_pil.size

                # Lógica: Logo ocupa 20% da LARGURA da foto (seja retrato ou paisagem)
                porcentagem_largura = 0.20 
                w_logo_novo = int(w_img * porcentagem_largura)
                
                ratio_logo = logo.size[1] / logo.size[0]
                h_logo_novo = int(w_logo_novo * ratio_logo)
                
                logo = logo.resize((w_logo_novo, h_logo_novo), Image.Resampling.LANCZOS)
                
                # Opacidade
                opacity_level = config.get('watermark_opacity', 100) / 100.0
                if opacity_level < 1.0:
                    r, g, b, a = logo.split()
                    a = a.point(lambda p: p * opacity_level)
                    logo = Image.merge('RGBA', (r, g, b, a))

                # Margem: 3% do menor lado
                margem = int(min(w_img, h_img) * 0.03)
                
                posicao_x = w_img - w_logo_novo - margem
                posicao_y = h_img - h_logo_novo - margem
                
                layer_transparente = Image.new('RGBA', img_pil.size, (0,0,0,0))
                layer_transparente.paste(logo, (posicao_x, posicao_y))
                
                img_pil = img_pil.convert("RGBA")
                img_pil = Image.alpha_composite(img_pil, layer_transparente)
                img_pil = img_pil.convert("RGB")

        return img_pil

    def _injetar_metadados(self, caminho_arquivo, artista, copyright_text):
        try:
            exif_dict = piexif.load(caminho_arquivo)
            exif_dict["0th"][piexif.ImageIFD.Artist] = artista.encode('utf-8')
            exif_dict["0th"][piexif.ImageIFD.Copyright] = copyright_text.encode('utf-8')
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, caminho_arquivo)
        except Exception: pass

    def processar_arquivos(self, lista_pastas, pasta_destino, prefixo, config, callback_progresso=None):
        arquivos_encontrados = []
        relatorio_borradas = [] 

        print("--- Coletando ---")
        for pasta in lista_pastas:
            if not os.path.exists(pasta): continue
            for nome in os.listdir(pasta):
                if nome.lower().endswith(self.extensoes_validas):
                    arquivos_encontrados.append(os.path.join(pasta, nome))

        total = len(arquivos_encontrados)
        if total == 0: return {"status": "erro", "msg": "Nenhum arquivo encontrado."}

        # Ordenação
        lista_ordenada = []
        for idx, caminho in enumerate(arquivos_encontrados):
            data = self._obter_data_exif(caminho)
            lista_ordenada.append((data, caminho))
            if callback_progresso:
                callback_progresso("Lendo EXIF...", (idx / total) * 30)
        lista_ordenada.sort(key=lambda x: x[0])

        # Processamento
        if not os.path.exists(pasta_destino): os.makedirs(pasta_destino)
        padding = len(str(total))

        for i, (data, caminho_origem) in enumerate(lista_ordenada):
            nome_original = os.path.basename(caminho_origem)
            extensao = os.path.splitext(caminho_origem)[1].lower()
            contador = str(i + 1).zfill(padding)
            novo_nome = f"{prefixo}_{contador}{extensao}"
            caminho_final = os.path.join(pasta_destino, novo_nome)

            if config.get('blur_ativo'):
                e_borrada, score = self._detectar_borrao(caminho_origem, config.get('blur_limiar', 100))
                if e_borrada:
                    relatorio_borradas.append((novo_nome, int(score)))

            processamento_pesado = config.get('resize_ativo') or config.get('watermark_ativo')
            
            try:
                if processamento_pesado and extensao in ['.jpg', '.jpeg', '.png']:
                    with Image.open(caminho_origem) as img:
                        # O processamento agora lida com a rotação internamente
                        img_processada = self._aplicar_processamento_visual(img, config)
                        
                        # Salvamos SEM o EXIF antigo de orientação, pois já aplicamos a rotação nos pixels
                        # Mas podemos querer manter outros metadados.
                        # O ideal é salvar limpo ou copiar EXIF seletivamente, 
                        # mas para web/entrega, salvar limpo evita muita dor de cabeça.
                        img_processada.save(caminho_final, quality=95)
                else:
                    shutil.copy2(caminho_origem, caminho_final)
                
                if config.get('copyright_ativo') and extensao in ['.jpg', '.jpeg']:
                    self._injetar_metadados(caminho_final, config.get('copyright_artista', ''), config.get('copyright_texto', ''))

            except Exception as e:
                print(f"Erro em {nome_original}: {e}")

            if callback_progresso:
                progresso = 30 + ((i + 1) / total) * 70
                callback_progresso(f"Processando {novo_nome}...", progresso)

        return {
            "status": "sucesso", 
            "msg": f"Processados {total} arquivos.",
            "borradas": relatorio_borradas
        }