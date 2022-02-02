#!/bin/bash

# Check if running as root. If it's not, add sudo preffix to all commands.
if [ "$EUID" -ne 0 ]; then
    PREFFIX="sudo"
    echo "Você não está em root. Os comandos que exigirem privilégios terão o prefixo 'sudo' adicionado a eles."
fi

# Check for machine system.
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    *)          machine="UNKNOWN:${unameOut}"
esac

# Check for machine architecture.
unameOut="$(uname -m)"
case "${unameOut}" in
    x86_64*)    arch=x86_64;;
    i*86*)      arch=x86;;
    *)          arch="UNKNOWN:${unameOut}"
esac

# Function that will build the binaries for datario.
function build_datario {

    # Check if python3 is available using the `which` command.
    if [ ! -x "$(which python3)" ]; then
        echo "Python 3.x não está instalado. Instale-o e execute este script novamente."
        exit 1
    fi

    # Check if pip3 is available using the `which` command.
    if [ ! -x "$(which pip3)" ]; then
        echo "Pip para Python 3.x não está instalado. Instale-o e execute este script novamente."
        exit 1
    fi

    # Check if git is available using the `which` command.
    if [ ! -x "$(which git)" ]; then
        echo "Git não está instalado. Instale-o e execute este script novamente."
        exit 1
    fi

    # Install virtualenv.
    python3 -m pip install virtualenv

    # Create temporary virtual environment for building binaries.
    python3 -m virtualenv -p python3 /tmp/venv

    # Clone datario-cli repository.
    git clone https://git.apps.rio.gov.br/escritorio-dados/escritorio-dados/datario-cli /tmp/datario-cli

    # Install dependencies
    cd /tmp/datario-cli/ && /tmp/venv/bin/pip install --no-cache-dir .

    # Build using pyinstaller
    cd /tmp/datario-cli/ && /tmp/venv/bin/pyinstaller --onefile --clean --windowed datario_cli/cli.py

    # Ensure it works (fails if command fails)
    /tmp/datario-cli/dist/cli --help > /dev/null

    # Rename it for later and we're done.
    mv /tmp/datario-cli/dist/cli /tmp/datario
}


# If we're on Linux and the machine is 64-bit, we can simply download binaries.
if [ "$machine" = "Linux" ] && [ "$arch" = "x86_64" ]; then
    echo "Você está executando o script em um computador Linux 64-bit."
    echo "Baixando os binários do datario..."
    wget -q -O /tmp/datario https://git.apps.rio.gov.br/escritorio-dados/escritorio-dados/datario-cli/-/package_files/6/download

# If we're on:
# - Linux (another architecture) or
# - Mac (any architecture)
# we need to build binaries
elif [ "$machine" = "Linux" ] || [ "$machine" = "Mac" ]; then
    echo "Você está executando o script em um computador Linux (não x86_64) ou Mac."
    echo "Precisamos construir os binários do datario."
    build_datario

# Else, advertise that we don't know how to build binaries.
else
    echo "Você está executando o script em um $machine $arch."
    echo "Essa combinação não é suportada para o momento."
    echo "Caso seja uma demanda, contate o time do Escritório de Dados."
    exit 1
fi

# Now we've got our binaries located at /tmp/datario. Let's add execute permissions.
chmod +x /tmp/datario

# Finally, we can copy it to the correct location.
if [ -d "/usr/local/bin" ]; then
    echo "Copiando o binário para /usr/local/bin..."
    $PREFFIX cp /tmp/datario /usr/local/bin/datario
else
    echo "Copiando o binário para /usr/bin..."
    $PREFFIX cp /tmp/datario /usr/bin/datario
fi