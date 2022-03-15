#!/bin/bash

# Script parameters
MIN_PYTHON_VERSION="39" # Python 3.9
MAX_PYTHON_VERSION="311" # Python 3.11

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

# Function for handling errors.
function exit_if_error() {
    local exit_code=$1
    shift
    [[ $exit_code]] &&
        ((exit_code != 0)) && {
            printf 'ERROR: %s\n' "$@" >&2
            exit "$exit_code"
        }
}

# Function that will build the binaries for datario.
function build_datario {

    # Check if python3 is available using the `which` command.
    python3_path=$(which python3)
    exit_if_error $? "Python 3.x não encontrado. Verifique se o comando `python3` está disponível."

    # Check if pip3 is available using the `which` command.
    pip3_path=$(which pip3)
    exit_if_error $? "Pip 3.x não encontrado. Verifique se o comando `pip3` está disponível."

    # Check if git is available using the `which` command.
    git_path=$(which git)
    exit_if_error $? "Git não encontrado. Verifique se o comando `git` está disponível."

    # Python version must be >= MIN_PYTHON_VERSION and < MAX_PYTHON_VERSION.
    python_version=$(python3 -c 'import sys; print("".join(map(str, sys.version_info[:2])));')
    exit_if_error $? "Erro ao verificar versão do Python."
    if [[ $python_version -lt $MIN_PYTHON_VERSION ]] || [[ $python_version -ge $MAX_PYTHON_VERSION ]]; then
        echo "Versão do Python inválida. Versão deve ser >= $MIN_PYTHON_VERSION e < $MAX_PYTHON_VERSION."
        exit 1
    fi

    # Install virtualenv.
    python3 -m pip install virtualenv
    exit_if_error $? "Erro ao instalar virtualenv."

    # Create temporary virtual environment for building binaries.
    python3 -m virtualenv -p python3 /tmp/venv
    exit_if_error $? "Erro ao criar virtualenv."

    # Clone datario-cli repository.
    git clone https://git.apps.rio.gov.br/escritorio-dados/escritorio-dados/datario-cli /tmp/datario-cli
    exit_if_error $? "Erro ao clonar o repositório do datario-cli."

    # Install dependencies
    cd /tmp/datario-cli/ && /tmp/venv/bin/pip install --no-cache-dir .
    exit_if_error $? "Erro ao instalar dependências da CLI."

    # Build using pyinstaller
    cd /tmp/datario-cli/ && /tmp/venv/bin/pyinstaller --onefile --clean --windowed datario_cli/cli.py
    exit_if_error $? "Erro ao compilar a CLI."

    # Ensure it works (fails if command fails)
    /tmp/datario-cli/dist/cli --help > /dev/null
    exit_if_error $? "Erro ao executar a CLI."

    # Rename it for later and we're done.
    mv /tmp/datario-cli/dist/cli /tmp/datario
    exit_if_error $? "Erro ao renomear o binário."
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
    echo "Você está executando o script em um computador Mac ou Linux (não x86_64)."
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
exit_if_error $? "Erro ao adicionar permissões de execução ao binário."

# Finally, we can copy it to the correct location.
if [ -d "/usr/local/bin" ]; then
    echo "Copiando o binário para /usr/local/bin..."
    $PREFFIX cp /tmp/datario /usr/local/bin/datario
else
    echo "Copiando o binário para /usr/bin..."
    $PREFFIX cp /tmp/datario /usr/bin/datario
fi