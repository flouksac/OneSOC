#!/bin/bash

# Configuration minimale de python
python_minimal=3.10
python_minimal_maj=$(echo $python_minimal | cut -d. -f1)
python_minimal_min=$(echo $python_minimal | cut -d. -f2)

# Configuration par défaut de python
python_default=3.12

# Chemin de python
python_path=""

# Cas d'utilisation : Afficher une erreur et quitter le script
handle_error () {
    echo -e "\033[31mErreur : $1\033[0m" 
    exit 1
}

# Cas d'utilisation : Identifier un succès
handle_success() {
    echo -e "\033[32mSuccès : $1\033[0m"
    echo
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

# Cas d'utilisation : Vérifier si l'utilisateur possède les droits administrateurs
# Retour : 0 ou 1 (succès ou échec)
is_root() {
    echo "Ce script doit etre execute en tant qu'administrateur (avec sudo)."
    echo "Verification ..."
    if [ "$EUID" -ne 0 ]; then
        handle_error "Relancer en tant qu'administrateur"
    else 
        handle_success "Le script est lancé en tant qu'administrateur"
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
    
    # Comparaison de la version avec 3.10
    if [[ $major_version -gt $python_minimal_maj || ( $major_version -eq $python_minimal_maj && $minor_version -ge $python_minimal_min ) ]]; then
        echo "La version de Python installée est $version, elle est supérieure ou égale à $python_minimal."
        return 0  # Code de succès
    else
        echo "La version de Python installée ($version) est inférieure à $python_minimal."
        return 1  # Code d'erreur
    fi
}

# Cas d'utilisation : Mise à jour des paquets
# Retour : 0 ou 1 (succès ou échec)
update_packages() {
    echo "Mise à jour des paquets..."

    # Vérification de l'outil de gestion de paquets et exécution des commandes appropriées
    if command -v apt-get &> /dev/null; then
        echo "Utilisation de apt-get pour mettre à jour les paquets..."
        apt-get update &> /dev/null && apt-get upgrade &> /dev/null -y || handle_error "Échec de la mise à jour des paquets avec apt."
        handle_success "Mise à jour des paquets terminée."
    elif command -v yum &> /dev/null; then
        echo "Utilisation de yum pour mettre à jour les paquets..."
        yum update -y &> /dev/null || handle_error "Échec de la mise à jour des paquets avec yum."
        handle_success "Mise à jour des paquets terminée."
    elif command -v dnf &> /dev/null; then
        echo "Utilisation de dnf pour mettre à jour les paquets..."
        dnf update -y &> /dev/null || handle_error "Échec de la mise à jour des paquets avec dnf."
        handle_success "Mise à jour des paquets terminée."
    else
        handle_error "Gestionnaire de paquets non pris en charge"
    fi
}

#Cas d'utilisation : Installer python
# Retour : 0 ou 1 (succès ou échec)
install_python() {
    echo "Installation de python"

    # Vérification de l'outil de gestion de paquets et exécution des commandes appropriées
    if command -v apt-get &> /dev/null; then
        echo "Utilisation de apt pour installer python..."
        apt-get install -y software-properties-common build-essential libffi-dev libssl-dev zlib1g-dev libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev libssl-dev &> /dev/null || handle_error "Problème lors de l'installation des dépendances pour python $python_default avec apt."
        add-apt-repository ppa:deadsnakes/ppa
        apt-get update
        apt-get install python$python_default -y &> /dev/null || handle_error "Problème lors de l'installation de python $python_default avec apt."
        handle_success "Installation de python terminée."
    elif command -v yum &> /dev/null; then
        echo "Utilisation de yum pour installer python..."
        yum install python$python_default -y &> /dev/null || handle_error "Problème lors de l'installation de python $python_default avec yum."
        handle_success "Installation de python terminée."
    elif command -v dnf &> /dev/null; then
        echo "Utilisation de dnf pour installer python..."
        dnf install python$python_default -y &> /dev/null || handle_error "Problème lors de l'installation de python $python_default avec dnf."
        handle_success "Installation de python terminée."
    else
        handle_error "Gestionnaire de paquets non pris en charge"
    fi

    # Vérification de l'installation de Python
    if python$python_default --version &> /dev/null; then
        python_path=$(command -v python$python_default)
        handle_success "Python $python_default installé avec succès." 
    else
        handle_error "L'installation de Python $python_default a échoué."
    fi
}

# Cas d'utilisation : Installer Python si nécessaire
ensure_python() {
    check_python_installed
    if [[ $? -ne 0 ]] || ! check_python_version; then
        echo "Installation ou mise à jour de Python $python_default..."
        update_packages
        install_python
        python_path=$(command -v python$python_default)
    else
        python_path=$(command -v python3)
    fi
}

# Cas d'utilisation : Installer pip
install_pip() {
    if command -v apt &> /dev/null; then 
        echo "Installation de pip via apt ..."
        sudo apt install -y python3-pip &> /dev/null || handle_error "Probleme lors de l'installation de pip"
    elif command -v yum &> /dev/null; then
        echo "Installation de pip via uym ..."
        sudo yum install -y python3-pip &> /dev/null || handle_error "Probleme lors de l'installation de pip"
    elif command -v dnf &> /dev/null; then
        echo "Installation de pip via dnf ..."
        sudo dnf install -y python3-pip &> /dev/null || handle_error "Probleme lors de l'installation de pip"
    else 
        handle_error "Gestionnaire de paquets non pris en charge"
    fi

    # Vérification de la présence de pip :
    if command -v pip3 &> /dev/null; then
        echo "Installation de pip reussie "
        handle_success "Version : $(pip3 --version)"
    else
        handle_error "Installation de pip non reussie"
    fi
}

# Cas d'utilisation : Installer module venv
install_module_venv() {
    if command -v apt &> /dev/null; then 
        echo "Installation du module venv via apt ..."
        sudo apt install -y python3-venv &> /dev/null || handle_error "Probleme lors de l'installation du module venv"
        handle_success "Installation du module venv reussie"
    elif command -v yum &> /dev/null; then
        echo "Installation du module venv via uym ..."
        sudo yum install -y python3-venv &> /dev/null || handle_error "Probleme lors de l'installation du module venv"
        handle_succes "Installation du module venv reussie"
    elif command -v dnf &> /dev/null; then
        echo "Installation du module venv via dnf ..."
        sudo dnf install -y python3-venv &> /dev/null || handle_error "Probleme lors de l'installation du module venv"
        handle_success "Installation du module venv reussie"
    else 
        handle_error "Gestionnaire de paquets non pris en charge"
    fi
}


# Cas d'utilisation : Création d'un environnement virtuel
# Retour : 0 ou 1 (succès ou échec)
create_venv() {
    if [[ -z "$python_path" ]]; then
        handle_error  "python_path non défini, impossible de créer le VENV."
    fi

    echo "Creation du venv en cours ..."
    "$python_path" -m venv venv &> /dev/null

    if [[ -d "venv" ]]; then
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
    ./venv/bin/python -m pip install -r requirements.txt &> /dev/null
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
        handle_error "L'environnement virtuel venv n'existe pas. Veuillez le créer avant de lancer main.py."
        handle_error "Problème lors du lancement de main.py (Code de sortie : $?)."
    fi
}

# 1. S'assurer que le script est lancé en tant qu'administrateur
is_root

# 2. Mise à jours des paquets
update_packages

# 3. S'assurer de la disponibilité de python
ensure_python

# 4. Installation de pip
install_pip

# 5. Installation du module venv
install_module_venv

# 6. Création du VENV
create_venv

# 7. Installation des requirements
install_requirements

# 8. Lancement du script main.py
#launch_main_py
