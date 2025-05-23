# Yandex Cloud MCP Server

🚀 **MCP сервер** для управления ресурсами Yandex Cloud с поддержкой **cloud/organization уровня** и **автоматическим определением scope**.

Предоставляет полный функционал только для чтения (read-only API) всех ресурсов Yandex Cloud: VMs, сети, диски, образы, зоны доступности, IP адреса и многое другое.

## Возможности

📚 **Полное покрытие API** - все операции чтения Compute, VPC и Disks/Snapshots  
🏗️ **Многоуровневый доступ** - folder/cloud/organization уровни  
🧠 **Умная навигация** - автоматическое определение scope и подсказки  
🔐 **Гибкая аутентификация** - через переменные окружения или интерактивно в Claude  

## Установка и настройка

### Вариант 1: Запуск через uv (для разработки)

```bash
# Установка зависимостей
uv sync

# Настройка аутентификации
export YC_TOKEN="your_iam_token_here"
export YC_FOLDER_ID="your_folder_id_here"

# Запуск сервера
uv run mcp_server.py
```

### Вариант 2: Запуск через Podman (для продакшена)

```bash
# Сборка образа
podman build -t yandex-cloud-mcp .

# Запуск контейнера
podman run -i --rm \
  -e YC_TOKEN="your_iam_token_here" \
  -e YC_FOLDER_ID="your_folder_id_here" \
  yandex-cloud-mcp
```

## Подключение к Claude AI Desktop

Добавьте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "yandex-cloud": {
      "command": "podman",
      "args": [
        "run", "-i", "--rm",
        "-e", "YC_TOKEN=your_token",
        "-e", "YC_FOLDER_ID=your_folder",
        "yandex-cloud-mcp"
      ]
    }
  }
}
```

## Использование

```
# Настройка учетных данных (опционально - можно в переменных окружения)
Настрой учетные данные для Yandex Cloud: IAM токен t1.xxx... и folder ID b1gxxx...

# Основные операции
Покажи список всех виртуальных машин
Покажи все сети и подсети
Покажи контекст организации со всеми облаками
Посоветуй scope для запроса дисков
```

## Получение учетных данных

**IAM токен:**
```bash
yc iam create-token
```

**Folder ID:**
```bash
yc config list
```

## Тестирование

```bash
export YC_TOKEN="your_token"
export YC_FOLDER_ID="your_folder_id"
uv run test_server.py
```

## Архитектура

```
src/yandex_cloud_mcp/
├── server.py          # Основной MCP сервер
├── credentials.py     # Управление учетными данными
├── compute.py         # ВМ, образы, зоны, типы дисков
├── network.py         # Сети, подсети, маршруты, IP, шлюзы
├── storage.py         # Диски и снапшоты
├── resource_manager.py # Cloud/Organization уровень
└── config.py          # Конфигурация
```

## Полный перечень функций

### 🔐 Управление учетными данными
- `setup_credentials(iam_token, folder_id)` - настройка учетных данных
- `get_credentials_status()` - проверка статуса учетных данных  
- `clear_credentials()` - очистка учетных данных

### 🏢 Cloud/Organization уровень
- `list_yandex_clouds(organization_id)` - список облаков в организации
- `get_cloud_details_info(cloud_id)` - детальная информация об облаке
- `list_yandex_folders(cloud_id)` - список папок (с автоопределением cloud_id)
- `get_folder_details_info(folder_id)` - детальная информация о папке
- `get_yandex_organization_context()` - полная иерархия организации
- `suggest_query_scope(resource_type)` - рекомендации по выбору scope

### 💻 Compute ресурсы
**Виртуальные машины:**
- `list_virtual_machines(folder_id)` - список ВМ
- `get_virtual_machine_config(instance_id)` - конфигурация ВМ

**Образы и инфраструктура:**
- `list_compute_images(folder_id)` - список образов
- `get_image_configuration(image_id)` - конфигурация образа
- `list_availability_zones()` - список зон доступности
- `get_zone_configuration(zone_id)` - конфигурация зоны
- `list_compute_disk_types(zone_id)` - типы дисков
- `get_disk_type_configuration(disk_type_id)` - конфигурация типа диска

### 🌐 VPC сетевые ресурсы
**Основные сети:**
- `list_vpc_networks(folder_id)` - список сетей
- `get_network_configuration(network_id)` - конфигурация сети
- `list_vpc_subnets(folder_id)` - список подсетей  
- `get_subnet_configuration(subnet_id)` - конфигурация подсети

**Безопасность и маршрутизация:**
- `list_vpc_security_groups(folder_id)` - список групп безопасности
- `get_security_group_details(security_group_id)` - конфигурация группы с правилами
- `list_vpc_route_tables(folder_id)` - список таблиц маршрутизации
- `get_route_table_configuration(route_table_id)` - конфигурация таблицы маршрутов

**IP адреса и шлюзы:**
- `list_vpc_addresses(folder_id)` - список статических IP адресов
- `get_address_configuration(address_id)` - конфигурация IP адреса
- `list_vpc_gateways(folder_id)` - список шлюзов
- `get_gateway_configuration(gateway_id)` - конфигурация шлюза

### 💾 Storage ресурсы
- `list_storage_disks(folder_id)` - список дисков
- `get_disk_details(disk_id)` - конфигурация диска
- `list_disk_snapshots(folder_id)` - список снапшотов
- `get_snapshot_details(snapshot_id)` - конфигурация снапшота