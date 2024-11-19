#!/bin/bash

# Configuration minimale de python
python_minimal=3.11
python_minimal_maj=$(echo $python_minimal | cut -d. -f1)
python_minimal_min=$(echo $python_minimal | cut -d. -f2)

# Configuration par défaut de python
python_default=3.12

# Chemin de python
python_path=""

# Cas d'utilisation : Afficher une erreur et quitter le script
handle_error() {
    echo -e "\033[31mErreur : $1\033[0m" 
    exit 1
}

# Cas d'utilisation : Identifier un succès
handle_success() {
    echo -e "\033[32mSuccès : $1\033[0m"
    return 0
}

# Cas d'utilisation : Afficher un conseil
handle_advice() {
    echo -e "\033[38;5;214mConseil : $1\033[0m"
}

# Cas d'utilisation : Vérifier la présence, ou non, de python sur la machine
# Retour : 0 ou 1 (succès ou échec)
check_python_installed() {
    if ! command -v python3 &> /dev/null; then
        echo "Python n'est pas installé sur ce système."
        return 1
        else 
            echo "Python est installé sur ce système."
            return 0
    fi
}

# Cas d'utilisation : Vérifier la version de python installée
# Retour : 0 ou 1 (supérieur ou égale à 3.10 ou inférieur à 3.11)
check_python_version() {
    # Récupération de la version de Python
    version=$(python3 --version 2>&1 | awk '{print $2}')
    
    # Extraction de la version majeure et mineure
    major_version=$(echo $version | cut -d. -f1)
    minor_version=$(echo $version | cut -d. -f2)
    
    # Comparaison de la version avec 3.11
    if [[ $major_version -gt $python_minimal_maj || ( $major_version -eq python_minimal_maj && $minor_version -ge python_minimal_min ) ]]; then
        echo "La version de Python installée ($version) est supérieure ou égale à $python_minimal."
        return 0
    else
        echo "La version de Python installée ($version) est inférieure à $python_minimal."
        return 1  # Code d'erreur
    fi
}

# Cas d'utilisation : Vérifier et installer homebrew
install_homebrew() {
    echo "Vérification de la présence de Homebrew..."
    if ! command -v brew &> /dev/null; then
    echo "Homebrew non installé. Installation..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)" # Pour configurer Homebrew dans le PATH

    handle_advice "Il peut être necéssaire de redémarrer le terminal pour vérifier l'installation de Homebrew."

    # Vérifier si l'installation a réussi après avoir mis à jour le PATH et après ouverture d'une nouvelle session
    if ! command -v brew &> /dev/null; then
        handle_error "L'installation de Homebrew a échoué. Le script va être arrêté."
    fi

    handle_success "Homebrew a été installé avec succès"
    
    else 
        echo "Homebrew est déjà installé."
    fi
}

# Cas d'utilisation : Installer python 3.12
# Retour : 0 ou 1 (succès ou échec)
install_python() {
    echo "Installation de Python $python_default via Homebrew..."
    brew install python@$python_default    
    python$python_default --version
    if [[ $? -eq 0 ]]; then
        handle_success "Python $python_default installé avec succès."
    else
        handle_error "Problème lors de l'installation de Python $python_default."
    fi
}

# Cas d'utilisation : Installer HomeBrew et Python si nécessaire
ensure_python() {
    check_python_installed
    if [[ $? -ne 0 ]] || ! check_python_version; then
        echo "Installation ou mise à jour de Python $python_default..."
        install_homebrew
        install_python
        python_path=$(command -v python$python_default)
    else
        python_path=$(command -v python3)
    fi
}

# Cas d'utilisation : Création d'un environnement virtuel
# Retour : 0 ou 1 (succès ou échec)
create_venv() {
    if [[ -z "$python_path" ]]; then
        handle_error "python_path non défini, impossible de créer le VENV."
    fi

    "$python_path" -m venv venv
    if [[ $? -eq 0 ]]; then
        handle_success "Création du VENV avec succès."
    else
        handle_error "Problème lors de la création du VENV"
    fi
}

# Cas d'utilisation : Installation des requirements
# Retour : 0 ou 1 (succès ou échec)
install_requirements() {
    if [[ ! -f "./requirements.txt" ]]; then
        handle_error "requirements.txt non trouvé dans le répertoire actuel."
    fi

    # Installer les modules depuis requirements.txt
    echo "Installation des modules depuis requirements.txt..."
    sudo -H ./venv/bin/python -m pip install -r requirements.txt
    if [[ $? -eq 0 ]]; then
        handle_success "Modules installés avec succès."
    else
        handle_error "Problème lors de l'installation des modules."
    fi
}

# Cas d'utilisation : Exécuter le script main.py
# Retour : 0 ou 1 (succès ou échec)
launch_main_py() {
    if [[ ! -f "./main.py" ]]; then
        handle_error "main.py non trouvé dans le répertoire actuel."
    fi

    if [[ ! -d "./venv" ]]; then
        handle_error "L'environnement virtuel venv n'existe pas. Veuillez le créer avant de lancer main.py."
    fi

    echo "Exécution de main.py"
    ./venv/bin/python main.py
    if [[ $? -ne 0 ]]; then
        handle_error "Problème lors du lancement de main.py (Code de sortie : $?)."
    fi
}

# 1. S'assurer de la disponibilité de python
ensure_python

# 2. Création du VENV
create_venv

# 3. Installation des requirements
install_requirements

# 4. Lancement du script main.py
#launch_main_py
