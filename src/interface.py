import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import json
from backend import PhotoManager

# Nome do arquivo para salvar configurações (copyright, logo, etc)
CONFIG_FILE = "user_config.json"

class PhotoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("PhotoFlow Pro")
        self.geometry("900x650")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.manager = PhotoManager()
        self.checkboxes_pastas = {} 
        self.pasta_destino = ""
        self.logo_path = ""

        # Layout Principal (Grid 2 colunas)
        self.grid_columnconfigure(0, weight=1) # Esquerda (Pastas)
        self.grid_columnconfigure(1, weight=1) # Direita (Configurações)
        self.grid_rowconfigure(0, weight=1)

        self._criar_painel_esquerdo()
        self._criar_painel_direito()
        self._criar_painel_inferior()
        
        # Carrega configurações salvas (se existirem)
        self._carregar_configuracoes()

    def _criar_painel_esquerdo(self):
        self.frame_left = ctk.CTkFrame(self)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_left, text="1. Origem das Fotos", font=("Arial", 16, "bold")).pack(pady=10)

        self.btn_add_raiz = ctk.CTkButton(self.frame_left, text="📂 Selecionar Pasta Raiz", command=self.adicionar_hierarquia)
        self.btn_add_raiz.pack(pady=5)
        
        ctk.CTkLabel(self.frame_left, text="Subpastas encontradas:", text_color="gray", font=("Arial", 12)).pack(pady=(10,0))

        self.scroll_pastas = ctk.CTkScrollableFrame(self.frame_left, label_text="Pastas Selecionadas")
        self.scroll_pastas.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.btn_limpar = ctk.CTkButton(self.frame_left, text="Limpar Lista", fg_color="transparent", border_width=1, height=25, command=self.limpar_selecao)
        self.btn_limpar.pack(pady=10)

    def _criar_painel_direito(self):
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_right, text="2. Configurações de Processamento", font=("Arial", 16, "bold")).pack(pady=10)

        # Usando ABAS para organizar as opções avançadas
        self.tabview = ctk.CTkTabview(self.frame_right)
        self.tabview.pack(padx=10, pady=5, fill="both", expand=True)

        self.tab_geral = self.tabview.add("Geral")
        self.tab_tratamento = self.tabview.add("Tratamento")
        self.tab_meta = self.tabview.add("Metadados")

        # --- ABA GERAL ---
        self.btn_destino = ctk.CTkButton(self.tab_geral, text="Selecionar Destino", command=self.selecionar_destino)
        self.btn_destino.pack(pady=15)
        self.lbl_destino_path = ctk.CTkLabel(self.tab_geral, text="Nenhum destino selecionado", text_color="gray", wraplength=300)
        self.lbl_destino_path.pack(pady=5)

        ctk.CTkLabel(self.tab_geral, text="Prefixo do Arquivo:").pack(pady=(20, 5))
        self.entry_prefixo = ctk.CTkEntry(self.tab_geral, placeholder_text="Ex: Judo_Finals")
        self.entry_prefixo.pack(pady=5, fill="x", padx=20)

        # --- ABA TRATAMENTO (Watermark & Blur) ---
        
        # Seção Marca D'água
        ctk.CTkLabel(self.tab_tratamento, text="--- Marca D'água ---", font=("Arial", 12, "bold")).pack(pady=5)
        self.switch_watermark = ctk.CTkSwitch(self.tab_tratamento, text="Aplicar Logo", command=self._toggle_watermark_options)
        self.switch_watermark.pack(pady=5)

        self.frame_watermark_opts = ctk.CTkFrame(self.tab_tratamento, fg_color="transparent")
        self.btn_logo = ctk.CTkButton(self.frame_watermark_opts, text="Escolher PNG do Logo", fg_color="#444", command=self.selecionar_logo)
        self.btn_logo.pack(pady=2)
        self.lbl_logo_path = ctk.CTkLabel(self.frame_watermark_opts, text="...", font=("Arial", 10))
        self.lbl_logo_path.pack(pady=2)
        
        self.chk_resize = ctk.CTkCheckBox(self.frame_watermark_opts, text="Redimensionar antes?")
        self.chk_resize.pack(pady=5)
        self.entry_resize = ctk.CTkEntry(self.frame_watermark_opts, placeholder_text="Largura Max (px). Ex: 2048")
        self.entry_resize.pack(pady=2)
        # (O frame só é packeado se o switch estiver on)

        ctk.CTkLabel(self.tab_tratamento, text=" ").pack() # Espaçador

        # Seção Blur
        ctk.CTkLabel(self.tab_tratamento, text="--- Análise de Nitidez ---", font=("Arial", 12, "bold")).pack(pady=5)
        self.switch_blur = ctk.CTkSwitch(self.tab_tratamento, text="Detectar Borrão")
        self.switch_blur.pack(pady=5)
        
        ctk.CTkLabel(self.tab_tratamento, text="Sensibilidade (Menor = Mais Rigoroso)").pack(pady=2)
        self.slider_blur = ctk.CTkSlider(self.tab_tratamento, from_=10, to=500, number_of_steps=50)
        self.slider_blur.set(100) # Padrão
        self.slider_blur.pack(pady=5)

        # --- ABA METADADOS ---
        self.switch_copyright = ctk.CTkSwitch(self.tab_meta, text="Gravar Copyright (IPTC)")
        self.switch_copyright.pack(pady=10)
        
        self.entry_artista = ctk.CTkEntry(self.tab_meta, placeholder_text="Nome do Fotógrafo")
        self.entry_artista.pack(pady=5, padx=10, fill="x")
        
        self.entry_copyright = ctk.CTkEntry(self.tab_meta, placeholder_text="Texto de Copyright (ex: Todos os direitos reservados)")
        self.entry_copyright.pack(pady=5, padx=10, fill="x")

    def _criar_painel_inferior(self):
        self.frame_bottom = ctk.CTkFrame(self, height=100)
        self.frame_bottom.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.frame_bottom)
        self.progress_bar.pack(fill="x", padx=20, pady=(15, 5))
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(self.frame_bottom, text="Pronto para iniciar.")
        self.lbl_status.pack(pady=5)

        self.btn_processar = ctk.CTkButton(self.frame_bottom, text="PROCESSAR FOTOS", height=40, font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen", command=self.iniciar_thread)
        self.btn_processar.pack(pady=10, fill="x", padx=50)

    # --- LÓGICA DE UI ---

    def _toggle_watermark_options(self):
        if self.switch_watermark.get() == 1:
            self.frame_watermark_opts.pack(pady=5, padx=10, fill="x")
        else:
            self.frame_watermark_opts.pack_forget()

    def selecionar_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Imagens PNG", "*.png")])
        if path:
            self.logo_path = path
            self.lbl_logo_path.configure(text=os.path.basename(path))

    def adicionar_hierarquia(self):
        pasta_raiz = filedialog.askdirectory()
        if not pasta_raiz: return
        
        # Thread para não travar a UI enquanto escaneia
        def scan():
            self.lbl_status.configure(text="Escaneando pastas...")
            subpastas = self.manager.escanear_hierarquia(pasta_raiz)
            
            # Atualiza UI na thread principal
            self.after(0, lambda: self._popular_lista_pastas(subpastas, pasta_raiz))
            self.after(0, lambda: self.lbl_status.configure(text="Escaneamento concluído."))

        threading.Thread(target=scan).start()

    def _popular_lista_pastas(self, subpastas, raiz):
        if not subpastas:
            messagebox.showinfo("Info", "Nenhuma foto encontrada.")
            return
        
        for pasta in subpastas:
            if pasta not in self.checkboxes_pastas:
                nome_exibicao = pasta.replace(raiz, "...") if len(pasta) > 60 else pasta
                chk = ctk.CTkCheckBox(self.scroll_pastas, text=nome_exibicao, onvalue=pasta, offvalue="")
                chk.select()
                chk.pack(anchor="w", pady=2, padx=5)
                self.checkboxes_pastas[pasta] = chk

    def limpar_selecao(self):
        for chk in self.checkboxes_pastas.values(): chk.destroy()
        self.checkboxes_pastas = {}

    def selecionar_destino(self):
        p = filedialog.askdirectory()
        if p:
            self.pasta_destino = p
            self.lbl_destino_path.configure(text=p)

    # --- PERSISTÊNCIA (Salvar/Carregar Configs) ---
    def _salvar_configuracoes(self):
        dados = {
            "artista": self.entry_artista.get(),
            "copyright_text": self.entry_copyright.get(),
            "blur_sensibilidade": self.slider_blur.get(),
            "resize_width": self.entry_resize.get()
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(dados, f)
        except: pass

    def _carregar_configuracoes(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    dados = json.load(f)
                    self.entry_artista.insert(0, dados.get("artista", ""))
                    self.entry_copyright.insert(0, dados.get("copyright_text", ""))
                    self.slider_blur.set(dados.get("blur_sensibilidade", 100))
                    self.entry_resize.insert(0, dados.get("resize_width", "2048"))
            except: pass

    # --- PROCESSAMENTO ---

    def atualizar_progresso(self, texto, porcentagem):
        self.lbl_status.configure(text=texto)
        self.progress_bar.set(porcentagem / 100)

    def iniciar_thread(self):
        pastas = [k for k, v in self.checkboxes_pastas.items() if v.get() == k]
        
        if not pastas or not self.pasta_destino or not self.entry_prefixo.get():
            messagebox.showwarning("Atenção", "Verifique Pastas de Origem, Destino e Prefixo.")
            return

        # Monta o objeto de configuração para o Backend
        config = {
            "watermark_ativo": bool(self.switch_watermark.get()),
            "watermark_path": self.logo_path,
            "resize_ativo": bool(self.chk_resize.get()),
            "resize_largura": self.entry_resize.get(),
            
            "blur_ativo": bool(self.switch_blur.get()),
            "blur_limiar": self.slider_blur.get(),
            
            "copyright_ativo": bool(self.switch_copyright.get()),
            "copyright_artista": self.entry_artista.get(),
            "copyright_texto": self.entry_copyright.get()
        }

        # Salva para a próxima vez
        self._salvar_configuracoes()

        self.btn_processar.configure(state="disabled")
        threading.Thread(target=lambda: self.executar_backend(pastas, config)).start()

    def executar_backend(self, pastas, config):
        try:
            resultado = self.manager.processar_arquivos(
                pastas, 
                self.pasta_destino, 
                self.entry_prefixo.get(), 
                config,
                self.atualizar_progresso
            )
            
            self.atualizar_progresso("Concluído!", 100)
            
            # Lógica de Relatório Final
            if resultado['status'] == 'sucesso':
                msg = resultado['msg']
                borradas = resultado.get('borradas', [])
                
                if borradas:
                    self.after(0, lambda: self._mostrar_relatorio_borradas(borradas))
                else:
                    messagebox.showinfo("Sucesso", msg)
            else:
                messagebox.showerror("Erro", resultado['msg'])

        except Exception as e:
            messagebox.showerror("Erro Crítico", str(e))
        finally:
            self.btn_processar.configure(state="normal")

    def _mostrar_relatorio_borradas(self, lista_borradas):
        # Janela Pop-up customizada
        top = ctk.CTkToplevel(self)
        top.title("Relatório de Nitidez")
        top.geometry("400x500")
        
        ctk.CTkLabel(top, text=f"⚠️ {len(lista_borradas)} fotos detectadas como borradas/tremidas:", font=("Arial", 12, "bold"), text_color="orange").pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(top)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        
        for nome, score in lista_borradas:
            # Score menor = mais borrado
            ctk.CTkLabel(scroll, text=f"{nome} (Score: {score})").pack(anchor="w")
            
        ctk.CTkButton(top, text="Fechar", command=top.destroy).pack(pady=10)