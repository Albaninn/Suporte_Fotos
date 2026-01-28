import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import json
from backend import PhotoManager

CONFIG_FILE = "user_config.json"

class PhotoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PhotoFlow Pro")
        self.geometry("900x680") # Aumentei um pouco altura
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.manager = PhotoManager()
        self.checkboxes_pastas = {} 
        self.pasta_destino = ""
        self.logo_path = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._criar_painel_esquerdo()
        self._criar_painel_direito()
        self._criar_painel_inferior()
        self._carregar_configuracoes()

    def _criar_painel_esquerdo(self):
        self.frame_left = ctk.CTkFrame(self)
        self.frame_left.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_left, text="1. Origem das Fotos", font=("Arial", 16, "bold")).pack(pady=10)
        self.btn_add_raiz = ctk.CTkButton(self.frame_left, text="📂 Selecionar Pasta Raiz", command=self.adicionar_hierarquia)
        self.btn_add_raiz.pack(pady=5)
        
        self.scroll_pastas = ctk.CTkScrollableFrame(self.frame_left, label_text="Pastas Selecionadas")
        self.scroll_pastas.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.btn_limpar = ctk.CTkButton(self.frame_left, text="Limpar Lista", fg_color="transparent", border_width=1, height=25, command=self.limpar_selecao)
        self.btn_limpar.pack(pady=10)

    def _criar_painel_direito(self):
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(self.frame_right, text="2. Configurações", font=("Arial", 16, "bold")).pack(pady=10)
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

        # --- ABA TRATAMENTO ---
        # Marca D'água
        ctk.CTkLabel(self.tab_tratamento, text="--- Marca D'água ---", font=("Arial", 12, "bold")).pack(pady=5)
        self.switch_watermark = ctk.CTkSwitch(self.tab_tratamento, text="Aplicar Logo", command=self._toggle_watermark_options)
        self.switch_watermark.pack(pady=5)

        self.frame_watermark_opts = ctk.CTkFrame(self.tab_tratamento, fg_color="transparent")
        self.btn_logo = ctk.CTkButton(self.frame_watermark_opts, text="Escolher PNG", fg_color="#444", command=self.selecionar_logo)
        self.btn_logo.pack(pady=2)
        self.lbl_logo_path = ctk.CTkLabel(self.frame_watermark_opts, text="...", font=("Arial", 10))
        self.lbl_logo_path.pack(pady=2)
        
        # Slider Opacidade (NOVO)
        self.lbl_opacity = ctk.CTkLabel(self.frame_watermark_opts, text="Opacidade: 100%")
        self.lbl_opacity.pack(pady=(5,0))
        self.slider_opacity = ctk.CTkSlider(self.frame_watermark_opts, from_=10, to=100, command=self._atualizar_label_opacity)
        self.slider_opacity.set(100)
        self.slider_opacity.pack(pady=2)

        self.chk_resize = ctk.CTkCheckBox(self.frame_watermark_opts, text="Redimensionar antes?")
        self.chk_resize.pack(pady=(10, 5))
        self.entry_resize = ctk.CTkEntry(self.frame_watermark_opts, placeholder_text="Largura Max (px)")
        self.entry_resize.pack(pady=2)

        ctk.CTkLabel(self.tab_tratamento, text=" ").pack() 

        # Blur
        ctk.CTkLabel(self.tab_tratamento, text="--- Análise de Nitidez ---", font=("Arial", 12, "bold")).pack(pady=5)
        self.switch_blur = ctk.CTkSwitch(self.tab_tratamento, text="Detectar Borrão")
        self.switch_blur.pack(pady=5)
        
        # Label Dinâmica para o Valor (NOVO)
        self.lbl_blur_valor = ctk.CTkLabel(self.tab_tratamento, text="Sensibilidade: 100")
        self.lbl_blur_valor.pack(pady=2)
        
        self.slider_blur = ctk.CTkSlider(self.tab_tratamento, from_=10, to=500, command=self._atualizar_label_blur)
        self.slider_blur.set(100)
        self.slider_blur.pack(pady=5)

        # --- ABA METADADOS ---
        self.switch_copyright = ctk.CTkSwitch(self.tab_meta, text="Gravar Copyright")
        self.switch_copyright.pack(pady=10)
        self.entry_artista = ctk.CTkEntry(self.tab_meta, placeholder_text="Nome do Fotógrafo")
        self.entry_artista.pack(pady=5, padx=10, fill="x")
        self.entry_copyright = ctk.CTkEntry(self.tab_meta, placeholder_text="Texto de Copyright")
        self.entry_copyright.pack(pady=5, padx=10, fill="x")

    def _criar_painel_inferior(self):
        self.frame_bottom = ctk.CTkFrame(self, height=100)
        self.frame_bottom.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.frame_bottom)
        self.progress_bar.pack(fill="x", padx=20, pady=(15, 5))
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(self.frame_bottom, text="Pronto.")
        self.lbl_status.pack(pady=5)

        self.btn_processar = ctk.CTkButton(self.frame_bottom, text="PROCESSAR", height=40, font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen", command=self.iniciar_thread)
        self.btn_processar.pack(pady=10, fill="x", padx=50)

    # --- EVENTOS DE INTERFACE ---
    def _atualizar_label_blur(self, value):
        self.lbl_blur_valor.configure(text=f"Sensibilidade: {int(value)}")
        
    def _atualizar_label_opacity(self, value):
        self.lbl_opacity.configure(text=f"Opacidade: {int(value)}%")

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
        def scan():
            self.lbl_status.configure(text="Escaneando...")
            subpastas = self.manager.escanear_hierarquia(pasta_raiz)
            self.after(0, lambda: self._popular_lista_pastas(subpastas, pasta_raiz))
            self.after(0, lambda: self.lbl_status.configure(text="Concluído."))
        threading.Thread(target=scan).start()

    def _popular_lista_pastas(self, subpastas, raiz):
        if not subpastas:
            messagebox.showinfo("Info", "Nenhuma foto encontrada.")
            return
        for pasta in subpastas:
            if pasta not in self.checkboxes_pastas:
                nome = pasta.replace(raiz, "...") if len(pasta) > 60 else pasta
                chk = ctk.CTkCheckBox(self.scroll_pastas, text=nome, onvalue=pasta, offvalue="")
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

    def _salvar_configuracoes(self):
        dados = {
            "artista": self.entry_artista.get(),
            "copyright_text": self.entry_copyright.get(),
            "blur_sensibilidade": self.slider_blur.get(),
            "watermark_opacity": self.slider_opacity.get(), # Salva opacidade
            "resize_width": self.entry_resize.get()
        }
        try:
            with open(CONFIG_FILE, "w") as f: json.dump(dados, f)
        except: pass

    def _carregar_configuracoes(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    dados = json.load(f)
                    self.entry_artista.insert(0, dados.get("artista", ""))
                    self.entry_copyright.insert(0, dados.get("copyright_text", ""))
                    
                    blur_val = dados.get("blur_sensibilidade", 100)
                    self.slider_blur.set(blur_val)
                    self.lbl_blur_valor.configure(text=f"Sensibilidade: {int(blur_val)}")
                    
                    opac_val = dados.get("watermark_opacity", 100)
                    self.slider_opacity.set(opac_val)
                    self.lbl_opacity.configure(text=f"Opacidade: {int(opac_val)}%")
                    
                    self.entry_resize.insert(0, dados.get("resize_width", "2048"))
            except: pass

    def atualizar_progresso(self, texto, porcentagem):
        self.lbl_status.configure(text=texto)
        self.progress_bar.set(porcentagem / 100)

    def iniciar_thread(self):
        pastas = [k for k, v in self.checkboxes_pastas.items() if v.get() == k]
        if not pastas or not self.pasta_destino or not self.entry_prefixo.get():
            messagebox.showwarning("Atenção", "Preencha os campos obrigatórios.")
            return

        config = {
            "watermark_ativo": bool(self.switch_watermark.get()),
            "watermark_path": self.logo_path,
            "watermark_opacity": self.slider_opacity.get(), # Manda para backend
            "resize_ativo": bool(self.chk_resize.get()),
            "resize_largura": self.entry_resize.get(),
            "blur_ativo": bool(self.switch_blur.get()),
            "blur_limiar": self.slider_blur.get(),
            "copyright_ativo": bool(self.switch_copyright.get()),
            "copyright_artista": self.entry_artista.get(),
            "copyright_texto": self.entry_copyright.get()
        }
        self._salvar_configuracoes()
        self.btn_processar.configure(state="disabled")
        threading.Thread(target=lambda: self.executar_backend(pastas, config)).start()

    def executar_backend(self, pastas, config):
        try:
            resultado = self.manager.processar_arquivos(pastas, self.pasta_destino, self.entry_prefixo.get(), config, self.atualizar_progresso)
            self.atualizar_progresso("Concluído!", 100)
            if resultado['status'] == 'sucesso':
                if resultado.get('borradas'):
                    self.after(0, lambda: self._mostrar_relatorio_borradas(resultado['borradas']))
                else:
                    messagebox.showinfo("Sucesso", resultado['msg'])
            else:
                messagebox.showerror("Erro", resultado['msg'])
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            self.btn_processar.configure(state="normal")

    def _mostrar_relatorio_borradas(self, lista):
        top = ctk.CTkToplevel(self)
        top.title("Relatório de Nitidez")
        top.geometry("400x500")
        ctk.CTkLabel(top, text=f"⚠️ {len(lista)} fotos suspeitas:", font=("Arial", 12, "bold"), text_color="orange").pack(pady=10)
        scroll = ctk.CTkScrollableFrame(top)
        scroll.pack(fill="both", expand=True, padx=10, pady=5)
        for nome, score in lista:
            ctk.CTkLabel(scroll, text=f"{nome} (Score: {score})").pack(anchor="w")
        ctk.CTkButton(top, text="Fechar", command=top.destroy).pack(pady=10)