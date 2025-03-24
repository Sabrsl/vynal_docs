import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class CTkApp:
    def __init__(self):
        # Configurer l'apparence
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Créer la fenêtre principale
        self.root = ctk.CTk()
        self.root.title("Test CustomTkinter")
        self.root.geometry("600x400")
        
        # Créer un frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Ajouter un titre
        self.title_label = ctk.CTkLabel(
            self.main_frame,
            text="Interface CustomTkinter de test",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=20)
        
        # Ajouter un bouton de test
        self.test_button = ctk.CTkButton(
            self.main_frame,
            text="Tester l'interface",
            command=self.test_interface
        )
        self.test_button.pack(pady=20)
        
        # Bouton pour quitter
        self.quit_button = ctk.CTkButton(
            self.main_frame,
            text="Quitter",
            command=self.on_close,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.quit_button.pack(pady=20)
        
        # Configurer le gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Démarrer la boucle principale
        self.root.mainloop()
    
    def test_interface(self):
        """Méthode de test simple"""
        messagebox.showinfo("Test", "L'interface CustomTkinter fonctionne correctement!")
    
    def on_close(self):
        """Ferme l'application"""
        self.root.destroy()

# Démarrer l'application
if __name__ == "__main__":
    CTkApp() 