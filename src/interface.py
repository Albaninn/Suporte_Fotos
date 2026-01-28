import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from backend import PhotoManager

class PhotoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("PhotoFlow Organizer")
        self.geometry("700x600") # Aumentei um pouco
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.manager = PhotoManager()
        self.pasta_destino = ""
        
        # Dicionário para guardar os checkboxes: {caminho_pasta: objeto_checkbox}
        self.checkboxes_pastas = {} 

        self._criar_elementos()

    def _criar_elementos(self):
        # --- SEÇÃO 1: Seleção Inteligente de Pastas ---
        self.frame_topo = ctk.CTkFrame(self)
        self.frame_topo.pack(pady=10, padx=20, fill="x")

        self.lbl_titulo = ctk.CTkLabel(self.frame_topo, text="Origem das Fotos (Hierarquia)", font=("Arial", 14, "bold"))
        self.lbl_titulo.pack(pady=5)

        self.btn_add_raiz = ctk.CTkButton(self.frame_topo, text="📂 Selecionar Pasta Raiz (Cartão/HD)", command=self.adicionar_hierarquia)
        self.btn_add_raiz.pack(pady=5)
        
        self.lbl_instrucao = ctk.CTkLabel(self.frame_topo, text="Desmarque as subpastas que não deseja incluir:", font=("Arial", 11), text_color="gray")
        self.lbl_instrucao.pack(pady=(5,0))

        # Área de Scroll com Checkboxes
        self.scroll_pastas = ctk.CTkScrollableFrame(self, label_text="Pastas Detectadas", height=200)
        self.scroll_pastas.pack(pady=5, padx=20, fill="x")
        
        self.btn_limpar = ctk.CTkButton(self, text="Limpar Seleção", fg_color="transparent", border_width=1, height=25, command=self.limpar_selecao)
        self.btn_limpar.pack(pady=(0, 10))

        # --- SEÇÃO 2: Configuração e Ação ---
        self.frame_bottom = ctk.CTkFrame(self)
        self.frame_bottom.pack(pady=10, padx=20, fill="both", expand=True)

        # Destino
        self.btn_destino = ctk.CTkButton(self.frame_bottom, text="Selecionar Destino", command=self.selecionar_destino)
        self.btn_destino.grid(row=0, column=0, padx=10, pady=15)
        
        self.lbl_destino_path = ctk.CTkLabel(self.frame_bottom, text="Nenhum destino selecionado", text_color="gray", anchor="w")
        self.lbl_destino_path.grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        # Prefixo
        self.entry_prefixo = ctk.CTkEntry(self.frame_bottom, placeholder_text="Prefixo (ex: Evento_Judo)")
        self.entry_prefixo.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Progresso
        self.progress_bar = ctk.CTkProgressBar(self.frame_bottom)
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="ew")
        self.progress_bar.set(0)

        self.lbl_status = ctk.CTkLabel(self.frame_bottom, text="Aguardando...")
        self.lbl_status.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.btn_processar = ctk.CTkButton(self.frame_bottom, text="PROCESSAR FOTOS", height=50, font=("Arial", 16, "bold"), fg_color="green", hover_color="darkgreen", command=self.iniciar_thread)
        self.btn_processar.grid(row=4, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
        
        self.frame_bottom.grid_columnconfigure(1, weight=1)

    # --- Lógica ---

    def adicionar_hierarquia(self):
        pasta_raiz = filedialog.askdirectory()
        if not pasta_raiz:
            return

        # Busca recursiva no backend
        subpastas_encontradas = self.manager.escanear_hierarquia(pasta_raiz)
        
        if not subpastas_encontradas:
            messagebox.showinfo("Info", "Nenhuma foto encontrada nessa pasta ou subpastas.")
            return

        # Para cada pasta encontrada, cria um Checkbox
        for pasta in subpastas_encontradas:
            if pasta not in self.checkboxes_pastas:
                # Tenta mostrar um nome mais curto para facilitar a leitura
                nome_exibicao = pasta.replace(pasta_raiz, "...") if len(pasta) > 50 else pasta
                
                chk = ctk.CTkCheckBox(self.scroll_pastas, text=nome_exibicao, onvalue=pasta, offvalue="")
                chk.select() # Já vem marcado por padrão
                chk.pack(anchor="w", pady=2, padx=5)
                
                # Guarda a referência para podermos ler depois
                self.checkboxes_pastas[pasta] = chk

    def limpar_selecao(self):
        for chk in self.checkboxes_pastas.values():
            chk.destroy()
        self.checkboxes_pastas = {}

    def selecionar_destino(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.pasta_destino = pasta
            self.lbl_destino_path.configure(text=pasta, text_color="white")

    def atualizar_progresso(self, texto, porcentagem):
        self.lbl_status.configure(text=texto)
        self.progress_bar.set(porcentagem / 100)

    def iniciar_thread(self):
        # 1. Recuperar quais pastas estão marcadas (Checked)
        pastas_para_processar = []
        for caminho_original, checkbox in self.checkboxes_pastas.items():
            if checkbox.get() == caminho_original: # Se estiver marcado, o valor é o caminho
                pastas_para_processar.append(caminho_original)

        # Validações
        if not pastas_para_processar:
            messagebox.showwarning("Atenção", "Nenhuma pasta selecionada/marcada para processamento.")
            return
        if not self.pasta_destino:
            messagebox.showwarning("Atenção", "Selecione a pasta de destino.")
            return
        if not self.entry_prefixo.get():
            messagebox.showwarning("Atenção", "Digite o prefixo.")
            return

        self.btn_processar.configure(state="disabled", text="Processando...")
        threading.Thread(target=lambda: self.executar_backend(pastas_para_processar)).start()

    def executar_backend(self, pastas):
        try:
            resultado = self.manager.processar_arquivos(
                pastas, 
                self.pasta_destino, 
                self.entry_prefixo.get(), 
                self.atualizar_progresso
            )
            self.atualizar_progresso(resultado, 100)
            messagebox.showinfo("Concluído", resultado)
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            self.btn_processar.configure(state="normal", text="PROCESSAR FOTOS")