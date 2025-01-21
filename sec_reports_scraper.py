import os
import requests
from bs4 import BeautifulSoup

# URL de la page des rapports SEC
BASE_URL = "https://investor.apple.com/sec-filings/default.aspx"
DOWNLOAD_FOLDER = "sec_reports"

# Créez un dossier pour stocker les PDF
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def get_pdf_links(base_url):
    """Scrape les liens vers les fichiers PDF depuis la page SEC."""
    response = requests.get(base_url)
    print(response)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Trouver les liens PDF (ajuster la classe ou l'attribut si nécessaire)
    links = soup.find_all("a", href=True, recursive=True)
    print(links)
    pdf_links = [link['href'] for link in links if link['href'].endswith('.pdf')]
    return pdf_links

def download_pdfs(pdf_links, folder):
    """Télécharge les fichiers PDF dans le dossier spécifié."""
    for link in pdf_links:
        pdf_url = f"https://investor.apple.com{link}"
        pdf_name = link.split("/")[-1]
        pdf_path = os.path.join(folder, pdf_name)
        
        print(f"Téléchargement de {pdf_name}...")
        response = requests.get(pdf_url)
        with open(pdf_path, "wb") as file:
            file.write(response.content)
        print(f"{pdf_name} téléchargé avec succès dans {folder}")

# Étape 1 : Récupérer les liens des PDF
pdf_links = get_pdf_links(BASE_URL)

# Étape 2 : Télécharger les fichiers
download_pdfs(pdf_links, DOWNLOAD_FOLDER)
