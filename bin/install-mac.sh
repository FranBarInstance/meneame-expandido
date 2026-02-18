#!/usr/bin/env sh
set -eu

REPO_OWNER="FranBarInstance"
REPO_NAME="meneame-expandido"
REPO_SLUG="${REPO_OWNER}/${REPO_NAME}"
API_TAGS_URL="https://api.github.com/repos/${REPO_SLUG}/tags?per_page=1"

tty_available() {
  [ -r /dev/tty ] && [ -w /dev/tty ]
}

say() {
  printf "%s\n" "$*"
}

warn() {
  printf "WARN: %s\n" "$*" >&2
}

die() {
  printf "ERROR: %s\n" "$*" >&2
  exit 1
}

prompt() {
  message="$1"
  default="${2-}"

  if tty_available; then
    if [ -n "$default" ]; then
      printf "%s [%s]: " "$message" "$default" > /dev/tty
    else
      printf "%s: " "$message" > /dev/tty
    fi
    IFS= read -r answer < /dev/tty || answer=""
  else
    answer=""
  fi

  if [ -z "$answer" ]; then
    printf "%s" "$default"
  else
    printf "%s" "$answer"
  fi
}

prompt_yes_no() {
  message="$1"
  default="${2-y}"

  answer="$(prompt "$message (y/n)" "$default")"
  case "$answer" in
    y|Y|yes|YES) return 0 ;;
    n|N|no|NO) return 1 ;;
    *)
      warn "Respuesta no válida, se usa '$default'."
      [ "$default" = "y" ] || [ "$default" = "Y" ]
      return
      ;;
  esac
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "Falta comando requerido: $1"
}

resolve_latest_tag() {
  tag="$(
    curl -fsSL "$API_TAGS_URL" 2>/dev/null \
    | sed -n 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
    | head -n 1
  )"
  [ -n "$tag" ] || return 1
  printf "%s" "$tag"
}

generate_secret_key() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -hex 32
    return 0
  fi

  if command -v python3 >/dev/null 2>&1; then
    python3 -c "import secrets; print(secrets.token_hex(32))"
    return 0
  fi

  if [ -r /dev/urandom ] && command -v od >/dev/null 2>&1; then
    od -An -N32 -tx1 /dev/urandom | tr -d ' \n'
    return 0
  fi

  return 1
}

detect_python() {
  if command -v python3 >/dev/null 2>&1; then
    printf "python3"
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    printf "python"
    return 0
  fi

  return 1
}

extract_env_value() {
  file="$1"
  key="$2"
  value="$(sed -n "s/^${key}=//p" "$file" | head -n 1)"
  printf "%s" "$value"
}

install_from_tag() {
  target_dir="$1"
  tag="$2"

  tmp_dir="$(mktemp -d)"
  archive="${tmp_dir}/source.tar.gz"
  extracted_root="${tmp_dir}/${REPO_NAME}-${tag}"
  archive_url="https://github.com/${REPO_SLUG}/archive/refs/tags/${tag}.tar.gz"

  say "Descargando ${REPO_SLUG} tag ${tag}..."
  curl -fsSL "$archive_url" -o "$archive"

  mkdir -p "$target_dir"
  tar -xzf "$archive" -C "$tmp_dir"

  if [ -d "$extracted_root" ]; then
    (cd "$extracted_root" && tar -cf - .) | (cd "$target_dir" && tar -xf -)
  else
    die "No se encontró carpeta extraída esperada: $extracted_root"
  fi

  rm -rf "$tmp_dir"
}

main() {
  require_cmd curl
  require_cmd tar
  require_cmd sed
  require_cmd awk
  require_cmd mktemp
  tty_available || die "Este instalador requiere terminal interactiva (TTY)."

  if [ "$(uname -s)" != "Darwin" ]; then
    warn "Este script está orientado a macOS. En Linux usa bin/install.sh."
  fi

  latest_tag="$(resolve_latest_tag)" || die "No se pudo resolver el último tag del repositorio."
  say "Último tag detectado: ${latest_tag}"

  cwd="$(pwd)"
  use_current="n"
  if prompt_yes_no "¿Instalar en el directorio actual (${cwd})?" "n"; then
    use_current="y"
  fi

  if [ "$use_current" = "y" ]; then
    install_dir="$cwd"
  else
    install_dir_default="${cwd}/${REPO_NAME}"
    install_dir="$(prompt "Directorio de instalación" "$install_dir_default")"
  fi

  [ -n "$install_dir" ] || die "El directorio de instalación no puede estar vacío."
  mkdir -p "$install_dir"
  if [ -n "$(ls -A "$install_dir" 2>/dev/null)" ]; then
    if ! prompt_yes_no "El directorio ${install_dir} no está vacío. ¿Continuar y sobrescribir archivos?" "n"; then
      die "Instalación cancelada por el usuario."
    fi
  fi

  install_from_tag "$install_dir" "$latest_tag"
  say "Código instalado en: $install_dir"

  python_cmd="$(detect_python)" || die "No se encontró Python (python3/python)."
  say "Python detectado: ${python_cmd}"

  (
    cd "$install_dir"
    "$python_cmd" -m venv .venv
    # shellcheck disable=SC1091
    . .venv/bin/activate
    pip install -r requirements.txt

    if [ ! -f config/.env ]; then
      cp config/.env.example config/.env
    fi

    secret_key="$(generate_secret_key)" || die "No se pudo generar SECRET_KEY."
    sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=${secret_key}/" config/.env
    rm -f config/.env.bak

    say "Configuración base lista en config/.env"

    user_name="$(prompt "Nombre del usuario" "Admin")"
    user_email="$(prompt "Email del usuario" "email@example.com")"
    while [ -z "$user_email" ]; do
      warn "El email no puede estar vacío."
      user_email="$(prompt "Email del usuario" "email@example.com")"
    done
    user_password="$(prompt "Password del usuario" "")"
    while [ -z "$user_password" ] || [ "${#user_password}" -lt 8 ]; do
      warn "La contraseña debe tener al menos 8 caracteres."
      user_password="$(prompt "Password del usuario" "")"
    done
    user_birthdate="$(prompt "Fecha de nacimiento ISO (YYYY-MM-DD)" "1990-01-01")"
    user_locale="$(prompt "Locale del usuario" "es")"
    user_region="$(prompt "Región del usuario (opcional)" "")"

    python bin/create_user.py \
      "$user_name" \
      "$user_email" \
      "$user_password" \
      "$user_birthdate" \
      --locale "$user_locale" \
      --region "$user_region"

    app_ip="$(extract_env_value config/.env APP_BIND_IP)"
    app_port="$(extract_env_value config/.env APP_BIND_PORT)"
    [ -n "$app_ip" ] || app_ip="localhost"
    [ -n "$app_port" ] || app_port="55000"
    app_url="http://${app_ip}:${app_port}"

    say ""
    say "Instalación completada."
    say "Aplicación disponible en: ${app_url}"
    say "Directorio: ${install_dir}"

    if prompt_yes_no "¿Quieres ejecutar la aplicación ahora?" "y"; then
      say "Ejecutando app en ${app_url} ..."
      python src/run.py
    else
      say "Para arrancar después:"
      say "cd \"${install_dir}\" && . .venv/bin/activate && python src/run.py"
    fi
  )
}

main "$@"
