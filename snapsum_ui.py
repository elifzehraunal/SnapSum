import customtkinter as ctk
import fitz  # PyMuPDF
from tkinter import filedialog

# --- TASARIM KİMLİĞİ ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- TOOLTIP (BALONCUK) SINIFI ---
class CTkToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = ctk.CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ctk.CTkLabel(tw, text=self.text, fg_color="#333333", corner_radius=5, padx=5, pady=2)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class SnapSumPro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SnapSum Pro - Ders Notu Özetleyici")
        self.geometry("1300x850") 

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=0) 
        self.grid_rowconfigure(0, weight=1)

        # --- 1. SOL SÜTUN: KÜTÜPHANELER ---
        self.sidebar = ctk.CTkFrame(self, width=380, corner_radius=0, fg_color="#121212")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="SnapSum", font=("Inter", 28, "bold"), text_color="#3B82F6").pack(pady=20)
        
        # GENEL KÜTÜPHANE
        ctk.CTkLabel(self.sidebar, text="GENEL KÜTÜPHANE", font=("Inter", 11, "bold"), text_color="gray").pack(pady=(10,5), padx=20, anchor="w")
        ctk.CTkButton(self.sidebar, text="+ Dosya Yükle", fg_color="#1E1E1E", border_width=1, command=lambda: self.load_file("genel")).pack(pady=5, padx=20, fill="x")
        self.scroll_genel = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", height=280)
        self.scroll_genel.pack(fill="x", padx=10)

        # ŞAHSİ KÜTÜPHANEM
        ctk.CTkLabel(self.sidebar, text="ŞAHSİ KÜTÜPHANEM", font=("Inter", 11, "bold"), text_color="gray").pack(pady=(20,5), padx=20, anchor="w")
        ctk.CTkButton(self.sidebar, text="+ Dosya Yükle", fg_color="#3B82F6", command=lambda: self.load_file("sahsi")).pack(pady=5, padx=20, fill="x")
        self.scroll_sahsi = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", height=280)
        self.scroll_sahsi.pack(fill="x", padx=10)

        # --- 2. ORTA SÜTUN: OKUYUCU ---
        self.reader_frame = ctk.CTkFrame(self, fg_color="#0F0F0F", corner_radius=0)
        self.reader_frame.grid(row=0, column=1, sticky="nsew", padx=2)
        self.reader_text = ctk.CTkTextbox(self.reader_frame, font=("Georgia", 16), fg_color="transparent", text_color="#E0E0E0")
        self.reader_text.pack(expand=True, fill="both", padx=40, pady=40)

        # --- 3. SAĞ SÜTUN: AI ANALİZ ---
        self.tools_sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#121212")
        self.tools_sidebar.grid(row=0, column=2, sticky="nsew")
        ctk.CTkLabel(self.tools_sidebar, text="AI ANALİZ & ÖZET", font=("Inter", 13, "bold")).pack(pady=(30, 20))
        
        self.summary_mode = ctk.StringVar(value="Orta")
        for text, val in [("Kısa", "Kısa"), ("Orta", "Orta"), ("Uzun", "Uzun")]:
            ctk.CTkRadioButton(self.tools_sidebar, text=text, variable=self.summary_mode, value=val).pack(pady=10, padx=20, anchor="w")

        ctk.CTkButton(self.tools_sidebar, text="Analiz Et", height=40, fg_color="#059669", command=self.run_analysis).pack(pady=30, padx=20, fill="x")
        self.summary_box = ctk.CTkTextbox(self.tools_sidebar, height=350, fg_color="#1E1E1E")
        self.summary_box.pack(pady=10, padx=20, fill="x")

    def load_file(self, target):
        path = filedialog.askopenfilename(filetypes=[("Belgeler", "*.pdf *.png *.jpg *.jpeg")])
        if path:
            self.clear_main_screen()
            filename = path.split("/")[-1]
            
            content = ""
            if filename.lower().endswith(".pdf"):
                try:
                    doc = fitz.open(path)
                    content = "".join([page.get_text() for page in doc])
                    doc.close()
                except:
                    content = "Hata: PDF okunamadı."
            else:
                content = f"--- GÖRSEL ANALİZ: {filename} ---"
            
            self.reader_text.insert("1.0", content)
            
            scroll_target = self.scroll_genel if target == "genel" else self.scroll_sahsi
            item_frame = ctk.CTkFrame(scroll_target, fg_color="transparent")
            item_frame.pack(fill="x", pady=2)

            del_btn = ctk.CTkButton(item_frame, text="🗑️", fg_color="transparent", text_color="#EF4444", 
                                    width=40, font=("Inter", 15),
                                    command=lambda f=item_frame: self.delete_item(f))
            del_btn.pack(side="right", padx=(5, 10))

            # Dosya ismi çok uzunsa kısaltıyoruz
            short_name = filename if len(filename) < 25 else filename[:22] + "..."
            file_btn = ctk.CTkButton(item_frame, text=f"📄 {short_name}", fg_color="transparent", 
                                     anchor="w", font=("Inter", 12),
                                     command=lambda c=content: self.show_text(c))
            file_btn.pack(side="left", fill="x", expand=True)

            # TOOLTIP EKLEME: Üstüne gelince tam ismi gösterir
            CTkToolTip(file_btn, filename)

    def show_text(self, content):
        self.reader_text.delete("1.0", "end")
        self.reader_text.insert("1.0", content)

    def delete_item(self, frame):
        frame.destroy()
        self.clear_main_screen()

    def clear_main_screen(self):
        self.reader_text.delete("1.0", "end")
        self.summary_box.delete("1.0", "end")

    def run_analysis(self):
        self.summary_box.delete("1.0", "end")
        self.summary_box.insert("1.0", f"[{self.summary_mode.get()}] Analiz tamamlandı.")

if __name__ == "__main__":
    app = SnapSumPro()
    app.mainloop()