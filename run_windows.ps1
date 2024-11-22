# PowerShell script for Windows

# Configuration minimale de python
$global:python_minimal=3.11
$global:python_minimal_maj="$python_minimal".Split(".")[0]
$global:python_minimal_min="$python_minimal".Split(".")[1]

# Configuration par défaut de python
$python_default=3.12

# Chemin de python
$global:pythonPath = $null

# Cas d'utilisation : Afficher une erreur et quitter le script
function handle_error {
    param (
        [string]$Message
    )
    Write-Host "Erreur : $Message" -ForegroundColor Red
    exit 1
}

# Cas d'utilisation : Identifier un succès
function handle_success {
    param (
        [string]$Message
    )
    Write-Host "Succès : $Message" -ForegroundColor Green
    return 0
}

# Cas d'utilisation : Afficher un conseil
function handle_advice {
    param (
        [string]$Message
    )
    Write-Host "Conseil : $Message" -ForegroundColor Yellow
}


# Cas d'utilisation : Vérifier la présence, ou non, de python sur la machine
# Retour : true ou false (succès ou échec)
function check_python_installed {
    if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
        Write-Output "Python n'est pas installé sur ce système."
        return $false
    } else {
        Write-Output "Python est installé sur ce système."
        return $true
    }
}

# Cas d'utilisation : Vérifier la version de python installée
# Retour : 0 ou 1 (supérieur ou égale à 3.10 ou inférieur à 3.11)
function check_python_version {
    # Get Python version
    $version = & python3 --version 2>&1 | ForEach-Object { "$_".Split(" ")[1] }
    
    # Extract major and minor version
    $majorVersion = "$version".Split(".")[0]
    $minorVersion = "$version".Split(".")[1]
    
    # Check if version is >= 3.11
    if ($majorVersion -gt 3 -or ($majorVersion -eq $python_minimal_maj -and $minorVersion -ge $python_minimal_min)) {
        Write-Output "La version de Python installée est $version, elle est supérieure ou égale à $python_minimal."
        return $true
    } else {
        Write-Output "La version de Python installée ($version) est inférieure à $python_minimal."
        return $false
    }
}

# Cas d'utilisation : Vérifier la présence de winget
function check_winget_installed {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Output "Winget n'est pas installé."
        return $false
    } else {
        Write-Output "Winget est installé sur ce système."
        return $true
    }
}

# Cas d'utilisation : Installer python
# Paramètre : $useWinget (true pour installer via Winget, false pour installation via URL)
# Retour : true ou false (succès ou échec)
function install_python {
    param (
        [bool]$useWinget
    )
    
    if ($useWinget) {
        # Tentative d'installation via Winget
        Write-Output "Installation de Python $python_default via Winget..."
        winget install --id Python.Python.$python_minimal_maj --version $python_default -e
        
        if ($?) {
            handle_success "Python $python_default installé avec succès via Winget."
        } else {
            handle_error "Problème lors de l'installation de Python $python_default via Winget."
        }
    } else {
        # Téléchargement et installation depuis le site officiel de Python
        Write-Output "Installation de Python $python_default via téléchargement direct..."
        $pythonInstallerUrl = "https://www.python.org/ftp/python/$python_default/python-$python_default-amd64.exe"
        $tempInstallerPath = "$env:TEMP\python-installer.exe"
        
        # Télécharger le fichier d'installation
        try {
            Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $tempInstallerPath -ErrorAction Stop
            Write-Output "Téléchargement de Python $python_default terminé."
        } catch {
            handle_error "Impossible de télécharger l'installateur Python."
        }

        # Exécuter l'installateur en mode silencieux
        Write-Output "Installation de Python $python_default..."
        Start-Process -FilePath $tempInstallerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

        # Vérifier l'installation
        if (Get-Command python -ErrorAction SilentlyContinue) {
            Remove-Item $tempInstallerPath -Force  # Nettoyer le fichier temporaire
            handle_success "Python $python_default installé avec succès."
        } else {
            Remove-Item $tempInstallerPath -Force  # Nettoyer le fichier temporaire
            handle_error "Problème lors de l'installation de Python $python_default."
        }
    }
}

# Cas d'utilisation : Installer Python si nécessaire
function ensure_python {
    # Vérifier si Python est installé et sa version
    $pythonInstalled = check_python_installed
    $pythonVersionOk = check_python_version
    if (-not $pythonInstalled -or -not $pythonVersionOk) {
        Write-Output "Installation ou mise à jour de python..."
        install_python -useWinget (check_winget_installed)
        $global:pythonPath = (Get-Command python$python_default).Source
    } else {
        $global:pythonPath = (Get-Command python3).Source
    }
}


# Cas d'utilisation : Création d'un environnement virtuel
# Retour : true ou false (succès ou échec)
function create_venv {
    if($global:pythonPath -eq $null) {
        handle_error "pythonPath n'est pas défini, impossible de créer l'environnement virtuel."
    }

    & "$global:pythonPath" -m venv venv
    if ($?) {
        handle_success "Environnement virtuel créé avec succès."
    } else {
        handle_error "Erreur lors de la création de l'environnement virtuel."
    }
}

# Cas d'utilisation : Installation des requirements
# Retour : true ou false (succès ou échec)
function install_requirements {
    # Vérifier si le fichier requirements.txt existe
    if (-not (Test-Path -Path "./requirements.txt")) {
        handle_error "requirements.txt non trouvé dans le répertoire actuel."
    }

    # Installer les modules depuis requirements.txt
    Write-Host "Installation des modules depuis requirements.txt..."
    
    # Exécute la commande pip à partir de l'environnement virtuel
    ./venv/Scripts/python.exe -m pip install -r requirements.txt

    # Vérifie si la commande a réussi
    if ($LASTEXITCODE -eq 0) {
        handle_success "Modules installés avec succès."
    } else {
        handle_error "Problème lors de l'installation des modules."
    }
}

# Cas d'utilisation : Exécuter le script main.py
# Retour : true ou false (succès ou échec)
function launch_main_py {
    # Vérification de l'existence de main.py
    if (-not (Test-Path "./main.py")) {
        handle_error "main.py non trouvé dans le répertoire actuel."
    }

    # Vérification de l'existence de l'environnement virtuel
    if (-not (Test-Path "./venv")) {
        handle_error "L'environnement virtuel 'venv' n'existe pas. Veuillez le créer avant de lancer main.py."
    }

    # Exécution de main.py
    Write-Output "Exécution de main.py"
    & "./venv/Scripts/python.exe" "./main.py"
    if (-not $?) {
        handle_error "Problème lors du lancement de main.py (Code de sortie : $LASTEXITCODE)."
    }

    Write-Output "main.py exécuté avec succès."
}



# 1. S'assurer de la disponibilité de python
ensure_python

# 2. Création du VENV
create_venv

# 3. Installation des requirements
install_requirements

# 4. Lancement du script main.py
