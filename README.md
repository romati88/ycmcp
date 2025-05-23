# Yandex Cloud MCP Server

MCP server для комплексного управления ресурсами Yandex Cloud. Предоставляет функционал для просмотра и анализа виртуальных машин, сетевых ресурсов, дисков и снапшотов.

## Архитектура

Проект имеет модульную архитектуру для улучшенной поддерживаемости:

```
src/yandex_cloud_mcp/
├── server.py          # Основной MCP сервер и определения инструментов
├── credentials.py     # Управление учетными данными
├── compute.py         # Операции с виртуальными машинами
├── network.py         # Работа с сетевыми ресурсами
├── storage.py         # Управление дисками и снапшотами
└── config.py          # Константы конфигурации
```

## Функции

### 🔐 Управление учетными данными
- `setup_credentials(iam_token, folder_id)` - настройка учетных данных для сессии
- `get_credentials_status()` - проверка статуса настроенных учетных данных  
- `clear_credentials()` - очистка сохраненных учетных данных

### 💻 Виртуальные машины
- `list_vms(folder_id)` - получение списка всех ВМ в указанной папке
- `get_vm_config(instance_id)` - получение детальной конфигурации конкретной ВМ

### 🌐 Сетевые ресурсы
- `list_networks(folder_id)` - получение списка всех сетей
- `list_subnets(folder_id)` - получение списка всех подсетей
- `list_security_groups(folder_id)` - получение списка групп безопасности
- `get_security_group_config(security_group_id)` - детальная конфигурация группы безопасности с правилами

### 💾 Диски и снапшоты
- `list_disks(folder_id)` - получение списка всех дисков
- `get_disk_config(disk_id)` - детальная конфигурация диска
- `list_snapshots(folder_id)` - получение списка всех снапшотов
- `get_snapshot_config(snapshot_id)` - детальная конфигурация снапшота

## Особенности

✅ **Комплексное управление** - ВМ, сети, диски, снапшоты, группы безопасности  
✅ **Безопасность** - валидация входных данных, логирование операций  
✅ **Удобство** - автоматическое использование сохраненных учетных данных  
✅ **Надежность** - обработка ошибок и подробные сообщения  
✅ **Гибкость** - поддержка переменных окружения и интерактивной настройки  
✅ **Контейнеризация** - запуск через Podman/Docker для изоляции

## Установка и настройка

### Вариант 1: Запуск через uv (рекомендуется для разработки)

#### 1. Установка зависимостей

С помощью uv:
```bash
uv sync
```

С помощью pip:
```bash
pip install fastmcp yandexcloud grpcio grpcio-status
```

#### 2. Настройка аутентификации

Получите IAM токен и установите переменные окружения:
```bash
export YC_TOKEN="your_iam_token_here"
export YC_FOLDER_ID="your_folder_id_here"
```

Для получения IAM токена можно использовать CLI:
```bash
yc iam create-token
```

Для получения folder_id:
```bash
yc config list
```

#### 3. Запуск сервера

```bash
uv run mcp_server.py
```

или 

```bash
python mcp_server.py
```

или напрямую из src:

```bash
uv run src/yandex_cloud_mcp/server.py
```

### Вариант 2: Запуск через Podman (рекомендуется для продакшена)

#### 1. Сборка образа

```bash
podman build -t yandex-cloud-mcp .
```

#### 2. Запуск контейнера

```bash
podman run -i --rm \
  -e YC_TOKEN="your_iam_token_here" \
  -e YC_FOLDER_ID="your_folder_id_here" \
  yandex-cloud-mcp
```

## Подключение к Claude AI Desktop

### 1. Найдите конфигурационный файл Claude

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

### 2. Добавьте конфигурацию MCP сервера

Откройте файл `claude_desktop_config.json` и добавьте одну из конфигураций:

#### Вариант A: Запуск через uv (для разработки)

Сначала установите переменные окружения в системе:
```bash
export YC_TOKEN="your_iam_token_here"
export YC_FOLDER_ID="your_folder_id_here"
```

Затем добавьте конфигурацию:
```json
{
  "mcpServers": {
    "yandex-cloud": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/your/project", "mcp_server.py"]
    }
  }
}
```

#### Вариант B: Запуск через Podman (рекомендуется)

```bash
podman build -t yandex-cloud-mcp .
```

Добавьте конфигурацию:
```json
{
  "mcpServers": {
    "yandex-cloud": {
      "command": "podman",
      "args": [
        "run", "-i", "--rm",
        "yandex-cloud-mcp"
      ]
    }
  }
}
```

### 3. Перезапустите Claude Desktop

После изменения конфигурации перезапустите Claude Desktop App.

## Использование

После подключения к Claude AI выполните следующие шаги:

### 1. Настройка учетных данных (при первом использовании)

```
Настрой учетные данные для Yandex Cloud: IAM токен t1.xxx... и folder ID b1gxxx...
```

### 2. Проверка статуса (опционально)

```
Проверь статус учетных данных
```

### 3. Работа с ресурсами

#### 💻 Виртуальные машины
```
Покажи список всех виртуальных машин
Покажи детальную конфигурацию ВМ fhm1234567890abcdef
```

#### 🌐 Сетевые ресурсы
```
Покажи список всех сетей
Покажи список всех подсетей
Покажи список групп безопасности
Покажи конфигурацию группы безопасности enpabcd1234567890
```

#### 💾 Диски и снапшоты
```
Покажи список всех дисков
Покажи конфигурацию диска fhm0987654321fedcba
Покажи список всех снапшотов
Покажи конфигурацию снапшота fd81234567890abcdef
```

## Получение учетных данных

### IAM токен

Для получения IAM токена используйте один из способов:

1. **Через Yandex CLI:**
   ```bash
   yc iam create-token
   ```

2. **Через консоль Yandex Cloud:**
   - Перейдите в [IAM](https://console.cloud.yandex.ru/iam)
   - Создайте новый токен

### Folder ID

Чтобы узнать ID папки в Yandex Cloud:

1. **Через Yandex CLI:**
   ```bash
   yc config list
   ```

2. **Через консоль:**
   - Откройте Yandex Cloud Console
   - Выберите нужную папку
   - ID папки отображается в URL: `https://console.cloud.yandex.ru/folders/YOUR_FOLDER_ID`

## Тестирование

### Локальное тестирование

```bash
cd /path/to/project
export YC_TOKEN="your_token"
export YC_FOLDER_ID="your_folder_id"
uv run test_server.py
```

### Тестирование модулей

```bash
# Тестирование функций вычислений
python -c "from src.yandex_cloud_mcp.compute import list_vms; print('Compute module loaded successfully')"

# Тестирование функций сети  
python -c "from src.yandex_cloud_mcp.network import list_networks; print('Network module loaded successfully')"

# Тестирование функций хранилища
python -c "from src.yandex_cloud_mcp.storage import list_disks; print('Storage module loaded successfully')"
```

### Тестирование Podman образа

```bash
podman build -t yandex-cloud-mcp .
podman run -i --rm \
  -e YC_TOKEN="your_token" \
  -e YC_FOLDER_ID="your_folder_id" \
  yandex-cloud-mcp
```

## Безопасность

- IAM токен хранится в переменной окружения
- Сервер предоставляет только доступ на чтение к информации о ВМ
- Никаких операций изменения или удаления не поддерживается
- Podman контейнер запускается под непривилегированным пользователем
- Регулярно обновляйте IAM токены (рекомендуется каждые 12 часов)