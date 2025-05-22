import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil  # Per eliminare cartelle non vuote
import tempfile # Per ottenere la cartella temp dell'utente
import ctypes # Per verificare i privilegi di amministratore

# --- Funzioni Logiche Core ---

def is_admin():
    """Controlla se lo script è in esecuzione con privilegi di amministratore."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_temp_paths():
    """Restituisce una lista di percorsi delle cartelle temporanee comuni."""
    paths = []
    
    # 1. Cartella temporanea dell'utente (più affidabile)
    try:
        user_temp = tempfile.gettempdir()
        if user_temp and os.path.exists(user_temp):
            paths.append(user_temp)
            print(f"Trovata cartella temp utente: {user_temp}")
    except Exception as e:
        print(f"Errore nell'ottenere la cartella temp utente: {e}")

    # 2. Cartella temporanea di sistema (C:\Windows\Temp)
    system_temp_win = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp")
    if os.path.exists(system_temp_win):
        paths.append(system_temp_win)
        print(f"Trovata cartella temp di sistema: {system_temp_win}")
    else:
        print(f"Cartella temp di sistema non trovata: {system_temp_win}")
        
    # Rimuove duplicati se ce ne fossero (improbabile con questi due)
    return list(set(paths))

def get_folder_size(folder_path):
    """Calcola la dimensione totale di una cartella in byte."""
    total_size = 0
    # Verifica se il percorso esiste e se si hanno i permessi di lettura
    if not os.path.exists(folder_path):
        print(f"Percorso non esistente: {folder_path}")
        return 0
        
    try:
        # os.walk gestisce i permessi man mano che scende, ma la radice deve essere accessibile
        if not os.access(folder_path, os.R_OK | os.X_OK): # Permesso di lettura ed esecuzione (per listare)
             print(f"Accesso negato (lettura/esecuzione) a: {folder_path}")
             return 0

        for dirpath, dirnames, filenames in os.walk(folder_path, topdown=True, onerror=handle_walk_error):
            # Filtra le directory a cui non si ha accesso per evitare di bloccare os.walk
            accessible_dirnames = []
            for d in dirnames:
                current_dir_path = os.path.join(dirpath, d)
                if os.access(current_dir_path, os.R_OK | os.X_OK):
                    accessible_dirnames.append(d)
                else:
                    print(f"Permesso negato per accedere alla sottocartella (durante calcolo dimensione): {current_dir_path}")
            dirnames[:] = accessible_dirnames # Modifica dirnames in-place per os.walk

            for f in filenames:
                fp = os.path.join(dirpath, f)
                # Salta i link simbolici rotti o se non è un file
                # e verifica l'esistenza e i permessi prima di chiamare getsize
                if os.path.exists(fp) and not os.path.islink(fp) and os.path.isfile(fp):
                    if os.access(fp, os.R_OK):
                        try:
                            total_size += os.path.getsize(fp)
                        except FileNotFoundError:
                            # Il file potrebbe essere stato eliminato nel frattempo
                            print(f"File non trovato durante il calcolo dimensione: {fp}")
                        except PermissionError:
                            print(f"Permesso negato per accedere alla dimensione di (file): {fp}")
                    else:
                        print(f"Permesso negato per leggere il file (dimensione): {fp}")
    
    except PermissionError as pe:
        # Questo cattura il permesso negato sulla cartella radice passata a os.walk
        print(f"Permesso negato nell'accedere alla cartella principale per il calcolo: {folder_path} - {pe}")
    except Exception as e:
        print(f"Errore generico durante il calcolo della dimensione per {folder_path}: {e}")
    return total_size

def handle_walk_error(os_error):
    """Gestore di errori per os.walk, per loggare e continuare."""
    print(f"Errore durante os.walk (probabile permesso negato): {os_error}")
    # Non sollevare l'eccezione per permettere a os.walk di continuare con altri elementi se possibile

def format_size(size_bytes):
    """Converte byte in un formato leggibile (KB, MB, GB)."""
    if size_bytes < 0: size_bytes = 0 # Sanity check
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(abs(size_bytes), 1024)))
    if i < 0 : i = 0 # Se size_bytes è < 1024 ma > 0
    if i >= len(size_name): i = len(size_name) -1 # Evita IndexError per dimensioni enormi

    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def clean_folder_contents(folder_path, progress_callback=None):
    """Pulisce il contenuto di una cartella (file e sottocartelle)."""
    deleted_items_count = 0
    failed_items_count = 0
    
    if not os.path.exists(folder_path):
        print(f"Cartella da pulire non trovata: {folder_path}")
        if progress_callback: progress_callback(f"Cartella non trovata: {folder_path}")
        return deleted_items_count, failed_items_count

    # Verifica i permessi di scrittura ed esecuzione sulla cartella principale
    if not os.access(folder_path, os.W_OK | os.X_OK):
        msg = f"Permesso negato per scrivere o elencare contenuto di: {folder_path}"
        print(msg)
        if progress_callback: progress_callback(msg)
        # Potremmo non essere in grado di eliminare nulla qui.
        # Tentiamo comunque gli elementi interni, ma è probabile che fallisca.

    # os.listdir() potrebbe fallire se non ci sono permessi di lettura/esecuzione
    try:
        items = os.listdir(folder_path)
    except PermissionError:
        msg = f"Permesso negato per elencare il contenuto di: {folder_path}"
        print(msg)
        if progress_callback: progress_callback(msg)
        return deleted_items_count, 1 # Considera la cartella stessa come un fallimento

    for item_name in items:
        item_path = os.path.join(folder_path, item_name)
        if progress_callback: progress_callback(f"Tento di eliminare: {item_path}")
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                if os.access(item_path, os.W_OK): # Verifica permesso di scrittura sul file
                    os.unlink(item_path) # Elimina file o link
                    deleted_items_count += 1
                    if progress_callback: progress_callback(f"Eliminato: {item_path}")
                else:
                    # Potrebbe essere che la cartella genitore ha i permessi, ma il file no (ACL specifiche)
                    print(f"Permesso negato per scrivere/eliminare il file: {item_path}")
                    if progress_callback: progress_callback(f"Fallito (permesso file): {item_path}")
                    failed_items_count +=1
            elif os.path.isdir(item_path):
                # shutil.rmtree necessita che la cartella e il suo contenuto siano accessibili
                # Tentiamo comunque, shutil.rmtree ha una sua gestione errori
                shutil.rmtree(item_path, onerror=handle_shutil_error) # Aggiunto onerror
                deleted_items_count += 1 # Considera la cartella come un singolo item eliminato
                if progress_callback: progress_callback(f"Eliminata cartella (o tentato): {item_path}")

        except PermissionError as pe_item:
            msg = f"Permesso negato per eliminare: {item_path} (probabilmente in uso o protetto) - {pe_item}"
            print(msg)
            if progress_callback: progress_callback(f"Fallito (permesso): {item_path}")
            failed_items_count += 1
        except Exception as e_item:
            msg = f"Errore generico durante l'eliminazione di {item_path}: {e_item}"
            print(msg)
            if progress_callback: progress_callback(f"Fallito (errore): {item_path}")
            failed_items_count += 1
            
    return deleted_items_count, failed_items_count

def handle_shutil_error(func, path, exc_info):
    """Gestore di errori per shutil.rmtree."""
    # func è la funzione che ha causato l'errore (es. os.unlink, os.rmdir)
    # path è il percorso su cui operava la funzione
    # exc_info è una tupla (tipo_eccezione, istanza_eccezione, traceback)
    print(f"Errore durante shutil.rmtree su {path} (funzione: {func.__name__}): {exc_info[1]}")
    # Non sollevare l'eccezione per permettere a rmtree di continuare con altri file/cartelle se possibile
    # Questo aiuta a pulire il più possibile anche se alcuni file sono bloccati.
    # Incrementeremo failed_items_count nella funzione chiamante se necessario,
    # anche se rmtree potrebbe aver già eliminato parte del contenuto.


# --- Funzioni per la GUI ---

def update_status(message):
    """Aggiorna l'etichetta di stato e la console."""
    print(message) # Log anche su console
    status_var.set(message)
    root.update_idletasks() # Aggiorna la GUI immediatamente

def analyze_temp_files():
    """Azione per il pulsante Analizza."""
    update_status("Analisi in corso... attendere prego.")
    
    if not is_admin():
        update_status("Analisi limitata: eseguire come Amministratore per risultati completi.")
        # Non interrompo, ma l'utente è avvisato.

    paths_to_scan = get_temp_paths()
    if not paths_to_scan:
        messagebox.showinfo("Analisi", "Nessuna cartella temporanea standard trovata o accessibile.")
        update_status("Nessuna cartella temporanea trovata.")
        return

    total_temp_size = 0
    update_status("Inizio calcolo dimensioni...")
    for i, path in enumerate(paths_to_scan):
        update_status(f"Analisi di: {path} ({i+1}/{len(paths_to_scan)})...")
        size_this_folder = get_folder_size(path)
        total_temp_size += size_this_folder
        update_status(f"Analisi di: {path} - Dim: {format_size(size_this_folder)}. Totale parziale: {format_size(total_temp_size)}")
        
    size_str = format_size(total_temp_size)
    result_message = f"Spazio totale stimato occupato dai file temporanei: {size_str}"
    
    messagebox.showinfo("Analisi Completata", result_message)
    update_status(f"Spazio occupato: {size_str}. Pronto.")

def clean_temp_files_action():
    """Azione per il pulsante Pulisci."""
    if not is_admin():
        warn_admin = messagebox.askyesno("Privilegi Insufficienti",
                                         "Lo script non sembra essere in esecuzione come Amministratore.\n"
                                         "La pulizia potrebbe fallire o essere incompleta.\n"
                                         "Continuare comunque?")
        if not warn_admin:
            update_status("Pulizia annullata. Eseguire come Amministratore.")
            return

    confirm = messagebox.askyesno("Conferma Pulizia", 
                                  "Sei sicuro di voler eliminare i file temporanei?\n"
                                  "Questa azione non può essere annullata.\n"
                                  "Assicurati che tutti i programmi importanti siano chiusi.")
    if not confirm:
        update_status("Pulizia annullata dall'utente.")
        return

    update_status("Pulizia in corso... attendere prego.")
    
    paths_to_clean = get_temp_paths()
    if not paths_to_clean:
        messagebox.showinfo("Pulizia", "Nessuna cartella temporanea standard trovata o accessibile per la pulizia.")
        update_status("Nessuna cartella temporanea per la pulizia.")
        return

    total_deleted = 0
    total_failed = 0
    
    for i, path in enumerate(paths_to_clean):
        update_status(f"Pulizia di: {path} ({i+1}/{len(paths_to_clean)})...")
        # Passa la funzione di callback per aggiornamenti più granulari
        deleted, failed = clean_folder_contents(path, progress_callback=lambda msg: update_status(f"Pulizia {path}: {msg}"))
        total_deleted += deleted
        total_failed += failed
        
    result_message = f"Pulizia completata.\nElementi stimati eliminati: {total_deleted}\nElementi stimati falliti/saltati: {total_failed}"
    
    messagebox.showinfo("Pulizia Completata", result_message)
    update_status(f"Eliminati: {total_deleted}, Falliti: {total_failed}. Rieseguire analisi per aggiornamento spazio.")


# --- Creazione della GUI ---
root = tk.Tk()
root.title("PyTemp Cleaner")
root.geometry("550x250") # Dimensioni finestra leggermente più grandi per lo status
root.resizable(False, False) # Impedisce il ridimensionamento della finestra (e disabilita il pulsante massimizza)

# Stile (opzionale, per un look più moderno se ttk è disponibile)
style = ttk.Style()
available_themes = style.theme_names()
if "vista" in available_themes: # Prova 'vista' o 'xpnative' per un look più nativo su Windows
    style.theme_use("vista")
elif "xpnative" in available_themes:
    style.theme_use("xpnative")
elif "clam" in available_themes: # Clam è un fallback comune
    style.theme_use("clam")

main_frame = ttk.Frame(root, padding="10 10 10 10") # Aggiunto padding uniforme
main_frame.pack(expand=True, fill=tk.BOTH)

# Etichetta per lo stato/risultati
status_var = tk.StringVar()
status_var.set("Pronto. Clicca 'Analizza' per iniziare o 'Pulisci' per eliminare.")
status_label = ttk.Label(main_frame, textvariable=status_var, wraplength=500, justify=tk.LEFT) # wraplength e justify
status_label.pack(pady=(5,10), fill=tk.X) # fill=tk.X per usare la larghezza

# Frame per i pulsanti per migliore organizzazione
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill=tk.X, pady=5)

analyze_button = ttk.Button(button_frame, text="Analizza Spazio Temporaneo", command=analyze_temp_files)
analyze_button.pack(side=tk.LEFT, padx=(0,5), expand=True, fill=tk.X) # expand e fill

clean_button = ttk.Button(button_frame, text="Pulisci File Temporanei", command=clean_temp_files_action)
clean_button.pack(side=tk.LEFT, padx=(5,0), expand=True, fill=tk.X) # expand e fill

# Info diritti amministratore
admin_status_text = "Eseguito come Amministratore." if is_admin() else "NON eseguito come Amministratore (funzionalità limitate)."
admin_info_label = ttk.Label(main_frame, text=admin_status_text, font=("Segoe UI", 8))
admin_info_label.pack(pady=(10,0), side=tk.BOTTOM, fill=tk.X)


# Avvia la GUI
if __name__ == "__main__":
    # Controlla i privilegi all'avvio e mostra un avviso se non è admin
    if not is_admin():
        # Questo messagebox appare prima della finestra principale se non admin
        messagebox.showwarning("Avviso Privilegi", 
                               "Lo script non è in esecuzione con privilegi di Amministratore.\n"
                               "L'analisi potrebbe essere incompleta e la pulizia potrebbe fallire per alcune cartelle.\n"
                               "Per funzionalità complete, esegui lo script come Amministratore.")
    root.mainloop()