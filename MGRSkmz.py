import simplekml
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import mgrs
from tkintermapview import TkinterMapView
import re
from simplekml import Kml  # Import per la creazione del KMZ

# Funzione per verificare la validità delle coordinate MGRS
def valida_coordinate_mgrs(coordinate):
    pattern = r"^\d{1,2}[C-HJ-NP-X][A-HJ-NP-Z]{2}\s?\d{1,5}\s?\d{1,5}$"
    return re.match(pattern, coordinate.strip())

# Funzione per aggiungere un punto
def aggiungi_punto():
    nome = entry_nome.get()
    coordinate = entry_coordinate.get().strip().upper()  # Conversione in maiuscolo

    if not nome or not coordinate:
        messagebox.showwarning("Errore", "Inserire sia il nome che le coordinate!")
        return

    if not valida_coordinate_mgrs(coordinate):
        messagebox.showerror("Errore", "Coordinate MGRS non valide! Controlla il formato.")
        return

    try:
        # Conversione coordinate MGRS in lat/lon
        m = mgrs.MGRS()
        lat, lon = m.toLatLon(coordinate.encode("utf-8"))
        punti.append({"nome": nome, "lat": lat, "lon": lon, "mgrs": coordinate})
        lista.insert(tk.END, f"{nome}: {coordinate}")
        entry_nome.delete(0, tk.END)
        entry_coordinate.delete(0, tk.END)

        # Aggiungi marker sulla mappa
        map_widget.set_marker(lat, lon, text=nome)
        label_status.config(text=f"Punto '{nome}' aggiunto con successo!", foreground="green")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la conversione MGRS: {e}")

# Funzione per eliminare un punto
def elimina_punto():
    selezione = lista.curselection()
    if not selezione:
        messagebox.showwarning("Errore", "Seleziona un punto da eliminare!")
        return

    indice = selezione[0]
    lista.delete(indice)
    punti.pop(indice)

    # Aggiorna i marker sulla mappa
    map_widget.delete_all_marker()
    for punto in punti:
        map_widget.set_marker(punto["lat"], punto["lon"], text=punto["nome"])

    label_status.config(text="Punto eliminato con successo!", foreground="blue")

# Funzione per modificare un punto
def modifica_punto():
    selezione = lista.curselection()
    if not selezione:
        messagebox.showwarning("Errore", "Seleziona un punto da modificare!")
        return

    indice = selezione[0]
    punto = punti[indice]

    # Pre-compila i campi di input
    entry_nome.delete(0, tk.END)
    entry_nome.insert(0, punto["nome"])

    entry_coordinate.delete(0, tk.END)
    entry_coordinate.insert(0, punto["mgrs"])

    # Rimuove il punto dalla lista temporaneamente
    lista.delete(indice)
    punti.pop(indice)

    # Aggiorna i marker sulla mappa
    map_widget.delete_all_marker()
    for p in punti:
        map_widget.set_marker(p["lat"], p["lon"], text=p["nome"])

    # Zoom e centraggio sulla mappa sul punto selezionato
    map_widget.set_position(punto["lat"], punto["lon"])  # Sposta la mappa
    map_widget.set_zoom(10)  # Fai uno zoom maggiore per visualizzare il punto più da vicino

    label_status.config(text=f"Punto '{punto['nome']}' modificato con successo!", foreground="orange")



# Funzione per esportare in formato KMZ
def genera_kmz():
    if not punti:
        messagebox.showwarning("Errore", "Nessun punto inserito!")
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".kmz", filetypes=[("File KMZ", "*.kmz")])
    if not filepath:
        return

    try:
        kml = Kml()
        for punto in punti:
            kml.newpoint(name=punto["nome"], coords=[(punto["lon"], punto["lat"])])
        kml.savekmz(filepath)
        label_status.config(text=f"File KMZ salvato: {filepath}", foreground="green")
    except Exception as e:
        messagebox.showerror("Errore", f"Errore durante la creazione del KMZ: {e}")

# Creazione finestra principale
root = tk.Tk()
root.title("MGRS WP export file KMZ by Antonino Fortunato")
root.geometry("1200x700")
root.iconbitmap("C:/Users/anton/Desktop/progetti python/iconamgrs.ico")
# Lista per i punti
punti = []

# Frame principale
frame_main = tk.Frame(root)
frame_main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Frame sinistro (Input e Lista)
frame_sinistro = tk.Frame(frame_main, width=300)
frame_sinistro.pack(side=tk.LEFT, fill=tk.Y, padx=10)

# Titolo
title_label = tk.Label(frame_sinistro, text="Gestione WP", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

# Entry per Nome e Coordinate
label_nome = tk.Label(frame_sinistro, text="Nome WP:")
label_nome.pack()
entry_nome = ttk.Entry(frame_sinistro, width=30)
entry_nome.pack(pady=5)

label_coordinate = tk.Label(frame_sinistro, text="Coordinate MGRS:")
label_coordinate.pack()
entry_coordinate = ttk.Entry(frame_sinistro, width=30)
entry_coordinate.pack(pady=5)

# Pulsante per aggiungere un punto
btn_aggiungi = ttk.Button(frame_sinistro, text="Aggiungi WP", command=aggiungi_punto, width=30)
btn_aggiungi.pack(pady=10)

# Pulsante per modificare un punto
btn_modifica = ttk.Button(frame_sinistro, text="Modifica WP", command=modifica_punto, width=30)
btn_modifica.pack(pady=10)

# Pulsante per eliminare un punto
btn_elimina = ttk.Button(frame_sinistro, text="Elimina WP", command=elimina_punto, width=30)
btn_elimina.pack(pady=10)


# Pulsante per esportare KMZ
btn_genera_kmz = ttk.Button(frame_sinistro, text="Esporta KMZ file", command=genera_kmz, width=30)
btn_genera_kmz.pack(pady=10)

# Lista dei punti
lista = tk.Listbox(frame_sinistro, width=40, height=20)
lista.pack(padx=5, pady=5)

# Barra di stato
label_status = tk.Label(frame_main, text="Benvenuto!", relief=tk.SUNKEN, anchor="w", font=("Helvetica", 10))
label_status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

# Frame della mappa
frame_mappa = tk.Frame(frame_main)
frame_mappa.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Creazione della mappa
map_widget = TkinterMapView(frame_mappa, width=800, height=600, corner_radius=0)
map_widget.pack(fill=tk.BOTH, expand=True)

# Centrare la mappa sull'Italia (posizione di Roma)
map_widget.set_position(41.9028, 12.4964)  # Coordinate centrali di Roma
map_widget.set_zoom(5)  # Impostare un livello di zoom adeguato per visualizzare tutta l'Italia


root.mainloop()