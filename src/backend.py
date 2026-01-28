import os
import shutil
from datetime import datetime
from PIL import Image

class PhotoManager:
    def __init__(self):
        # Extensões que aceitamos
        self.extensoes_validas = ('.jpg', '.jpeg', '.png', '.cr2', '.nef', '.arw')

    def escanear_hierarquia(self, pasta_raiz):
        """
        Percorre a pasta raiz e todas as subpastas.
        Retorna uma lista de caminhos de pastas que contêm pelo menos uma foto válida.
        """
        pastas_com_fotos = []
        
        # os.walk desce recursivamente em toda a árvore de diretórios
        for root, dirs, files in os.walk(pasta_raiz):
            # Verifica se tem alguma foto nesta pasta específica
            tem_foto = any(arquivo.lower().endswith(self.extensoes_validas) for arquivo in files)
            
            if tem_foto:
                pastas_com_fotos.append(root)
                
        return pastas_com_fotos

    def _obter_data_exif(self, caminho_arquivo):
        try:
            image = Image.open(caminho_arquivo)
            exif_data = image._getexif()
            if exif_data:
                data_str = exif_data.get(36867) # Tag DateTimeOriginal
                if data_str:
                    return datetime.strptime(data_str, '%Y:%m:%d %H:%M:%S')
        except Exception:
            pass
        # Fallback: data de modificação do arquivo
        return datetime.fromtimestamp(os.path.getmtime(caminho_arquivo))

    def processar_arquivos(self, lista_pastas_selecionadas, pasta_destino, prefixo, callback_progresso=None):
        arquivos_encontrados = []

        # ETAPA 1: Coleta apenas das pastas que o usuário deixou marcadas
        print("--- Iniciando Coleta ---")
        for pasta in lista_pastas_selecionadas:
            if not os.path.exists(pasta):
                continue
            
            # Pega os arquivos dessa pasta
            for nome_arquivo in os.listdir(pasta):
                if nome_arquivo.lower().endswith(self.extensoes_validas):
                    caminho_completo = os.path.join(pasta, nome_arquivo)
                    arquivos_encontrados.append(caminho_completo)

        total_arquivos = len(arquivos_encontrados)
        if total_arquivos == 0:
            return "Nenhum arquivo encontrado nas pastas selecionadas."

        # ETAPA 2: Ordenação Inteligente
        print(f"--- Ordenando {total_arquivos} fotos ---")
        lista_com_datas = []
        
        for idx, caminho in enumerate(arquivos_encontrados):
            data = self._obter_data_exif(caminho)
            lista_com_datas.append((data, caminho))
            
            if callback_progresso:
                # Primeiros 40% da barra é leitura
                callback_progresso("Lendo metadados...", (idx / total_arquivos) * 40)

        lista_com_datas.sort(key=lambda x: x[0])

        # ETAPA 3: Cópia
        if not os.path.exists(pasta_destino):
            os.makedirs(pasta_destino)

        padding = len(str(total_arquivos))

        for i, (data, caminho_origem) in enumerate(lista_com_datas):
            extensao = os.path.splitext(caminho_origem)[1]
            contador = str(i + 1).zfill(padding)
            novo_nome = f"{prefixo}_{contador}{extensao}"
            caminho_final = os.path.join(pasta_destino, novo_nome)

            try:
                shutil.copy2(caminho_origem, caminho_final)
            except Exception as e:
                print(f"Erro: {e}")

            if callback_progresso:
                # Do 40% ao 100% é cópia
                progresso_atual = 40 + ((i + 1) / total_arquivos) * 60
                callback_progresso(f"Copiando {novo_nome}...", progresso_atual)

        return f"Sucesso! {total_arquivos} fotos processadas."