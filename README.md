🧹 Pulitore File Temporanei per Windows 🗑️
Un semplice ma efficace strumento con interfaccia grafica (GUI) per analizzare e pulire i file temporanei dal tuo sistema Windows, aiutandoti a liberare spazio su disco! 🚀
✨ Funzionalità Principali
•	📊 Analisi Spazio: Calcola e visualizza lo spazio occupato dai file nelle cartelle temporanee più comuni di Windows.
•	🧹 Pulizia Rapida: Elimina i file temporanei con un clic, previa conferma.
•	💡 Interfaccia Semplice: Facile da usare grazie a una GUI intuitiva creata con Tkinter.
•	🚀 Avvio come Amministratore: Include un file .bat per lanciare facilmente l'applicazione con i privilegi di amministratore necessari per una pulizia completa.
🛠️ Prerequisiti
•	Sistema Operativo: Windows.
•	Python: Versione 3.x installata e aggiunta al PATH di sistema.
o	Puoi scaricare Python da python.org.
•	Moduli Python:
o	tkinter (solitamente incluso con l'installazione standard di Python)
o	shutil (incluso)
o	tempfile (incluso)
o	os (incluso)
o	ctypes (incluso)
🚀 Come Usare
1.	Scarica il Progetto:
o	Clona il repository: git clone https://github.com/TUO_USERNAME/NOME_TUO_REPOSITORY.git
o	Oppure scarica lo ZIP e scompattalo.
2.	Naviga nella Cartella: Apri un terminale o prompt dei comandi e spostati nella cartella del progetto.
3.	Esegui come Amministratore (Consigliato per la Pulizia):
o	Fai doppio clic sul file avvia_pulitore_admin.bat.
o	Questo script richiederà i privilegi di amministratore per garantire che l'applicazione possa accedere e pulire tutte le cartelle temporanee (specialmente C:\Windows\Temp).
o	Conferma la richiesta UAC (Controllo Account Utente) di Windows.
4.	Utilizza l'Applicazione:
o	Una volta avviata l'interfaccia:
	Clicca su "Analizza Spazio Temporaneo" per vedere quanto spazio è attualmente occupato.
	Clicca su "Pulisci File Temporanei" per eliminare i file. Ti verrà chiesta una conferma.
(Sostituisci il link sopra con uno screenshot reale della tua applicazione!)
⚠️ Note Importanti
•	Esegui come Amministratore: Per una pulizia efficace, specialmente della cartella C:\Windows\Temp e per evitare errori di accesso negato, è fondamentale eseguire l'applicazione tramite il file avvia_pulitore_admin.bat o comunque con privilegi elevati.
•	File in Uso: Alcuni file temporanei potrebbero essere attualmente in uso dal sistema o da altre applicazioni. Questi file non potranno essere eliminati e verranno segnalati come "falliti" o "saltati" durante il processo di pulizia. Questo è un comportamento normale.
•	Usa con Cautela: Sebbene l'applicazione sia progettata per eliminare solo file temporanei, l'eliminazione di file è un'operazione potente. Assicurati di capire cosa fa il programma.
🧑‍💻 Tecnologie Utilizzate
•	Python 3
•	Tkinter per l'interfaccia grafica (GUI)
•	Script Batch (.bat) per l'avvio facilitato con privilegi di amministratore
🤝 Contributi
I contributi sono benvenuti! Se hai idee per migliorare questo strumento, sentiti libero di:
•	Aprire una Issue per discutere di modifiche o segnalare bug.
•	Creare una Pull Request con i tuoi miglioramenti.
Spero che questo strumento ti sia utile! 😊
