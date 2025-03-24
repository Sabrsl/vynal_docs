import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

class SimpleApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Test Interface Simple")
        self.root.geometry("600x400")
        
        # Créer un frame principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Ajouter un titre
        self.title_label = tk.Label(
            self.main_frame,
            text="Interface de test simple",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack(pady=20)
        
        # Ajouter un bouton de test
        self.test_button = tk.Button(
            self.main_frame,
            text="Tester l'interface",
            command=self.test_interface
        )
        self.test_button.pack(pady=20)
        
        # Bouton pour quitter
        self.quit_button = tk.Button(
            self.main_frame,
            text="Quitter",
            command=self.on_close
        )
        self.quit_button.pack(pady=20)
        
        # Configurer le gestionnaire de fermeture
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Démarrer la boucle principale
        self.root.mainloop()
    
    def test_interface(self):
        """Méthode de test simple"""
        messagebox.showinfo("Test", "L'interface fonctionne correctement!")
    
    def on_close(self):
        """Ferme l'application"""
        self.root.destroy()

# Démarrer l'application
if __name__ == "__main__":
    SimpleApp() 